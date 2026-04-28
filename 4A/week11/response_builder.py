"""Response builder for Team 4A / Team 4B integration.

build_response(classified_intent: dict, session_context: dict) -> str
- Calls Team 4B event API through api_client.py
- Formats the response using Week 7 WhatsApp templates
- Enforces the 4096-character WhatsApp limit
- Never fabricates missing fields
- Uses "Not listed on the event page" when a requested field is unavailable
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from api_client import (
    APIClientError,
    APIConfig,
    EventAPIClient,
)

try:
    from schedule import get_current_schedule
except Exception:
    get_current_schedule = None


WHATSAPP_CHAR_LIMIT = 4096
MISSING_FIELD_TEXT = "Not listed on the event page"
DEFAULT_LIST_LIMIT = 5
DEFAULT_SEARCH_LIMIT = 5


def build_response(classified_intent: dict, session_context: dict) -> str:
    """Build the final WhatsApp response for the user.

    Parameters
    ----------
    classified_intent:
        Expected to contain the detected intent and any extracted entities such as
        query text, event_id, or flags like today/recurring.

    session_context:
        Conversation state such as selected_event_id or an already constructed
        EventAPIClient under session_context["api_client"].

    Returns
    -------
    str
        WhatsApp-safe response text.
    """
    classified_intent = classified_intent or {}
    session_context = session_context or {}

    client = _get_api_client(session_context)
    intent = _resolve_intent(classified_intent)
    event_id = _resolve_event_id(classified_intent, session_context)
    query = _resolve_query(classified_intent, session_context)

    try:
        if intent == "recurring_schedule":
            if get_current_schedule is not None:
                active_programs = get_current_schedule()
                return _truncate_whatsapp(_format_active_recurring_schedule(active_programs))

            return _build_event_list_response(client, intent="recurring_events", query=query)

        if intent in {"event_list", "event_search", "today_events", "recurring_events"}:
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

        # Fallback:
        event = _resolve_single_event(client, event_id=event_id, query=query)
        if event is not None:
            return _truncate_whatsapp(_format_single_event(event))

        return _truncate_whatsapp(_build_event_list_response(client, intent="event_list", query=query))

    except APIClientError:
        return (
            "I could not retrieve event information right now. "
            "Please try again in a moment."
        )
    except Exception:
        return (
            "I ran into an issue while building the event response. "
            "Please try again."
        )


def _get_api_client(session_context: Mapping[str, Any]) -> EventAPIClient:
    existing = session_context.get("api_client")
    if isinstance(existing, EventAPIClient):
        return existing

    base_url = session_context.get("api_base_url")
    bearer_token = session_context.get("api_bearer_token")
    headers = session_context.get("api_headers")

    config = APIConfig(
        base_url=base_url or APIConfig().base_url,
        events_base_path=APIConfig().events_base_path,
        timeout_seconds=APIConfig().timeout_seconds,
        bearer_token=bearer_token or APIConfig().bearer_token,
    )
    return EventAPIClient(config=config, headers=headers)


def _resolve_intent(classified_intent: Mapping[str, Any]) -> str:
    raw_intent = str(classified_intent.get("intent", "")).strip().lower()

    aliases = {
        "event_list": "event_list",
        "events_list": "event_list",
        "list_events": "event_list",
        "upcoming_events": "event_list",
        "event_query": "event_list",
        "today": "today_events",
        "today_events": "today_events",
        "events_today": "today_events",
        "recurring_schedule": "recurring_schedule",
        "weekly_schedule": "recurring_schedule",
        "current_schedule": "recurring_schedule",
        "temple_schedule": "recurring_schedule",
        "recurring": "recurring_events",
        "recurring_events": "recurring_events",
        "event_detail": "single_event_detail",
        "single_event_detail": "single_event_detail",
        "single_event": "single_event_detail",
        "details": "single_event_detail",
        "event_search": "event_search",
        "search": "event_search",
        "sponsorship": "sponsorship",
        "sponsorship_tiers": "sponsorship",
        "logistics": "logistics",
        "parking": "logistics",
        "logistics_parking": "logistics",
    }
    return aliases.get(raw_intent, raw_intent or "event_list")


def _resolve_query(classified_intent: Mapping[str, Any], session_context: Mapping[str, Any]) -> Optional[str]:
    candidates: Iterable[Any] = (
        classified_intent.get("query"),
        classified_intent.get("event_name"),
        classified_intent.get("entity"),
        classified_intent.get("keyword"),
        session_context.get("last_query"),
    )
    for value in candidates:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _resolve_event_id(classified_intent: Mapping[str, Any], session_context: Mapping[str, Any]) -> Optional[int]:
    candidates = [
        classified_intent.get("event_id"),
        classified_intent.get("id"),
        session_context.get("selected_event_id"),
        session_context.get("event_id"),
    ]
    for value in candidates:
        parsed = _coerce_int(value)
        if parsed is not None:
            return parsed
    return None


def _coerce_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _build_event_list_response(client: EventAPIClient, *, intent: str, query: Optional[str]) -> str:
    if intent == "today_events":
        payload = client.get_today()
        heading_query = "today"
    elif intent == "recurring_events":
        payload = client.get_recurring()
        heading_query = "recurring events"
    elif query:
        payload = client.search_events(query, limit=DEFAULT_SEARCH_LIMIT, offset=0)
        heading_query = query
    else:
        payload = client.get_events(limit=DEFAULT_LIST_LIMIT, offset=0)
        heading_query = "upcoming events"

    events = _extract_events(payload)
    if not events:
        return _format_no_results(heading_query)

    # Cap to 5 and trim to stay under WhatsApp size.
    for count in range(min(5, len(events)), 0, -1):
        candidate = _format_event_list(events[:count], heading_query)
        if len(candidate) <= WHATSAPP_CHAR_LIMIT:
            return candidate

    return _truncate_whatsapp(_format_event_list(events[:1], heading_query))


def _resolve_single_event(
    client: EventAPIClient,
    *,
    event_id: Optional[int],
    query: Optional[str],
) -> Optional[Dict[str, Any]]:
    if event_id is not None:
        try:
            payload = client.get_event_by_id(event_id)
            wrapped_event = payload.get("event")
            if isinstance(wrapped_event, dict):
                return dict(wrapped_event)
            return payload
        except APIClientError:
            raise

    if not query:
        return None

    search_payload = client.search_events(query, limit=DEFAULT_SEARCH_LIMIT, offset=0)
    events = _extract_events(search_payload)
    if not events:
        return None

    exact_match = _find_exact_name_match(events, query)
    if exact_match is not None:
        return exact_match

    if len(events) == 1:
        return events[0]

    # If multiple search results exist and none is exact, use the first result.
    return events[0]


def _extract_events(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    events = payload.get("events")
    if isinstance(events, list):
        return [event for event in events if isinstance(event, dict)]
    return []


def _find_exact_name_match(events: Sequence[Mapping[str, Any]], query: str) -> Optional[Dict[str, Any]]:
    normalized_query = " ".join(query.lower().split())
    for event in events:
        name = str(event.get("name") or "").strip().lower()
        if name == normalized_query:
            return dict(event)
    return None


def _format_active_recurring_schedule(active_programs: Any) -> str:
    if not isinstance(active_programs, Sequence) or isinstance(active_programs, (str, bytes)):
        active_programs = []

    programs = [str(program).strip() for program in active_programs if str(program).strip()]
    if not programs:
        return "There are no recurring temple programs currently active right now."

    lines = [
        "*Currently active temple programs:*",
        "",
    ]
    lines.extend(f"- {program}" for program in programs)
    return "\n".join(lines).strip()


def _format_single_event(event: Mapping[str, Any]) -> str:
    subtitle_line = _value_or_blank(event.get("subtitle"))
    date_time_text = _format_date_time(event)
    location_text = _format_location(event)
    description_short = _value_or_missing(event.get("description"))
    price_line = f"Price: {_format_price(event.get('price'))}"
    food_line = f"Food: {_value_or_missing(event.get('food_info'))}"
    parking_line = f"Parking: {_value_or_missing(event.get('parking_notes'))}"
    registration_line = f"Registration: {_format_registration(event)}"
    contact_line = f"Contact: {_format_contact(event)}"
    source_url = _value_or_missing(event.get("source_url"))

    lines = [
        f"*{_value_or_missing(event.get('name'))}*",
    ]
    if subtitle_line:
        lines.append(subtitle_line)
    lines.extend(
        [
            "",
            date_time_text,
            location_text,
            "",
            description_short,
            "",
            price_line,
            food_line,
            parking_line,
            registration_line,
            "",
            contact_line,
            f"More info: {source_url}",
        ]
    )
    return "\n".join(lines).strip()


def _format_event_list(events: Sequence[Mapping[str, Any]], query: str) -> str:
    lines = [f"Here are the events I found for *{query}*:", ""]
    for index, event in enumerate(events, start=1):
        lines.append(f"{index}) *{_value_or_missing(event.get('name'))}*")
        lines.append(f"   {_format_short_date_time(event)}")
        lines.append(f"   {_format_short_location(event)}")
        lines.append("")
    lines.extend(
        [
            "Reply with:",
            "- 1, 2, or 3 for full details",
            "- logistics for parking, food, or travel info",
            "- sponsorship for seva or sponsorship options",
        ]
    )
    return "\n".join(lines).strip()


def _format_no_results(query: str) -> str:
    return (
        f"I could not find any matching events for *{query}* right now.\n\n"
        "You can try:\n"
        "- an event name (example: *Holi*, *retreat*, *family camp*)\n"
        "- a month or date\n"
        "- a category like *festival*, *weekly satsang*, or *youth*\n\n"
        "If you want, I can also show the latest upcoming events."
    )


def _format_sponsorship(event: Mapping[str, Any]) -> str:
    tiers = event.get("sponsorship_tiers")
    bullets: List[str] = []

    if isinstance(tiers, list) and tiers:
        for tier in tiers:
            if not isinstance(tier, Mapping):
                continue
            tier_name = _value_or_missing(tier.get("tier_name"))
            price = _format_sponsorship_price(tier.get("price"))
            description = _value_or_missing(tier.get("description"))
            bullet = f"- {tier_name} — {price}"
            if description != MISSING_FIELD_TEXT:
                bullet += f" ({description})"
            bullets.append(bullet)

    if not bullets:
        bullets = [f"- {MISSING_FIELD_TEXT}"]

    lines = [
        f"*Sponsorship / Seva Information for {_value_or_missing(event.get('name'))}*",
        "",
        "Available options:",
        *bullets,
        "",
        "If you want, I can also help with:",
        "- event dates and venue",
        "- food details",
        "- registration / contact information",
    ]
    return "\n".join(lines).strip()


def _format_logistics(event: Mapping[str, Any]) -> str:
    lines = [
        f"*Logistics for {_value_or_missing(event.get('name'))}*",
        "",
        f"Venue: {_format_location(event)}",
        f"Parking: {_value_or_missing(event.get('parking_notes'))}",
        f"Food: {_value_or_missing(event.get('food_info'))}",
        f"Transportation: {_value_or_missing(event.get('transportation_notes'))}",
        "",
        f"Registration: {_format_registration(event)}",
        f"Contact: {_format_contact(event)}",
        f"More info: {_value_or_missing(event.get('source_url'))}",
    ]
    return "\n".join(lines).strip()


def _format_date_time(event: Mapping[str, Any]) -> str:
    start = _parse_iso_datetime(event.get("start_datetime"))
    end = _parse_iso_datetime(event.get("end_datetime"))
    timezone = _value_or_blank(event.get("timezone"))

    if start is None and end is None:
        return f"When: {MISSING_FIELD_TEXT}"

    if start is not None and end is not None:
        start_text = start.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        end_text = end.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        return f"When: {start_text} to {end_text}{_prefix_space(timezone)}"

    dt = start or end
    assert dt is not None
    return f"When: {dt.strftime('%b %d, %Y %I:%M %p').replace(' 0', ' ')}{_prefix_space(timezone)}"


def _format_short_date_time(event: Mapping[str, Any]) -> str:
    start = _parse_iso_datetime(event.get("start_datetime"))
    timezone = _value_or_blank(event.get("timezone"))
    if start is None:
        return f"When: {MISSING_FIELD_TEXT}"
    return f"When: {start.strftime('%b %d, %I:%M %p').replace(' 0', ' ')}{_prefix_space(timezone)}"


def _format_location(event: Mapping[str, Any]) -> str:
    parts = [
        _value_or_blank(event.get("location_name")),
        _value_or_blank(event.get("address")),
        _value_or_blank(_city_state_postal(event)),
        _value_or_blank(event.get("country")),
    ]
    location = ", ".join(part for part in parts if part)
    return location or MISSING_FIELD_TEXT


def _format_short_location(event: Mapping[str, Any]) -> str:
    short = _value_or_blank(event.get("location_name")) or _city_state_postal(event)
    return f"Where: {short or MISSING_FIELD_TEXT}"


def _city_state_postal(event: Mapping[str, Any]) -> str:
    parts = [
        _value_or_blank(event.get("city")),
        _value_or_blank(event.get("state")),
        _value_or_blank(event.get("postal_code")),
    ]
    return ", ".join(part for part in parts if part)


def _format_registration(event: Mapping[str, Any]) -> str:
    status = _value_or_blank(event.get("registration_status"))
    required = event.get("registration_required")
    url = _value_or_blank(event.get("registration_url"))

    details: List[str] = []
    if isinstance(required, bool):
        details.append("Required" if required else "Not required")
    if status:
        details.append(status.capitalize())
    if url:
        details.append(url)

    return " | ".join(details) if details else MISSING_FIELD_TEXT


def _format_contact(event: Mapping[str, Any]) -> str:
    contact_parts = [
        _value_or_blank(event.get("contact_email")),
        _value_or_blank(event.get("contact_phone")),
    ]
    contact = " | ".join(part for part in contact_parts if part)
    return contact or MISSING_FIELD_TEXT


def _format_price(price_value: Any) -> str:
    if not isinstance(price_value, Mapping):
        return MISSING_FIELD_TEXT

    amount = price_value.get("amount")
    notes = _value_or_blank(price_value.get("notes"))

    pieces: List[str] = []
    if amount is not None:
        try:
            amount_number = float(amount)
            if amount_number.is_integer():
                pieces.append(f"${int(amount_number)}")
            else:
                pieces.append(f"${amount_number:.2f}")
        except (TypeError, ValueError):
            pieces.append(str(amount))
    if notes:
        pieces.append(notes)

    return " | ".join(pieces) if pieces else MISSING_FIELD_TEXT


def _format_sponsorship_price(value: Any) -> str:
    if value is None or value == "":
        return MISSING_FIELD_TEXT
    try:
        number = float(value)
        return f"${int(number)}" if number.is_integer() else f"${number:.2f}"
    except (TypeError, ValueError):
        return str(value).strip() or MISSING_FIELD_TEXT


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _value_or_blank(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text


def _value_or_missing(value: Any) -> str:
    text = _value_or_blank(value)
    return text if text else MISSING_FIELD_TEXT


def _prefix_space(value: str) -> str:
    return f" {value}" if value else ""


def _truncate_whatsapp(text: str, limit: int = WHATSAPP_CHAR_LIMIT) -> str:
    if len(text) <= limit:
        return text
    ellipsis = "... [truncated]"
    if limit <= len(ellipsis):
        return ellipsis[:limit]
    return text[: limit - len(ellipsis)].rstrip() + ellipsis
