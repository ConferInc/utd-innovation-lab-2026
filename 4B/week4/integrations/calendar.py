"""
Google Calendar API + Knowledge Base Fallback
Subodh Krishna Nikumbh - Week 3 JKYog WhatsApp Bot
Integrates Leena Hussein's knowledge_base/events.json
"""

import os
import json
import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")


def _try_calendar_api(limit: int = 5) -> List[Dict]:
    """Attempt real Google Calendar API"""
    if not SERVICE_ACCOUNT_JSON:
        return []
    
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_JSON,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        service = build("calendar", "v3", credentials=creds)
        
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        return [
            {
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "summary": event.get("summary", "Unnamed Event"),
                "location": event.get("location", "TBD"),
            }
            for event in events_result.get("items", [])
        ]
    except:
        return []


def _load_events_from_kb() -> List[Dict]:
    """Load from Leena's knowledge_base/events.json"""
    try:
        with open("knowledge_base/events.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Demo data matching Leena's expected format
        return [
            {
                "start": "2026-03-07T10:00:00",
                "summary": "Morning Meditation & Kriya Yoga Class",
                "location": "Dallas Temple"
            },
            {
                "start": "2026-03-07T18:00:00", 
                "summary": "Evening Kirtan & Discourse",
                "location": "Irving Temple"
            }
        ]


def get_upcoming_events(limit: int = 5) -> List[Dict]:
    """Rohan's bot entrypoint - API first, then Knowledge Base"""
    events = _try_calendar_api(limit)
    if not events:
        events = _load_events_from_kb()[:limit]
    return events


def get_events_on_date(date_str: str) -> List[Dict]:
    """Rohan's bot entrypoint - events for specific date"""
    all_events = _try_calendar_api(20) or _load_events_from_kb()
    
    target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    filtered = []
    
    for event in all_events:
        try:
            event_date = datetime.datetime.fromisoformat(event["start"]).date()
            if event_date == target_date:
                filtered.append(event)
        except:
            continue
    
    return filtered


class GoogleCalendarIntegration:
    """Google Calendar API + knowledge base fallback integration."""

    def list_events(self, limit: int = 5) -> List[Dict]:
        """List upcoming events (API first, then KB fallback)."""
        return get_upcoming_events(limit=limit)
