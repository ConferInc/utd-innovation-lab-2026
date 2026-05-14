"""Optional grounded LLM rewrite of template WhatsApp replies.

When ``main._llm_routing_available()`` is true (Gemini or Ollama configured, and
``DISABLE_LLM_ROUTING`` is not set), ``main`` always calls this module after
``build_response_with_facts``. If providers fail or return nothing, the template
draft is sent instead.
"""

from __future__ import annotations

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Mapping, Optional

from intent_classifier import _get_gemini_client
from response_builder import WHATSAPP_CHAR_LIMIT, _truncate_whatsapp

log = logging.getLogger(__name__)

_GEMINI_TIMEOUT_S = 10.0
_OLLAMA_TIMEOUT_S = 8.0
_OLLAMA_CLOUD_BASE = "https://ollama.com/v1"
_OLLAMA_DEFAULT_MODEL = "gemma3:4b"

_LIST_ROW_CAP = 8

_GROUNDED_SYSTEM_PROMPT = """You are the WhatsApp assistant for JKYog Radha Krishna Temple in Cedar Park, Texas.

You will receive the user's message and a JSON object called FACTS. The FACTS were built from the event API, recurring schedule data, or static temple information — nothing else.

Write ONE WhatsApp-ready reply in plain text. Match the user's question scope only (e.g. if they asked about parking, focus on parking; do not volunteer food, transport, or registration unless the question is broad or explicitly asks for multiple topics).

WhatsApp formatting (use where it helps readability — not on every word):
- Bold: wrap with single asterisks, like *this* (do not use **double** asterisks; WhatsApp does not treat those as bold).
- Italic: wrap with underscores, like _this_, for light emphasis (secondary detail, hints, or soft stress).
- Do not use markdown headings: no lines starting with #. No HTML.

Layout and structure (follow the shape of FACTS, not decorative style):
- Start with one short lead line, then use a blank line between sections when you have multiple sections.
- When FACTS contain several events, programs, or distinct logistics fields, use a numbered list for events or short flat bullets for grouped lines — you do not need the user to say "list" or "bullet points."
- For each listed event: put the event name and date/time on separate lines; use *bold* for the event title when listing multiple events.
- Cap long lists: at most about """ + str(_LIST_ROW_CAP) + """ top-level numbered rows or bullets; summarize or trim within FACTS rather than inventing. No nested bullet lists.
- When a single fact or a single event answers the question, short prose is fine — do not force bullets.

Hard rules:
- Use ONLY information present in FACTS. Do not add events, dates, times, prices, URLs, phone numbers, or logistics that are not in FACTS.
- You may copy or lightly paraphrase FACTS. Do not invent filler facts.
- If the user asks for something not present in FACTS, say so plainly. When a field would be unknown in the non-LLM bot, use this exact phrase when appropriate: Not listed on the event page
- Stay warm and concise. No JSON in the reply. Avoid decorative one-line-per-bullet spam when a short paragraph would read better."""

_MAX_OUT_GEMINI = 900
_MAX_OUT_OLLAMA = 900


def grounded_reply_providers_configured() -> bool:
    """Same capability gate as conversational replies (Gemini or Ollama Cloud)."""
    from conversational_reply import conversational_providers_configured

    return conversational_providers_configured()


def _rewrite_char_cap() -> int:
    raw = (os.getenv("LLM_REWRITE_MAX_CHARS") or "").strip()
    if raw.isdigit():
        n = int(raw)
        return max(256, min(n, WHATSAPP_CHAR_LIMIT))
    return WHATSAPP_CHAR_LIMIT


