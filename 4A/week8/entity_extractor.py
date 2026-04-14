"""
Entity Extractor (Week 7 Aligned)

Extracts:
- timeframe
- event_name
- program_name

Rule-based, deterministic, no hallucination
"""

from typing import Dict


TIMEFRAMES = {
    "today": ["today", "tonight"],
    "tomorrow": ["tomorrow"],
    "this_weekend": ["this weekend"],
    "this_week": ["this week"],
    "friday_evening": ["friday evening"]
}

EVENT_NAMES = [
    "holi festival",
    "hanuman jayanti",
    "ram navami",
    "diwali gala"
]

PROGRAM_NAMES = [
    "darshan",
    "aarti",
    "satsang",
    "yoga"
]


def extract_entities(message: str) -> Dict:
    msg = message.lower()

    entities = {
        "timeframe": None,
        "event_name": None,
        "program_name": None
    }

    # Timeframe
    for key, values in TIMEFRAMES.items():
        if any(v in msg for v in values):
            entities["timeframe"] = key
            break

    # Event
    for event in EVENT_NAMES:
        if event in msg:
            entities["event_name"] = event
            break

    # Program
    for program in PROGRAM_NAMES:
        if program in msg:
            entities["program_name"] = program
            break

    return entities
