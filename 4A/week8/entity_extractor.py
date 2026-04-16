import re
from datetime import datetime, timedelta
from typing import Dict

TIMEFRAMES = {
    "today": ["today", "tonight"],
    "tomorrow": ["tomorrow"],
    "this_weekend": ["this weekend"],
    "this_week": ["this week"],
    "friday_evening": ["friday evening"]
}

EVENT_NAMES = [
    "Lohri", "Sakranti", "Sanskriti", "Mahashivratri", "Holi", "Ram Navami", 
    "Youth Leadership Workshop", "Dallas Yoga Fest", "JKYog Spiritual Retreat and Family Camp", 
    "Guru Poornima", "LTP with Swami Mukudananda", "Dallas Retreat", "Janmashtami", 
    "Ganesh Chaturthi", "Navratri", "Dussehra", "Deepavali", "Diwali", "New Year" 
]

PROGRAM_NAMES = [
    "Satsang", "Abhishek", "Sunderkand", "Mata Ki Chowki", "Aarti", "Kirtan", "Chalisa"
]

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

def extract_entities(message: str) -> Dict:
    msg = message.lower()
    entities = {"timeframe": None, "event_name": None, "program_name": None, "parsed_date": None}

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

    entities["parsed_date"] = _extract_date_regex(message)
    if not entities["timeframe"] and entities["parsed_date"]:
        entities["timeframe"] = entities["parsed_date"]

    return entities
