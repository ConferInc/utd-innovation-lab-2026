"""
Entity Extractor for JKYog WhatsApp Bot
Rohan Kothapalli - Week 3 Assignment

Extracts structured entities from user messages using regex patterns
and context-aware extraction based on detected intent.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional


def _extract_date(text: str) -> Optional[str]:
    """
    Extract date from text and return in ISO format (YYYY-MM-DD).
    
    Supports:
    - Explicit dates: "March 7", "3/7", "7th March"
    - Relative dates: "today", "tomorrow", "next Friday"
    """
    text_lower = text.lower()
    today = datetime.now()
    
    # Handle relative dates
    if "today" in text_lower:
        return today.strftime("%Y-%m-%d")
    
    if "tomorrow" in text_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Handle "next [day of week]"
    days_of_week = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    for day_name, day_num in days_of_week.items():
        if f"next {day_name}" in text_lower or f"{day_name}" in text_lower:
            current_day = today.weekday()
            days_ahead = (day_num - current_day) % 7
            if days_ahead == 0 and "next" in text_lower:
                days_ahead = 7
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%Y-%m-%d")
    
    # Handle month names with day numbers
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for month_name, month_num in months.items():
        # Pattern: "March 7" or "7 March" or "7th March"
        pattern = rf"\b({month_name})\s+(\d{{1,2}})(st|nd|rd|th)?\b|\b(\d{{1,2}})(st|nd|rd|th)?\s+({month_name})\b"
        match = re.search(pattern, text_lower)
        if match:
            # Extract day number
            day_str = match.group(2) or match.group(4)
            day = int(day_str)
            
            # Assume current year or next year if date has passed
            year = today.year
            test_date = datetime(year, month_num, day)
            if test_date < today:
                year += 1
            
            return f"{year}-{month_num:02d}-{day:02d}"
    
    # Handle numeric dates: "3/7", "03/07", "3-7"
    date_pattern = r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b"
    match = re.search(date_pattern, text)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        year = int(match.group(3)) if match.group(3) else today.year
        
        # Handle 2-digit year
        if year < 100:
            year += 2000
        
        try:
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    return None


def _extract_time(text: str) -> Optional[str]:
    """
    Extract time from text and return in 24-hour format (HH:MM).
    
    Supports:
    - "7pm", "7:30pm", "7:30 PM"
    - "10:00 AM", "10am"
    - "19:30", "1930"
    """
    text_lower = text.lower()
    
    # Pattern for time with AM/PM
    am_pm_pattern = r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b"
    match = re.search(am_pm_pattern, text_lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)
        
        # Convert to 24-hour format
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    
    # Pattern for 24-hour format
    time_pattern = r"\b(\d{1,2}):(\d{2})\b"
    match = re.search(time_pattern, text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if 0 <= hour < 24 and 0 <= minute < 60:
            return f"{hour:02d}:{minute:02d}"
    
    return None


def _extract_location(text: str) -> Optional[str]:
    """
    Extract location/city names from text.
    
    Focuses on common Texas cities and general location references.
    """
    text_lower = text.lower()
    
    # Common Texas cities
    cities = [
        "dallas", "irving", "plano", "allen", "frisco", "mckinney",
        "richardson", "garland", "fort worth", "arlington", "houston",
        "austin", "san antonio"
    ]
    
    for city in cities:
        if city in text_lower:
            return city.title()
    
    # Check for "from [location]" pattern
    from_pattern = r"\bfrom\s+([a-zA-Z\s]+?)(?:\s+to|\s+$|\.|,)"
    match = re.search(from_pattern, text, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        if len(location) > 2:
            return location.title()
    
    return None


def _extract_event_type(text: str) -> Optional[str]:
    """
    Extract event type from text.
    
    Supports: satsang, mela, bhajan, meditation, kirtan, etc.
    """
    text_lower = text.lower()
    
    event_types = {
        "satsang": ["satsang", "satsangs"],
        "mela": ["mela", "festival", "holi mela"],
        "bhajan": ["bhajan", "bhajans", "devotional singing"],
        "meditation": ["meditation", "dhyan"],
        "kirtan": ["kirtan", "kirtans"],
        "yoga": ["yoga", "kriya yoga"],
        "discourse": ["discourse", "pravachan"],
    }
    
    for event_type, keywords in event_types.items():
        for keyword in keywords:
            if keyword in text_lower:
                return event_type
    
    return None


def _extract_amount(text: str) -> Optional[float]:
    """
    Extract donation amount from text.
    
    Supports: "$50", "50 dollars", "100", etc.
    """
    # Pattern for dollar amounts
    dollar_pattern = r"\$\s*(\d+(?:\.\d{2})?)"
    match = re.search(dollar_pattern, text)
    if match:
        return float(match.group(1))
    
    # Pattern for numbers with "dollar" or "dollars"
    amount_pattern = r"\b(\d+(?:\.\d{2})?)\s*dollars?\b"
    match = re.search(amount_pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Look for standalone numbers in donation context
    if any(word in text.lower() for word in ["donate", "donation", "contribute"]):
        number_pattern = r"\b(\d+(?:\.\d{2})?)\b"
        match = re.search(number_pattern, text)
        if match:
            amount = float(match.group(1))
            # Only consider reasonable donation amounts
            if 1 <= amount <= 100000:
                return amount
    
    return None


def extract_entities(user_message: str, intent: str) -> Dict[str, any]:
    """
    Extract structured entities from user message.
    
    Extraction is context-aware based on the detected intent.
    
    Args:
        user_message: The user's input message
        intent: The detected intent (from intent_classifier)
    
    Returns:
        Dictionary with extracted entities. Possible keys:
        - date: ISO format string (YYYY-MM-DD)
        - time: 24-hour format (HH:MM)
        - location: User location for directions
        - event_type: satsang, mela, bhajan, meditation, etc.
        - amount: Donation amount (float)
    
    Example:
        >>> extract_entities("When is satsang on Friday at 7pm?", "event_query")
        {"date": "2026-03-07", "time": "19:00", "event_type": "satsang"}
    """
    entities = {}
    
    # Extract based on intent type
    if intent == "event_query":
        # For event queries, prioritize date, time, and event type
        date = _extract_date(user_message)
        if date:
            entities["date"] = date
        
        time = _extract_time(user_message)
        if time:
            entities["time"] = time
        
        event_type = _extract_event_type(user_message)
        if event_type:
            entities["event_type"] = event_type
    
    elif intent == "directions_request":
        # For directions, extract user location
        location = _extract_location(user_message)
        if location:
            entities["location"] = location
    
    elif intent == "donation_request":
        # For donations, extract amount if specified
        amount = _extract_amount(user_message)
        if amount:
            entities["amount"] = amount
    
    elif intent == "faq_query":
        # For FAQs, we might extract event type if asking about specific events
        event_type = _extract_event_type(user_message)
        if event_type:
            entities["event_type"] = event_type
    
    # Always extract date and time if present (useful for context)
    if "date" not in entities:
        date = _extract_date(user_message)
        if date:
            entities["date"] = date
    
    if "time" not in entities:
        time = _extract_time(user_message)
        if time:
            entities["time"] = time
    
    return entities


if __name__ == "__main__":
    # Test the entity extractor
    test_cases = [
        ("When is satsang on Friday at 7pm?", "event_query"),
        ("Directions from Dallas to the temple", "directions_request"),
        ("I want to donate $100", "donation_request"),
        ("What time does the temple open tomorrow?", "faq_query"),
        ("Tell me about holi mela on March 7", "event_query"),
        ("How do I get there from Irving?", "directions_request"),
    ]
    
    print("\n=== Entity Extractor Test ===\n")
    for message, intent in test_cases:
        entities = extract_entities(message, intent)
        print(f"Message: {message}")
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        print()
