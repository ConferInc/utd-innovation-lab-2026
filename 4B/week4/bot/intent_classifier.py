"""
Intent Classifier for JKYog WhatsApp Bot

Classifies user messages into intents using Gemini zero-shot classification
with a keyword regex fallback for when the Google API is unavailable.
"""

import json
import os
import re
from typing import Dict

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types as genai_types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

load_dotenv()

_SYSTEM_PROMPT = """You are an intent classifier for a WhatsApp bot for JKYog Radha Krishna Temple.

Classify the user message into exactly one of these intents:
- greeting: greetings or salutations (Hello, Hi, Namaste, Hari Om, Radhe Radhe, Good morning, etc.)
- faq_query: questions about temple information such as location, address, hours, dress code, parking, or philosophy
- event_query: questions about events, schedules, or timings (satsang, bhajans, Holi Mela, kirtan, meditation, calendar)
- donation_request: anything about donating, contributing, or making a payment to the temple
- directions_request: asking how to get to the temple, navigation, routes, or directions
- unknown: anything that does not fit the above categories

Respond ONLY with valid JSON in this exact format (no explanation, no markdown):
{"intent": "<intent>", "confidence": <float between 0.0 and 1.0>}"""

# Keyword patterns used as fallback when Google API is unavailable
_KEYWORD_PATTERNS = {
    "greeting": [
        r"\b(hello|hi|hey|namaste|greetings?|good (morning|evening|afternoon|night))\b",
        r"\b(hari om|radhe radhe|jai shri ram|jai radhe)\b",
    ],
    "event_query": [
        r"\b(satsang|bhajan|mela|holi|kirtan|meditation|schedule|calendar|event)\b",
        r"\b(when|what time|upcoming|next)\b.{0,30}\b(temple|event|satsang|bhajan)\b",
    ],
    "donation_request": [
        r"\b(donat(e|ion)|contribut(e|ion)|payment|give|fund|help financially|support the temple)\b",
    ],
    "directions_request": [
        r"\b(direction|route|navigation|how (do i|to) (get|reach)|way to get|miles from)\b",
        r"\b(get to|drive to|from (dallas|irving|plano|frisco|mckinney))\b",
    ],
    "faq_query": [
        r"\b(location|address|hours?|timings?|open|close|dress code|parking|philosophy|bhakti)\b",
        r"\b(when (does|is) the temple|what (are|is) the temple)\b",
    ],
}

_VALID_INTENTS = {"greeting", "faq_query", "event_query", "donation_request", "directions_request", "unknown"}


def _classify_with_gemini(user_message: str) -> Dict[str, object] | None:
    """Classify intent using Gemini. Returns None if unavailable or on error."""
    if not GOOGLE_AVAILABLE or not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=user_message,
            config=genai_types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=60,
            ),
        )
        raw = response.text.strip()
        result = json.loads(raw)
        intent = result.get("intent", "unknown")
        confidence = float(result.get("confidence", 0.0))
        if intent not in _VALID_INTENTS:
            intent = "unknown"
        return {"intent": intent, "confidence": confidence}
    except Exception as exc:
        print(f"Gemini classification error: {exc}")
        return None


def _classify_with_keywords(user_message: str) -> Dict[str, object]:
    """Classify intent using keyword regex patterns (fallback)."""
    message_lower = user_message.lower()
    scores: Dict[str, int] = {}

    for intent, patterns in _KEYWORD_PATTERNS.items():
        score = sum(len(re.findall(p, message_lower, re.IGNORECASE)) for p in patterns)
        if score > 0:
            scores[intent] = score

    if not scores:
        return {"intent": "unknown", "confidence": 0.0}

    best_intent = max(scores, key=scores.get)
    # Cap confidence lower than Gemini to signal it's a fallback result
    confidence = min(0.55, 0.35 + scores[best_intent] * 0.1)
    return {"intent": best_intent, "confidence": confidence}


def classify_intent(user_message: str) -> Dict[str, object]:
    """
    Classify a user message into an intent category.

    Tries Gemini first for accurate zero-shot classification.
    Falls back to keyword matching if the API is unavailable or errors.

    Args:
        user_message: The raw text message from the user.

    Returns:
        {"intent": str, "confidence": float}
        intent is one of: greeting, faq_query, event_query,
                          donation_request, directions_request, unknown
    """
    if not user_message or not user_message.strip():
        return {"intent": "unknown", "confidence": 0.0}

    result = _classify_with_gemini(user_message)

    if result is None:
        result = _classify_with_keywords(user_message)

    if result["confidence"] < 0.4:
        result["intent"] = "unknown"

    return result
