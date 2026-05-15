"""Optional LLM-authored clarification replies (Phase 3).

When ``main._llm_routing_available()`` is true (Gemini or Ollama configured, and
``DISABLE_LLM_ROUTING`` is not set), ``main`` calls this module for
``clarification_needed`` / ``ambiguous`` / ``unknown`` intents before falling
back to the static clarification text.
"""

from __future__ import annotations

import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Optional

from intent_classifier import _get_gemini_client

log = logging.getLogger(__name__)

_MAX_REPLY_CHARS = 700
_GEMINI_TIMEOUT_S = 10.0
_OLLAMA_TIMEOUT_S = 8.0
_OLLAMA_CLOUD_BASE = "https://ollama.com/v1"
_OLLAMA_DEFAULT_MODEL = "gemma3:4b"

_REPLY_SYSTEM_PROMPT = """You are the WhatsApp helper for Radha Krishna Temple of Dallas in Allen, Texas.

The user's message was hard to route. Write ONE short, friendly reply for WhatsApp in plain text — no JSON.

If they only said hello, hi, namaste, good morning, or similar (no specific question yet), open with a brief warm greeting that matches their tone, then invite them to ask about events, the recurring schedule, logistics for a program, or donations — without dumping a list of event names.

Focus on what the user actually wrote. Any intent label or "Internal route" metadata in the message block is only for routing — do not answer as if that label were the user's question.

WhatsApp formatting (use only where it improves scanability; do not decorate every word):
- Bold: single asterisks, like *this* (do not use **double** asterisks; WhatsApp does not treat those as bold).
- Italic: underscores, like _this_, for light emphasis on a phrase or hint.
- No markdown headings (no lines starting with #). No HTML.

Layout:
- Default to one or two short paragraphs. If example questions help disambiguate, use at most 2–3 flat bullets or short lines — no nested bullet lists, no long catalogs.
- A blank line between two short paragraphs is fine when you have two distinct beats (e.g. acknowledge, then ask).

Rules:
- Do not invent event names, times, parking details, or prices. If you mention events or logistics, keep it generic ("upcoming events on the calendar") or refer only to facts in the context block.
- Do not give personal spiritual counseling; gently point to temple programs, the website, or visiting in person.
- Vary your opening across replies (examples: acknowledge briefly, ask a focused question, offer 2–3 example topics) — do not reuse the same opening every time.
- Optional: at most one warm sign-off phrase per reply (e.g. "Radhe Radhe" or similar); often skip it so replies do not sound repetitive.
- Stay under about 500 words; the system will hard-truncate at 700 characters.

Your job is tone and guidance only — not factual event data from APIs."""


def conversational_providers_configured() -> bool:
    """True if Gemini client or Ollama Cloud auth is available for reply generation."""
    if _get_gemini_client() is not None:
        return True
    return bool(
        os.getenv("OLLAMA_CLOUD_API_KEY")
        or os.getenv("OLLAMA_API_KEY")
        or os.getenv("ZAI_API_KEY")
    )


def build_clarification_context_block() -> str:
    """Compact temple facts for the reply model (not the full WhatsApp temple block)."""
    return (
        "Temple: Radha Krishna Temple of Dallas, Allen, TX. "
        "Address: 1450 N. Watters Road, Allen, TX 75013. "
        "Phone/WhatsApp: +1 (469) 444-7173. Website: jkyog.org; donations: jkyog.org/donate. "
        "The bot can help with: upcoming events, recurring schedule (e.g. Sunday Satsang), "
        "logistics for a named event, and donations/seva."
    )


_CLARIFICATION_FORMATTING_BLOCK = """Formatting (instructions only — not new facts; do not invent beyond the reference block above):
- Clarification turn: prose-first (one or two short paragraphs). Optional: at most 2–3 flat example questions if that genuinely helps routing.
- You may use *bold* or _italic_ sparingly for labels or emphasis; no nested bullets; no # headings."""


def _format_user_block(user_message: str, intent: str, confidence: Any, context_block: str) -> str:
    try:
        conf_f = float(confidence)
    except (TypeError, ValueError):
        conf_f = 0.0
    route_line = (
        f"Internal route (metadata only — not the user's question): {intent!r}, confidence {conf_f:.2f}."
    )
    return (
        "Your reply must directly respond to what the user wrote below.\n\n"
        f"What the user wrote:\n{user_message.strip()}\n\n"
        f"Reference facts (do not invent beyond these):\n{context_block.strip()}\n\n"
        f"{route_line}\n\n"
        f"{_CLARIFICATION_FORMATTING_BLOCK}"
    )


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:].lstrip()
    return t.strip()


def _sanitize_reply(text: str) -> str:
    if not text:
        return ""
    lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    if len(body) <= _MAX_REPLY_CHARS:
        return body
    cut = _MAX_REPLY_CHARS - 3
    if cut < 1:
        return "…"[:_MAX_REPLY_CHARS]
    trimmed = body[:cut].rstrip()
    return f"{trimmed}..."


def _reply_with_gemini(user_message: str, intent: str, confidence: Any, context_block: str) -> Optional[str]:
    client = _get_gemini_client()
    if client is None:
        return None
    try:
        from google.genai import types as genai_types
    except ImportError:
        return None

    model = os.getenv("GEMINI_MODEL_REPLY", "gemini-2.5-flash-lite")
    user_block = _format_user_block(user_message, intent, confidence, context_block)

    def _call():
        return client.models.generate_content(
            model=model,
            contents=user_block,
            config=genai_types.GenerateContentConfig(
                system_instruction=_REPLY_SYSTEM_PROMPT,
                temperature=0.65,
                max_output_tokens=320,
            ),
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(_call)
            response = fut.result(timeout=_GEMINI_TIMEOUT_S)
    except FuturesTimeout:
        log.debug("Gemini conversational reply timed out after %ss", _GEMINI_TIMEOUT_S)
        return None
    except Exception as exc:
        log.debug("Gemini conversational reply failed: %s", exc)
        return None

    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        return None
    return _strip_code_fences(raw)


def _reply_with_ollama_cloud(
    user_message: str, intent: str, confidence: Any, context_block: str
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
    user_block = _format_user_block(user_message, intent, confidence, context_block)
    payload = {
        "model": model,
        "temperature": 0.65,
        "max_tokens": 384,
        "messages": [
            {"role": "system", "content": _REPLY_SYSTEM_PROMPT},
            {"role": "user", "content": user_block},
        ],
    }

    try:
        import httpx

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=_OLLAMA_TIMEOUT_S) as http:
            resp = http.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            log.debug("Ollama conversational HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        content = _strip_code_fences(content)
        return content if content else None
    except Exception as exc:
        log.debug("Ollama conversational reply failed: %s", exc)
        return None


def build_conversational_clarification_reply(
    user_message: str,
    intent: str,
    confidence: Any,
    context: str,
) -> Optional[str]:
    """Return plain text for WhatsApp, or ``None`` to fall back to static clarification."""
    for fn in (_reply_with_gemini, _reply_with_ollama_cloud):
        raw = fn(user_message, intent, confidence, context)
        if not raw:
            continue
        cleaned = _sanitize_reply(raw)
        if cleaned:
            return cleaned
    return None
