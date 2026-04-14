"""
Intent Classifier (Week 7 + Week 8/9 API-Aligned)

Approach: Hybrid (Entity-first + Rule-based)

Key Features:
- Entity-driven classification (matches design doc)
- Priority-based intent resolution
- API contract v2.1 compliant mapping
- No fabricated data (strict schema alignment)
- Multi-step API calls via follow_up actions
"""

from typing import Dict
from entity_extractor import extract_entities


def classify(message: str) -> Dict:
    msg = message.lower()
    entities = extract_entities(message)

    intent = None
    confidence = 0.0

    # -------------------------------
    # INTENT CLASSIFICATION (PRIORITY ORDER)
    # -------------------------------

    # 1. EVENT SPECIFIC
    if entities["event_name"]:
        intent = "event_specific"
        confidence = 0.9

    # 2. RECURRING
    elif entities["program_name"]:
        intent = "recurring_schedule"
        confidence = 0.85

    # 3. TIME-BASED
    elif entities["timeframe"]:
        intent = "time_based"
        confidence = 0.8

    # 4. LOGISTICS
    elif any(word in msg for word in ["parking", "where", "address", "location", "directions"]):
        intent = "logistics"
        confidence = 0.8

    # 5. SPONSORSHIP
    elif any(word in msg for word in ["donate", "donation", "sponsor", "contribute"]):
        intent = "sponsorship"
        confidence = 0.85

    # 6. DISCOVERY
    elif any(phrase in msg for phrase in [
        "what's happening", "what is happening", "any events", "events", "what's going on"
    ]):
        intent = "discovery"
        confidence = 0.75

    # 7. NO RESULTS CHECK (edge case)
    elif "3 am" in msg or "midnight" in msg:
        intent = "no_results_check"
        confidence = 0.7

    # 8. AMBIGUOUS
    else:
        intent = "ambiguous"
        confidence = 0.5

    # -------------------------------
    # CONFIDENCE CHECK
    # -------------------------------
    if confidence < 0.6:
        return {
            "intent": "clarification_needed",
            "confidence": confidence,
            "entities": entities,
            "api_call": {"action": "clarification_needed"}
        }

    # -------------------------------
    # MAP TO API
    # -------------------------------
    api_call = map_to_api(intent, entities)

    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "api_call": api_call
    }


def map_to_api(intent: str, entities: dict) -> dict:
    event_name = entities.get("event_name")
    timeframe = entities.get("timeframe")

    # -------------------------------
    # TIME-BASED
    # -------------------------------
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
            "params": {
                "start_date": timeframe
            }
        }

    # -------------------------------
    # EVENT SPECIFIC
    # -------------------------------
    elif intent == "event_specific":
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "resolve_event_id_and_fetch_details"
        }

    # -------------------------------
    # RECURRING
    # -------------------------------
    elif intent == "recurring_schedule":
        return {
            "endpoint": "/api/v2/events/recurring",
            "method": "GET",
            "params": {}
        }

    # -------------------------------
    # LOGISTICS
    # -------------------------------
    elif intent == "logistics":

        if not event_name:
            return {"action": "clarification_needed"}

        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "fetch_event_details_for_logistics"
        }

    # -------------------------------
    # SPONSORSHIP
    # -------------------------------
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

    # -------------------------------
    # DISCOVERY
    # -------------------------------
    elif intent == "discovery":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5}
        }

    # -------------------------------
    # NO RESULTS
    # -------------------------------
    elif intent == "no_results_check":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 3}
        }

    return {"action": "clarification_needed"}