def _facts_json_block(facts: Mapping[str, Any]) -> str:
    try:
        return json.dumps(dict(facts), ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return "{}"


_EVENT_LABEL_KEYS: tuple[tuple[str, str], ...] = (
    ("name", "event title in *bold*"),
    ("start_datetime", "*When:* (combine start/end and timezone from FACTS on one or two lines)"),
    ("location_name", "*Where:*"),
    ("address", "*Where:*"),
    ("city", "*Where:*"),
    ("state", "*Where:*"),
    ("price", "*Price:*"),
    ("food_info", "*Food:*"),
    ("parking_notes", "*Parking:*"),
    ("transportation_notes", "*Travel / transport:*"),
    ("registration_status", "*Registration:*"),
    ("registration_required", "*Registration:*"),
    ("registration_url", "*Registration:*"),
    ("contact_email", "*Contact:*"),
    ("contact_phone", "*Contact:*"),
    ("source_url", "link line (use URL from FACTS only)"),
    ("sponsorship_tiers", "*Sponsorship:* (tiers exactly as in FACTS)"),
)


def _truthy_fact_value(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def _formatting_guidance(facts: Mapping[str, Any]) -> str:
    """Deterministic layout hints from envelope + data (not new facts)."""
    rk = str(facts.get("response_kind") or "").strip() or "unknown"
    raw_data = facts.get("data")
    data: dict[str, Any] = raw_data if isinstance(raw_data, dict) else {}

    lines: list[str] = [
        "Formatting (instructions only — do not treat as new facts; all values must still come from FACTS):",
        f"- response_kind is {rk!r}.",
    ]

    if rk == "event_list":
        events = data.get("events")
        n = len(events) if isinstance(events, list) else 0
        lines.append(f"- FACTS include {n} event row(s) in data.events.")
        if n == 0:
            lines.append("- Use 1–2 short sentences; no fake event list.")
        elif n == 1:
            lines.append(
                "- One event: concise prose or a tiny block; *bold* for the event name; "
                "date/time and place on their own lines if you show them."
            )
        else:
            lines.append(
                f"- Multiple events: use a numbered list (1–{min(n, _LIST_ROW_CAP)} at most). "
                "Each item: *bold* title line, then date/time on the next line, then location on the next. "
                "Do not nest bullets."
            )
        if n > _LIST_ROW_CAP:
            lines.append(
                f"- More than {_LIST_ROW_CAP} events appear in FACTS: show the first {_LIST_ROW_CAP} "
                "in full list form, then briefly note there are more (no invented names)."
            )
        return "\n".join(lines)

    if rk == "no_results":
        lines.append("- No matching events: one or two short friendly sentences; no bullet list of events.")
        return "\n".join(lines)

    if rk == "temple_static":
        lines.append(
            "- Static temple info: mirror sections from data.temple with *bold* section titles "
            "(e.g. *Address*, *Contact*) and blank lines between sections; keep the same field order "
            "as in FACTS; do not invent fields."
        )
        return "\n".join(lines)

    if rk in {"logistics_event", "single_event", "sponsorship_event"}:
        event = data.get("event")
        if isinstance(event, dict):
            hints: list[str] = []
            for key, hint in _EVENT_LABEL_KEYS:
                if key in event and _truthy_fact_value(event.get(key)):
                    hints.append(hint)
            if hints:
                uniq: list[str] = []
                for h in hints:
                    if h not in uniq:
                        uniq.append(h)
                cap = 12
                shown = uniq[:cap]
                tail = f" … (+{len(uniq) - cap} more label types)" if len(uniq) > cap else ""
                lines.append(
                    "- Single-event payload: use short prose or labeled lines; include *bold* labels only "
                    f"for fields that exist in FACTS, e.g. {', '.join(shown)}{tail}."
                )
            else:
                lines.append("- Event payload has no filled fields in FACTS: keep the reply very short.")
        else:
            lines.append("- Use *bold* sparingly for scanability; stay within FACTS.")
        if rk == "sponsorship_event":
            lines.append(
                "- Sponsorship: describe only tiers/options present in FACTS; no invented prices or levels."
            )
        return "\n".join(lines)

    if rk == "recurring_schedule":
        lines.append(
            "- Recurring schedule: if data.live_now or data.upcoming_within_2h has entries, "
            "use a short flat list or clearly labeled lines (*Now:* / *Coming up:*); "
            "preserve program names and times from FACTS only."
        )
        if data.get("next_occurrence"):
            lines.append(
                "- If data.next_occurrence is set, mention it in a compact labeled line (*Next:* …)."
            )
        return "\n".join(lines)

    if rk == "sponsorship":
        ways = data.get("ways_to_contribute")
        nw = len(ways) if isinstance(ways, list) else 0
        if nw > 0:
            cap_w = min(nw, _LIST_ROW_CAP)
            lines.append(
                f"- General sponsorship: at most {cap_w} short flat bullets from ways_to_contribute "
                "in FACTS only; *bold* optional on the first word of each line; no invented tiers."
            )
        else:
            lines.append(
                "- General sponsorship: short prose from FACTS (e.g. note, ways_to_contribute); "
                "no invented tiers."
            )
        return "\n".join(lines)

    if rk in {"api_client_error", "generic_error"}:
        lines.append(
            "- System/API issue: brief empathetic prose (one short paragraph); "
            "no decorative bullet lists or fake recovery steps."
        )
        return "\n".join(lines)

    lines.append(
        "- Follow the structure of FACTS; use *bold* / _italic_ only where they aid scanning; "
        "no nested bullet lists."
    )
    return "\n".join(lines)


def _format_grounded_user_block(
    user_message: str, intent: str, confidence: Any, facts: Mapping[str, Any]
) -> str:
    try:
        conf_f = float(confidence)
    except (TypeError, ValueError):
        conf_f = 0.0
    guidance = _formatting_guidance(facts)
    return (
        f"What the user wrote:\n{user_message.strip()}\n\n"
        f"Classifier intent: {intent} (confidence {conf_f:.2f})\n\n"
        f"FACTS (JSON — sole source of truth):\n{_facts_json_block(facts)}\n\n"
        f"{guidance}"
    )


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:].lstrip()
    return t.strip()


def _sanitize_grounded(text: str) -> str:
    if not text:
        return ""
    lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    cap = _rewrite_char_cap()
    return _truncate_whatsapp(body, limit=cap)


def _rewrite_model_gemini() -> str:
    return (
        os.getenv("GEMINI_MODEL_REWRITE")
        or os.getenv("GEMINI_MODEL_REPLY")
        or "gemini-2.5-flash-lite"
    )


def _grounded_gemini(user_message: str, intent: str, confidence: Any, facts: Mapping[str, Any]) -> Optional[str]:
    client = _get_gemini_client()
    if client is None:
        return None
    try:
        from google.genai import types as genai_types
    except ImportError:
        return None

    user_block = _format_grounded_user_block(user_message, intent, confidence, facts)

    def _call():
        return client.models.generate_content(
            model=_rewrite_model_gemini(),
            contents=user_block,
            config=genai_types.GenerateContentConfig(
                system_instruction=_GROUNDED_SYSTEM_PROMPT,
                temperature=0.35,
                max_output_tokens=_MAX_OUT_GEMINI,
            ),
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(_call)
            response = fut.result(timeout=_GEMINI_TIMEOUT_S)
    except FuturesTimeout:
        log.debug("Gemini grounded rewrite timed out after %ss", _GEMINI_TIMEOUT_S)
        return None
    except Exception as exc:
        log.debug("Gemini grounded rewrite failed: %s", exc)
        return None

    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        return None
    return _strip_code_fences(raw)


def _grounded_ollama_cloud(
    user_message: str, intent: str, confidence: Any, facts: Mapping[str, Any]
) -> Optional[str]:
    api_key = (
        os.getenv("OLLAMA_CLOUD_API_KEY")
        or os.getenv("OLLAMA_API_KEY")
        or os.getenv("ZAI_API_KEY")
    )
    if not api_key:
        return None

    base = (os.getenv("OLLAMA_CLOUD_BASE_URL") or _OLLAMA_CLOUD_BASE).rstrip("/")
    model = os.getenv("OLLAMA_CLOUD_MODEL") or _OLLAMA_DEFAULT_MODEL
    url = f"{base}/chat/completions"
    user_block = _format_grounded_user_block(user_message, intent, confidence, facts)
    payload = {
        "model": model,
        "temperature": 0.35,
        "max_tokens": _MAX_OUT_OLLAMA,
        "messages": [
            {"role": "system", "content": _GROUNDED_SYSTEM_PROMPT},
            {"role": "user", "content": user_block},
        ],
    }

    try:
        import httpx

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=_OLLAMA_TIMEOUT_S) as http:
            resp = http.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            log.debug("Ollama grounded rewrite HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        content = _strip_code_fences(content)
        return content if content else None
    except Exception as exc:
        log.debug("Ollama grounded rewrite failed: %s", exc)
        return None


def build_grounded_whatsapp_reply(
    user_message: str,
    intent: str,
    confidence: Any,
    facts: Mapping[str, Any],
) -> Optional[str]:
    """Return rewritten plain text, or ``None`` so the caller sends the template draft."""
    for fn in (_grounded_gemini, _grounded_ollama_cloud):
        raw = fn(user_message, intent, confidence, facts)
        if not raw:
            continue
        cleaned = _sanitize_grounded(raw)
        if cleaned:
            return cleaned
    return None
