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
    "Lohri",
    "Sakranti",
    "Sanskriti",
    "Mahashivratri",
    "Holi",
    "Ram Navami",
    "Youth Leadership Workshop",
    "Dallas Yoga Fest",
    "JKYog Spiritual Retreat and Family Camp",
    "Guru Poornima",
    "LTP with Swami Mukudananda",
    "Dallas Retreat",
    "Janmashtami",
    "Ganesh Chaturthi",
    "Navratri",
    "Dussehra",
    "Deepavali",
    "Diwali",
    "New Year" 
]

PROGRAM_NAMES = [
    "Satsang",
    "Abhishek",
    "Sunderkand",
    "Mata Ki Chowki",
    "Aarti",
    "Kirtan",
    "Chalisa"
]

def extract_entities(message: str) -> Dict:
    msg = message.lower()
    entities = {"timeframe": None, "event_name": None, "program_name": None}

    
    for key, values in TIMEFRAMES.items():
        if any(v in msg for v in values):
            entities["timeframe"] = key
            break

    
    for event in EVENT_NAMES:
        if event.lower() in msg: 
            entities["event_name"] = event
            break

    
    for program in PROGRAM_NAMES:
        if program.lower() in msg: 
            entities["program_name"] = program
            break

    return entities
