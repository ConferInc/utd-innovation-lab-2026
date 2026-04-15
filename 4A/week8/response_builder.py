"""Response builder for Team 4A / Team 4B integration (FINAL ALIGNED VERSION)."""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence
from api_client import APIClientError, APIConfig, EventAPIClient
from recurring_handler import get_current_schedule, TIMEZONE

WHATSAPP_CHAR_LIMIT = 4096
MISSING_FIELD_TEXT = "Not listed on the event page"
DEFAULT_LIST_LIMIT = 5

def build_response(classified_intent: dict, session_context: dict) -> str:
    """Build the final WhatsApp response for the user."""
    classified_intent = classified_intent or {}
    session_context = session_context or {}

    client = _get_api_client(session_context)
    intent = classified_intent.get("intent", "event_list")
    query = _resolve_query(classified_intent, session_context)
    event_id = _resolve_event_id(classified_intent, session_context)

    try:
        
        if intent == "recurring_events":
            local_sched = get_current_schedule(datetime.now(TIMEZONE))
            header = ""
            if local_sched.get("exception"):
                header = f"⚠️ *TEMPLE NOTICE:* {local_sched['exception']}\n\n"
            
            api_resp = _build_event_list_response(client, intent=intent, query=query)
            return header + api_resp

        
        if intent in {"event_list", "event_search", "today_events"}:
            return _build_event_list_response(client, intent=intent, query=query)

        
        if intent in {"single_event_detail", "event_detail"}:
            event = _resolve_single_event(client, event_id=event_id, query=query)
            if event is None:
                return _format_no_results(query or "your request")
            return _truncate_whatsapp(_format_single_event(event))

        
        if intent in {"sponsorship", "sponsorship_tiers"}:
            event = _resolve_single_event(client, event_id=event_id, query=query)
            if event is None:
                return _format_no_results(query or "your request")
            return _truncate_whatsapp(_format_sponsorship(event))

        
        if intent in {"logistics", "parking", "logistics_parking"}:
            event = _resolve_single_event(client, event_id=event_id, query=query)
            if event is None:
                return _format_no_results(query or "your request")
            return _truncate_whatsapp(_format_logistics(event))

        
        return _truncate_whatsapp(_build_event_list_response(client, intent="event_list", query=query))

    except APIClientError:
        return "I could not retrieve event info right now. Please try again soon."
    except Exception:
        return "I ran into an issue building the response. Please try again."



def _get_api_client(session_context: Mapping[str, Any]) -> EventAPIClient:
    config = APIConfig(
        base_url=session_context.get("api_base_url") or APIConfig().base_url,
        bearer_token=session_context.get("api_bearer_token") or APIConfig().bearer_token,
    )
    return EventAPIClient(config=config)

def _resolve_query(classified_intent: dict, session_context: dict) -> Optional[str]:
    
    entities = classified_intent.get("entities", {})
    return entities.get("event_name") or classified_intent.get("query") or session_context.get("last_query")

def _resolve_event_id(classified_intent: dict, session_context: dict) -> Optional[int]:
    val = classified_intent.get("entities", {}).get("event_id") or session_context.get("selected_event_id")
    try:
        return int(val) if val else None
    except:
        return None

def _extract_events(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Defensive check for Team 4B's response keys."""
    events = payload.get("events") or payload.get("results")
    if isinstance(events, list):
        return [e for e in events if isinstance(e, dict)]
    return []

def _build_event_list_response(client: EventAPIClient, *, intent: str, query: Optional[str]) -> str:
    if intent == "today_events":
        payload = client.get_today()
        heading = "today"
    elif intent == "recurring_events":
        payload = client.get_recurring()
        heading = "recurring programs"
    elif query:
        payload = client.search_events(query)
        heading = query
    else:
        payload = client.get_events()
        heading = "upcoming events"

    events = _extract_events(payload)
    if not events:
        return _format_no_results(heading)

    return _format_event_list(events[:5], heading)



def _format_single_event(event: Mapping[str, Any]) -> str:
    name = event.get('name') or MISSING_FIELD_TEXT
    date_text = f"When: {event.get('start_datetime', MISSING_FIELD_TEXT)}"
    loc = f"Where: {event.get('location_name') or event.get('address') or MISSING_FIELD_TEXT}"
    desc = event.get('description') or MISSING_FIELD_TEXT
    
    lines = [
        f"*{name}*",
        f"{date_text}",
        f"{loc}",
        "",
        f"{desc}",
        "",
        f"More info: {event.get('source_url', 'Check website')}"
    ]
    return "\n".join(lines)

def _format_event_list(events: Sequence[Mapping[str, Any]], query: str) -> str:
    lines = [f"Here are the events I found for *{query}*:", ""]
    for i, event in enumerate(events, start=1):
        lines.append(f"{i}) *{event.get('name', 'Event')}*")
        lines.append(f"   {event.get('start_datetime', 'TBD')}")
    
    lines.extend(["", "Reply with a number for details, or 'logistics' for parking info."])
    return "\n".join(lines)

def _format_no_results(query: str) -> str:
    return f"I couldn't find any matching events for *{query}* right now. Try a general name like 'Holi' or 'Satsang'."

def _format_sponsorship(event: Mapping[str, Any]) -> str:
    tiers = event.get("sponsorship_tiers", [])
    bullets = [f"• {t.get('tier_name')}: ${t.get('price')}" for t in tiers] if tiers else [f"• {MISSING_FIELD_TEXT}"]
    return f"*Sponsorship for {event.get('name')}*\n\n" + "\n".join(bullets)

def _format_logistics(event: Mapping[str, Any]) -> str:
    return f"*Logistics: {event.get('name')}*\n\nParking: {event.get('parking_notes') or MISSING_FIELD_TEXT}\nFood: {event.get('food_info') or MISSING_FIELD_TEXT}"

def _truncate_whatsapp(text: str) -> str:
    if len(text) <= WHATSAPP_CHAR_LIMIT: return text
    return text[:WHATSAPP_CHAR_LIMIT-20] + "... [Reply for more]"
