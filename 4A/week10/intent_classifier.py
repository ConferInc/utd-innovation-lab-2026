import os
import json
from typing import Dict
from dotenv import load_dotenv

from entity_extractor import extract_entities

load_dotenv()

try:
    from google import genai
    from google.genai import types as genai_types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


# -------------------------------
# INTENT KEYWORDS (ALL 8 INTENTS)
# -------------------------------
INTENT_KEYWORDS = {
    "logistics": {
        "parking", "where", "address", "location", "directions",
        "map", "how to get", "route", "food", "prasad"
    },
    "sponsorship": {
        "donate", "donation", "sponsor", "sponsorship",
        "contribute", "seva", "fund", "support"
    },
    "discovery": {
        "events", "happening", "going on", "any events",
        "upcoming", "what's happening", "what is happening"
    },
    "no_results_check": {
        "3am", "2am", "4am", "midnight", "overnight",
        "late night", "after midnight", "before dawn"
    },
    "time_based": {
        "today", "tomorrow", "tonight", "this week", "this weekend",
        "next week", "date", "time", "when", "schedule",
        "timing", "start time", "end time"
    },
    "event_specific": {
        "event", "program", "festival", "session",
        "workshop", "class", "celebration",
        "aarti", "darshan", "retreat", "seminar"
    },
    "recurring_schedule": {
        "daily", "every day", "weekly", "every week",
        "every monday", "every tuesday", "every weekend",
        "recurring", "regular", "routine",
        "hours", "open hours", "closing time"
    },
    "ambiguous": {
        "info", "information", "details", "tell me more",
        "help", "something", "stuff", "things",
        "not sure", "anything"
    }
}


# -------------------------------
# SYSTEM PROMPT (LLM)
# -------------------------------
_SYSTEM_PROMPT = """You are an intent classifier for a WhatsApp bot for JKYog Radha Krishna Temple.

Classify the user message into exactly one of these intents:
- time_based
- event_specific
- recurring_schedule
- logistics
- sponsorship
- discovery
- no_results_check
- ambiguous

Respond ONLY with JSON:
{"intent": "<intent>", "confidence": <float>}
"""


# -------------------------------
# HELPERS
# -------------------------------
def tokenize(text: str) -> set:
    return set(text.lower().split())


def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def compute_entity_score(entities: dict) -> float:
    entity_values = [
        entities.get("timeframe"),
        entities.get("event_name"),
        entities.get("program_name"),
    ]
    extracted = sum(1 for v in entity_values if v)
    return extracted / len(entity_values)


# -------------------------------
# GEMINI CLASSIFIER (OPTIONAL)
# -------------------------------
def _classify_with_gemini(user_message: str) -> Dict | None:
    if not GOOGLE_AVAILABLE or not os.getenv("GOOGLE_API_KEY"):
        return None

    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_INTENT", "gemini-2.5-flash-lite"),
            contents=user_message,
            config=genai_types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=60,
            ),
        )

        result = json.loads(response.text.strip())
        return {
            "intent": result.get("intent", "ambiguous"),
            "confidence": float(result.get("confidence", 0.0)),
        }

    except Exception:
        return None


# -------------------------------
# FIXED JACCARD CLASSIFIER
# -------------------------------
def _classify_with_jaccard(message: str, entities: dict) -> Dict:
    msg = message.lower()
    tokens = tokenize(message)

    # -------- Intent Routing --------
    if entities.get("event_name"):
        intent = "event_specific"
    elif entities.get("program_name"):
        intent = "recurring_schedule"
    elif entities.get("timeframe"):
        intent = "time_based"
    elif any(word in msg for word in INTENT_KEYWORDS["logistics"]):
        intent = "logistics"
    elif any(word in msg for word in INTENT_KEYWORDS["sponsorship"]):
        intent = "sponsorship"
    elif any(word in msg for word in INTENT_KEYWORDS["no_results_check"]):
        intent = "no_results_check"
    elif any(word in msg for word in INTENT_KEYWORDS["discovery"]):
        intent = "discovery"
    else:
        intent = "ambiguous"

    # -------- Scores (FIXED) --------
    keyword_score = jaccard_similarity(tokens, INTENT_KEYWORDS.get(intent, set()))
    entity_score = compute_entity_score(entities)

    # -------- Balanced Confidence --------
    if intent in ["event_specific", "time_based", "recurring_schedule"]:
        confidence = 0.6 * entity_score + 0.4 * keyword_score
    elif intent in ["logistics", "sponsorship"]:
        confidence = 0.4 * entity_score + 0.6 * keyword_score
    else:
        confidence = 0.2 * entity_score + 0.8 * keyword_score

    return {
        "intent": intent,
        "confidence": round(confidence, 2),
    }


# -------------------------------
# MAIN CLASSIFIER
# -------------------------------
def classify(message: str) -> Dict:
    entities = extract_entities(message)

    ai_result = _classify_with_gemini(message)

    if not ai_result or ai_result["confidence"] < 0.6:
        result = _classify_with_jaccard(message, entities)
    else:
        result = ai_result

    if result["confidence"] < 0.6:
        result["intent"] = "clarification_needed"

    return {
        "intent": result["intent"],
        "confidence": result["confidence"],
        "entities": entities,
        "api_call": map_to_api(result["intent"], entities),
    }


# -------------------------------
# API MAPPING
# -------------------------------
def map_to_api(intent: str, entities: dict) -> dict:
    event_name = entities.get("event_name")
    timeframe = entities.get("timeframe")

    if intent == "time_based":
        if timeframe == "today":
            return {
                "endpoint": "/api/v2/events/today",
                "method": "GET",
                "params": {},
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"start_date": timeframe},
        }

    elif intent == "event_specific":
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "resolve_event_id_and_fetch_details",
        }

    elif intent == "recurring_schedule":
        return {
            "endpoint": "/api/v2/events/recurring",
            "method": "GET",
            "params": {},
        }

    elif intent == "logistics":
        if not event_name:
            return {"action": "clarification_needed"}
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "fetch_event_details_for_logistics",
        }

    elif intent == "sponsorship":
        if event_name:
            return {
                "endpoint": "/api/v2/events/search",
                "method": "GET",
                "params": {"q": event_name},
                "follow_up": "extract_sponsorship_tiers",
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5},
        }

    elif intent == "discovery":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5},
        }

    elif intent == "no_results_check":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 3},
        }

    return {"action": "clarification_needed"}
