import re
from datetime import datetime, timedelta
from typing import Dict, Optional

TIMEFRAMES = {
    "today": ["today", "tonight"],
    "tomorrow": ["tomorrow"],
    "this_weekend": ["this weekend"],
    # Must appear before "next_week": the phrase "next weekend" contains "next week".
    "next_weekend": ["next weekend"],
    "this_week": ["this week"],
    "next_week": ["next week"],
    "friday_evening": ["friday evening"],
}

EVENT_ALIAS_SEEDS = [
    "Lohri", "Sakranti", "Sanskriti", "Mahashivratri", "Holi", "Ram Navami", 
    "Youth Leadership Workshop", "Dallas Yoga Fest", "JKYog Spiritual Retreat and Family Camp", 
    "Guru Poornima", "LTP with Swami Mukudananda", "Dallas Retreat", "Janmashtami", 
    "Ganesh Chaturthi", "Navratri", "Dussehra", "Deepavali", "Diwali", "New Year" 
]

PROGRAM_NAMES = [
    "Satsang", "Abhishek", "Sunderkand", "Mata Ki Chowki", "Aarti", "Kirtan", "Chalisa"
]

TARGETED_EVENT_PATTERNS = (
    r"(?:tell me about|what is|what's|when is|where is|where's|details for|info(?:rmation)? about|parking for|directions for|how do i get to|sponsorship(?: tiers)? for)\s+(?P<target>.+)",
)

TARGET_STOPWORDS = {
    "a", "an", "about", "address", "at", "by", "details", "did", "do",
    "does", "event", "events", "for", "get", "held", "how", "i", "info",
    "information", "is", "location", "map", "me", "more", "parking",
    "park", "please", "program", "programs", "route", "show", "sponsor",
    "sponsorship", "tell", "the", "tiers", "to", "what", "when", "where",
}

EVENT_HINT_KEYWORDS = {
    "camp", "celebration", "festival", "jayanti", "ltp", "navami",
    "poornima", "retreat", "shivir", "workshop", "yatra",
}
EVENT_HINT_PHRASES = {
    "life transformation",
}

SEEDED_EVENT_NAMES = {name.lower() for name in EVENT_ALIAS_SEEDS}
PROGRAM_NAME_LOOKUP = {name.lower(): name for name in PROGRAM_NAMES}

def _extract_date_regex(text: str) -> str | None:
    text_lower = text.lower()
    today = datetime.now()
    
    days_of_week = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
    for day_name, day_num in days_of_week.items():
        if f"next {day_name}" in text_lower or f"{day_name}" in text_lower:
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead == 0 and "next" in text_lower: days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            
    months = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
    for month_name, month_num in months.items():
        match = re.search(rf"\b({month_name})\s+(\d{{1,2}})(st|nd|rd|th)?\b|\b(\d{{1,2}})(st|nd|rd|th)?\s+({month_name})\b", text_lower)
        if match:
            day = int(match.group(2) or match.group(4))
            year = today.year + 1 if datetime(today.year, month_num, day) < today else today.year
            return f"{year}-{month_num:02d}-{day:02d}"
    return None


def _clean_candidate_phrase(text: str) -> str:
    normalized = re.sub(r"[^\w\s&'-]", " ", text).strip()
    tokens = [token for token in normalized.split() if token]
    kept = [token for token in tokens if token.lower() not in TARGET_STOPWORDS]
    return " ".join(kept).strip()


def _looks_like_event_candidate(candidate: str) -> bool:
    if not candidate:
        return False
    lowered = candidate.lower()
    tokens = lowered.split()
    if lowered in SEEDED_EVENT_NAMES:
        return True
    if len(tokens) >= 2:
        return True
    return any(keyword in lowered for keyword in EVENT_HINT_KEYWORDS)


def _has_specific_event_signal(raw_text: str, cleaned_candidate: str) -> bool:
    lowered = cleaned_candidate.lower()
    tokens = set(lowered.split())
    if lowered in SEEDED_EVENT_NAMES:
        return True
    if tokens & EVENT_HINT_KEYWORDS:
        return True
    if any(phrase in lowered for phrase in EVENT_HINT_PHRASES):
        return True
    return False


def _match_program_name(candidate: str) -> Optional[str]:
    lowered = candidate.lower()
    for program in PROGRAM_NAMES:
        if program.lower() in lowered.split():
            return program
    return None


def _extract_dynamic_event_candidate(message: str) -> Optional[str]:
    message = (message or "").strip()
    if not message:
        return None

    for pattern in TARGETED_EVENT_PATTERNS:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if not match:
            continue
        candidate = _clean_candidate_phrase(match.group("target"))
        if _looks_like_event_candidate(candidate) and _has_specific_event_signal(match.group("target"), candidate):
            return candidate

    fallback = _clean_candidate_phrase(message)
    if _looks_like_event_candidate(fallback) and _has_specific_event_signal(message, fallback):
        return fallback
    return None

def extract_entities(message: str) -> Dict:
    msg = message.lower()
    entities = {"timeframe": None, "event_name": None, "program_name": None, "parsed_date": None}

    for key, values in TIMEFRAMES.items():
        if any(v in msg for v in values):
            entities["timeframe"] = key
            break
            
    for event in EVENT_ALIAS_SEEDS:
        if event.lower() in msg: 
            entities["event_name"] = event
            break
            
    for program in PROGRAM_NAMES:
        if program.lower() in msg: 
            entities["program_name"] = program
            break

    if not entities["event_name"]:
        dynamic_event = _extract_dynamic_event_candidate(message)
        if dynamic_event:
            matched_program = _match_program_name(dynamic_event)
            if matched_program and not _has_specific_event_signal(message, dynamic_event):
                entities["program_name"] = entities["program_name"] or matched_program
            elif dynamic_event.lower() not in PROGRAM_NAME_LOOKUP:
                entities["event_name"] = dynamic_event
            elif not entities["program_name"]:
                entities["program_name"] = PROGRAM_NAME_LOOKUP[dynamic_event.lower()]

    entities["parsed_date"] = _extract_date_regex(message)
    if not entities["timeframe"] and entities["parsed_date"]:
        entities["timeframe"] = entities["parsed_date"]

    return entities
