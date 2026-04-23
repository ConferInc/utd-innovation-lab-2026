"""
Intent Classifier (Week 7 Spec + Week 8/9 API Mapping)

Approach: Hybrid (Rule-based + Knowledge-Based Scoring)

Design:
1. Rule-based intent classification using:
   - Extracted entities (event_name, timeframe, program_name)
   - Keyword matching (from Week 7 intent catalog)

2. Confidence Scoring (Fully Dynamic, No Hardcoding):
   - Jaccard similarity between message tokens and intent keywords
   - Entity coverage score (ratio of extracted entities)
   - Final confidence = average of keyword score and entity score

3. Spec Rule:
   - If confidence < 0.6 → return "clarification_needed"

This ensures:
- Explainable AI (no arbitrary confidence values)
- Alignment with Week 7 intent definitions
- API-ready outputs for Week 8/9 integration
"""

from typing import Dict
from entity_extractor import extract_entities


# -------------------------------
# INTENT KEYWORD KB (Week 7 aligned)
# -------------------------------
INTENT_KEYWORDS = {
    "time_based": {
        "today", "tomorrow", "tonight", "weekend", "week", "month",
        "date", "dates", "when", "schedule", "upcoming", "soon"
    },
    "event_specific": {
        "event", "festival", "show", "details", "about",
        "info", "information", "attend", "ticket", "tickets"
    },
    "recurring_schedule": {
        "every", "weekly", "daily", "monthly", "recurring", "regular",
        "ongoing", "program", "series", "class", "classes"
    },
    "logistics": {
        "parking", "where", "address", "location", "directions", "venue",
        "entry", "entrance", "map", "getting", "arrive"
    },
    "sponsorship": {
        "donate", "donation", "sponsor", "sponsorship", "contribute",
        "support", "partner", "fund", "funding", "money"
    },
    "discovery": {
        "events", "event", "happening", "going", "any", "discover",
        "find", "browse", "upcoming", "around"
    },
    "no_results_check": {
        "3am", "midnight", "late night", "overnight", "after midnight", "before dawn"
    },
    "ambiguous": {
        "help", "question", "something", "anything", "info", "information"
    },
}


# -------------------------------
# TOKENIZATION
# -------------------------------
def tokenize(text: str) -> set:
    return set(text.lower().split())


# -------------------------------
# JACCARD SIMILARITY
# -------------------------------
def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


# -------------------------------
# ENTITY COVERAGE SCORE
# -------------------------------
INTENT_ENTITY_FIELDS = {
    "time_based": {"timeframe"},
    "event_specific": {"event_name"},
    "recurring_schedule": {"program_name"},
    "logistics": {"event_name"},
    "sponsorship": set(),
    "discovery": set(),
    "no_results_check": {"timeframe"},
    "ambiguous": set(),
}


def compute_entity_score(intent: str, entities: dict) -> float:
    required_fields = INTENT_ENTITY_FIELDS.get(intent, set())
    if not required_fields:
        return 0.0

    matched_fields = sum(1 for field in required_fields if entities.get(field))
    return matched_fields / len(required_fields)


# -------------------------------
# FINAL KB SCORE
# -------------------------------
def compute_kb_score(message: str, intent: str, entities: dict) -> float:
    tokens = tokenize(message)

    intent_keywords = INTENT_KEYWORDS.get(intent, set())
    keyword_score = jaccard_similarity(tokens, intent_keywords)

    entity_score = compute_entity_score(intent, entities)

    scores = [keyword_score]
    if INTENT_ENTITY_FIELDS.get(intent):
        scores.append(entity_score)

    confidence = sum(scores) / len(scores)

    return round(confidence, 2)


# -------------------------------
# MAIN CLASSIFIER
# -------------------------------
def classify(message: str) -> Dict:
    msg = message.lower()
    entities = extract_entities(message)

    # -------------------------------
    # INTENT MAPPING (8 intents only)
    # -------------------------------
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

    elif any(phrase in msg for phrase in [
        "what's happening", "what is happening", "any events", "events"
    ]):
        intent = "discovery"

    elif any(word in msg for word in INTENT_KEYWORDS["no_results_check"]):
        intent = "no_results_check"

    else:
        intent = "ambiguous"

    # -------------------------------
    # CONFIDENCE
    # -------------------------------
    confidence = compute_kb_score(message, intent, entities)

    # -------------------------------
    # SPEC RULE
    # -------------------------------
    if confidence < 0.6:
        return {
            "intent": "clarification_needed",
            "confidence": confidence,
            "entities": {
                "timeframe": entities.get("timeframe"),
                "event_name": entities.get("event_name"),
                "program_name": entities.get("program_name"),
            },
            "api_call": {"action": "clarification_needed"}
        }

    # -------------------------------
    # API MAPPING
    # -------------------------------
    api_call = map_to_api(intent, entities)

    return {
        "intent": intent,
        "confidence": confidence,
        "entities": {
            "timeframe": entities.get("timeframe"),
            "event_name": entities.get("event_name"),
            "program_name": entities.get("program_name"),
        },
        "api_call": api_call
    }


# -------------------------------
# API MAPPING (Week 8/9 Spec)
# -------------------------------
def map_to_api(intent: str, entities: dict) -> dict:
    event_name = entities.get("event_name")
    timeframe = entities.get("timeframe")

    if intent == "time_based":
        if timeframe == "today":
            return {
                "endpoint": "/api/v2/events/today",
                "method": "GET",
                "params": {}
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"start_date": timeframe}
        }

    elif intent == "event_specific":
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "resolve_event_id_and_fetch_details"
        }

    elif intent == "recurring_schedule":
        return {
            "endpoint": "/api/v2/events/recurring",
            "method": "GET",
            "params": {}
        }

    elif intent == "logistics":
        if not event_name:
            return {"action": "clarification_needed"}
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "fetch_event_details_for_logistics"
        }

    elif intent == "sponsorship":
        if event_name:
            return {
                "endpoint": "/api/v2/events/search",
                "method": "GET",
                "params": {"q": event_name},
                "follow_up": "extract_sponsorship_tiers"
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5}
        }

    elif intent == "discovery":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5}
        }

    elif intent == "no_results_check":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 3}
        }

    return {"action": "clarification_needed"}
