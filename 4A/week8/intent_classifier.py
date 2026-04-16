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

INTENT_KEYWORDS = {
    "logistics": {"parking", "where", "address", "location", "directions"},
    "sponsorship": {"donate", "donation", "sponsor", "contribute"},
    "discovery": {"events", "happening", "going", "any"},
    "no_results_check": {"3am", "midnight"},
}

_SYSTEM_PROMPT = """You are an intent classifier for a WhatsApp bot for JKYog Radha Krishna Temple.
Classify the user message into exactly one of these intents based on their request:
- time_based: asking about events today, tomorrow, or a specific date/time
- event_specific: asking about a specific named event (e.g., Holi, Diwali, Retreat)
- recurring_schedule: asking about daily/weekly programs (e.g., Satsang, Aarti)
- logistics: asking about parking, location, directions, or food
- sponsorship: asking about donations, seva, or sponsorship tiers
- discovery: general queries about what is happening or upcoming events
- no_results_check: nonsense times or impossible requests

Respond ONLY with valid JSON in this exact format:
{"intent": "<intent>", "confidence": <float between 0.0 and 1.0>}"""

def tokenize(text: str) -> set:
    return set(text.lower().split())

def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def compute_entity_score(entities: dict) -> float:
    entity_values = [entities.get("timeframe"), entities.get("event_name"), entities.get("program_name")]
    extracted_count = sum(1 for val in entity_values if val)
    total_possible = len(entity_values)
    return extracted_count / total_possible if total_possible else 0.0

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
        return {"intent": result.get("intent", "clarification_needed"), "confidence": float(result.get("confidence", 0.0))}
    except Exception:
        return None

def _classify_with_jaccard(message: str, entities: dict) -> Dict:
    msg = message.lower()
    
    if entities.get("event_name"): intent = "event_specific"
    elif entities.get("program_name"): intent = "recurring_schedule"
    elif entities.get("timeframe"): intent = "time_based"
    elif any(word in msg for word in INTENT_KEYWORDS["logistics"]): intent = "logistics"
    elif any(word in msg for word in INTENT_KEYWORDS["sponsorship"]): intent = "sponsorship"
    elif any(p in msg for p in ["what's happening", "any events", "events"]): intent = "discovery"
    elif any(word in msg for word in INTENT_KEYWORDS["no_results_check"]): intent = "no_results_check"
    else: intent = "ambiguous"

    keyword_score = jaccard_similarity(tokenize(message), INTENT_KEYWORDS.get(intent, set()))
    confidence = round((keyword_score + compute_entity_score(entities)) / 2, 2)
    return {"intent": intent, "confidence": confidence}

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
        "api_call": map_to_api(result["intent"], entities)
    }

def map_to_api(intent: str, entities: dict) -> dict:
    event_name = entities.get("event_name")
    timeframe = entities.get("timeframe")

    if intent == "time_based":
        if timeframe == "today":
            return {"endpoint": "/api/v2/events/today", "method": "GET", "params": {}}
        return {"endpoint": "/api/v2/events", "method": "GET", "params": {"start_date": timeframe}}
    elif intent == "event_specific":
        return {"endpoint": "/api/v2/events/search", "method": "GET", "params": {"q": event_name}, "follow_up": "resolve_event_id_and_fetch_details"}
    elif intent == "recurring_schedule":
        return {"endpoint": "/api/v2/events/recurring", "method": "GET", "params": {}}
    elif intent == "logistics":
        if not event_name: return {"action": "clarification_needed"}
        return {"endpoint": "/api/v2/events/search", "method": "GET", "params": {"q": event_name}, "follow_up": "fetch_event_details_for_logistics"}
    elif intent == "sponsorship":
        if event_name: return {"endpoint": "/api/v2/events/search", "method": "GET", "params": {"q": event_name}, "follow_up": "extract_sponsorship_tiers"}
        return {"endpoint": "/api/v2/events", "method": "GET", "params": {"limit": 5}}
    elif intent == "discovery":
        return {"endpoint": "/api/v2/events", "method": "GET", "params": {"limit": 5}}
    elif intent == "no_results_check":
        return {"endpoint": "/api/v2/events", "method": "GET", "params": {"limit": 3}}
    return {"action": "clarification_needed"}
