"""Optional grounded LLM rewrite of template WhatsApp replies.

Enabled when ``ENABLE_LLM_RESPONSE_REWRITE=1`` and providers are configured;
``main`` gates calls. Uses only JSON facts from ``build_response_with_facts`` —
no free-form API synthesis in the prompt beyond those facts.
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

_GROUNDED_SYSTEM_PROMPT = """You are the WhatsApp assistant for JKYog Radha Krishna Temple in Cedar Park, Texas.

You will receive the user's message and a JSON object called FACTS. The FACTS were built from the event API, recurring schedule data, or static temple information — nothing else.

Write ONE plain-text WhatsApp reply (no markdown headings: no lines starting with #). Match the user's question scope only (e.g. if they asked about parking, focus on parking; do not volunteer food, transport, or registration unless the question is broad or explicitly asks for multiple topics).

Hard rules:
- Use ONLY information present in FACTS. Do not add events, dates, times, prices, URLs, phone numbers, or logistics that are not in FACTS.
- You may copy or lightly paraphrase FACTS. Do not invent filler facts.
- If the user asks for something not present in FACTS, say so plainly. When a field would be unknown in the non-LLM bot, use this exact phrase when appropriate: Not listed on the event page
- Stay warm and concise. No JSON in the reply. No bullet spam unless the user clearly asked for a list."""

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


def _format_grounded_user_block(
    user_message: str, intent: str, confidence: Any, facts: Mapping[str, Any]
) -> str:
    try:
        conf_f = float(confidence)
    except (TypeError, ValueError):
        conf_f = 0.0
    return (
        f"What the user wrote:\n{user_message.strip()}\n\n"
        f"Classifier intent: {intent} (confidence {conf_f:.2f})\n\n"
        f"FACTS (JSON — sole source of truth):\n{_facts_json_block(facts)}"
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
