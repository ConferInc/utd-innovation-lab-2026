"""Improved response builder for Team 4A / Team 4B integration.

Highlights
----------
- Better intent normalization and query fallback
- Handles timing questions more directly
- Supports donation / sponsorship and attire questions
- Better single-event matching with typo-tolerant fuzzy logic
- Supports lightweight natural-language time windows like today, tonight,
  tomorrow, this weekend, and weekday names
- Enforces the 4096-character WhatsApp limit
- Never fabricates missing fields
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from difflib import SequenceMatcher
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from api_client import APIClientError, APIConfig, EventAPIClient


WHATSAPP_CHAR_LIMIT = 4096
MISSING_FIELD_TEXT = "Not listed on the event page"
DEFAULT_LIST_LIMIT = 5
DEFAULT_SEARCH_LIMIT = 8
FETCH_WINDOW_LIMIT = 25

WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

FIELD_KEYWORDS = {
    "timing": {
        "time", "timings", "timing", "when", "start", "starts", "schedule",
    },
    "attire": {"attire", "dress code", "dresscode", "wear", "clothes", "dress"},
    "sponsorship": {
        "donation", "donate", "donations", "sponsorship", "sponsor", "seva", "tiers", "tier"
    },
    "logistics": {"parking", "logistics", "food", "travel", "transport", "venue", "location"},
}

STOPWORDS = {
    "what", "whats", "what's", "is", "are", "the", "a", "an", "for", "of", "to", "at",
    "on", "in", "there", "anything", "happening", "happens", "tell", "me", "about", "please",
    "tonight", "today", "tomorrow", "this", "weekend", "event", "events", "timings", "timing",
    "time", "when", "donation", "donations", "donate", "attire", "parking", "logistics", "food",
    "tier", "tiers", "sponsorship", "sponsor", "seva", "info", "information", "details",
}


@dataclass(frozen=True)
class TimeWindow:
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    label: Optional[str] = None
    target_time: Optional[time] = None


def build_response(classified_intent: dict, session_context: dict) -> str:
    classified_intent = classified_intent or {}
    session_context = session_context or {}

    client = _get_api_client(session_context)
    intent = _resolve_intent(classified_intent, session_context)
    event_id = _resolve_event_id(classified_intent, session_context)
    query = _resolve_query(classified_intent, session_context)
    requested_field = _resolve_requested_field(classified_intent, query)
    time_window = _resolve_time_window(classified_intent, query)

    try:
        if requested_field == "sponsorship" and intent not in {"sponsorship", "sponsorship_tiers"}:
            intent = "sponsorship"
        elif requested_field == "logistics" and intent not in {"logistics", "parking", "logistics_parking"}:
            intent = "logistics"
        elif requested_field in {"timing", "attire"} and intent == "event_list":
            intent = "single_event_detail"

        if intent in {"today_events", "recurring_events"}:
            return _truncate_whatsapp(_build_filtered_list_response(client, intent=intent, query=query, time_window=time_window))

        if intent in {"event_list", "event_search"}:
            return _truncate_whatsapp(_build_filtered_list_response(client, intent=intent, query=query, time_window=time_window))

        if intent in {"single_event_detail", "event_detail"}:
            event = _resolve_single_event(client, event_id=event_id, query=query)
            if event is None:
                # For a query like "what's happening this weekend", listing is more useful.
                if time_window.start or time_window.end:
                    return _truncate_whatsapp(_build_filtered_list_response(client, intent="event_list", query=query, time_window=time_window))
                return _format_no_results(query or "your request")
            return _truncate_whatsapp(_format_detail_answer(event, requested_field=requested_field))

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

        event = _resolve_single_event(client, event_id=event_id, query=query)
        if event is not None:
            return _truncate_whatsapp(_format_detail_answer(event, requested_field=requested_field))

        return _truncate_whatsapp(_build_filtered_list_response(client, intent="event_list", query=query, time_window=time_window))

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

    default_config = APIConfig()
    config = APIConfig(
        base_url=base_url or default_config.base_url,
        events_base_path=default_config.events_base_path,
        timeout_seconds=default_config.timeout_seconds,
        bearer_token=bearer_token or default_config.bearer_token,
    )
    return EventAPIClient(config=config, headers=headers)


def _resolve_intent(classified_intent: Mapping[str, Any], session_context: Mapping[str, Any]) -> str:
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
    normalized = aliases.get(raw_intent, raw_intent)
    if normalized:
        return normalized

    query = _resolve_query(classified_intent, session_context) or ""
    lowered = query.lower()
    if any(keyword in lowered for keyword in ("today", "tonight", "this weekend", "tomorrow")):
        return "event_list"
    if _resolve_requested_field(classified_intent, query) in {"timing", "attire"}:
        return "single_event_detail"
    if _looks_like_single_event_query(query):
        return "single_event_detail"
    return "event_list"


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


def _resolve_requested_field(classified_intent: Mapping[str, Any], query: Optional[str]) -> Optional[str]:
    explicit = str(classified_intent.get("requested_field", "")).strip().lower()
    if explicit in {"timing", "attire", "sponsorship", "logistics"}:
        return explicit

    if not query:
        return None
    lowered = query.lower()
    for field_name, keywords in FIELD_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return field_name
    return None


def _looks_like_single_event_query(query: Optional[str]) -> bool:
    if not query:
        return False
    words = [word for word in re.findall(r"[a-zA-Z0-9']+", query.lower()) if word not in STOPWORDS]
    # Two or more meaningful words usually indicates an event name or phrase.
    return len(words) >= 2


def _resolve_time_window(classified_intent: Mapping[str, Any], query: Optional[str]) -> TimeWindow:
    today = datetime.now()

    start_raw = classified_intent.get("start_datetime")
    end_raw = classified_intent.get("end_datetime")
    if start_raw or end_raw:
        return TimeWindow(
            start=_parse_iso_datetime(start_raw),
            end=_parse_iso_datetime(end_raw),
            label="requested time",
        )

    if not query:
        return TimeWindow()

    lowered = query.lower()
    target_time = _extract_clock_time(lowered)

    if "today" in lowered:
        start = datetime.combine(today.date(), time.min)
        end = datetime.combine(today.date(), time.max)
        label = "today"
    elif "tonight" in lowered:
        start = datetime.combine(today.date(), time(18, 0))
        end = datetime.combine(today.date(), time.max)
        label = "tonight"
    elif "tomorrow" in lowered:
        target_date = today.date() + timedelta(days=1)
        start = datetime.combine(target_date, time.min)
        end = datetime.combine(target_date, time.max)
        label = "tomorrow"
    elif "this weekend" in lowered or "weekend" in lowered:
        start, end = _weekend_bounds(today)
        label = "this weekend"
    else:
        weekday_date = _extract_weekday_date(lowered, today.date())
        if weekday_date:
            start = datetime.combine(weekday_date, time.min)
            end = datetime.combine(weekday_date, time.max)
            label = weekday_date.strftime("%A")
        else:
            start = end = None
            label = None

    return TimeWindow(start=start, end=end, label=label, target_time=target_time)


def _weekend_bounds(reference: datetime) -> Tuple[datetime, datetime]:
    weekday = reference.weekday()
    days_until_saturday = (5 - weekday) % 7
    saturday = reference.date() + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return datetime.combine(saturday, time.min), datetime.combine(sunday, time.max)


def _extract_weekday_date(query: str, reference_date: date) -> Optional[date]:
    for weekday_name, weekday_num in WEEKDAY_INDEX.items():
        if weekday_name in query:
            delta = (weekday_num - reference_date.weekday()) % 7
            return reference_date + timedelta(days=delta)
    return None


def _extract_clock_time(query: str) -> Optional[time]:
    match = re.search(r"\b(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*(am|pm)\b", query)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = match.group(3)
        if meridiem == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = hour if hour == 12 else hour + 12
        return time(hour, minute)

    match_24 = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", query)
    if match_24:
        return time(int(match_24.group(1)), int(match_24.group(2)))
    return None


def _build_filtered_list_response(
    client: EventAPIClient,
    *,
    intent: str,
    query: Optional[str],
    time_window: TimeWindow,
) -> str:
    if intent == "today_events":
        events = client.get_today_items()
        heading = "today"
    elif intent == "recurring_events":
        events = client.get_recurring_items()
        heading = "recurring events"
    elif query and _should_use_search(query, time_window):
        search_query = _query_without_field_words(query)
        events = client.search_event_items(search_query or query, limit=DEFAULT_SEARCH_LIMIT)
        heading = search_query or query
    else:
        events = client.list_upcoming_events(limit=FETCH_WINDOW_LIMIT)
        heading = time_window.label or "upcoming events"

    filtered_events = _apply_time_window(events, time_window)
    if not filtered_events and query and intent != "event_list":
        filtered_events = _apply_time_window(client.search_event_items(_query_without_field_words(query) or query, limit=DEFAULT_SEARCH_LIMIT), time_window)

    if not filtered_events:
        return _format_no_results(heading)

    for count in range(min(DEFAULT_LIST_LIMIT, len(filtered_events)), 0, -1):
        candidate = _format_event_list(filtered_events[:count], heading)
        if len(candidate) <= WHATSAPP_CHAR_LIMIT:
            return candidate
    return _truncate_whatsapp(_format_event_list(filtered_events[:1], heading))


def _should_use_search(query: str, time_window: TimeWindow) -> bool:
    stripped = _query_without_field_words(query)
    if not stripped:
        return False
    # If the phrase is mostly an event name, use search.
    return _looks_like_single_event_query(stripped) and not (time_window.start or time_window.end)


def _apply_time_window(events: Sequence[Mapping[str, Any]], time_window: TimeWindow) -> List[Dict[str, Any]]:
    if not events:
        return []

    if not time_window.start and not time_window.end and not time_window.target_time:
        return [dict(event) for event in events]

    filtered: List[Dict[str, Any]] = []
    for event in events:
        start_dt = _parse_iso_datetime(event.get("start_datetime"))
        end_dt = _parse_iso_datetime(event.get("end_datetime")) or start_dt
        if start_dt is None:
            continue

        within_window = True
        if time_window.start and start_dt < time_window.start and (end_dt is None or end_dt < time_window.start):
            within_window = False
        if time_window.end and start_dt > time_window.end:
            within_window = False

        if within_window and time_window.target_time:
            event_start_time = start_dt.time()
            latest_allowed = (datetime.combine(date.today(), time_window.target_time) + timedelta(hours=2)).time()
            target_minutes = time_window.target_time.hour * 60 + time_window.target_time.minute
            event_minutes = event_start_time.hour * 60 + event_start_time.minute
            within_window = abs(event_minutes - target_minutes) <= 120
            # Also allow events spanning the requested time.
            if not within_window and end_dt is not None:
                end_minutes = end_dt.time().hour * 60 + end_dt.time().minute
                within_window = event_minutes <= target_minutes <= end_minutes

        if within_window:
            filtered.append(dict(event))

    filtered.sort(key=lambda item: _parse_iso_datetime(item.get("start_datetime")) or datetime.max)
    return filtered


def _resolve_single_event(
    client: EventAPIClient,
    *,
    event_id: Optional[int],
    query: Optional[str],
) -> Optional[Dict[str, Any]]:
    if event_id is not None:
        payload = client.get_event_by_id(event_id)
        event = client.extract_event(payload)
        if event:
            return event

    cleaned_query = _query_without_field_words(query or "")
    if not cleaned_query:
        return None

    events = client.search_event_items(cleaned_query, limit=DEFAULT_SEARCH_LIMIT)
    if not events:
        # Fall back to broad list matching if search is weak.
        broad_events = client.list_upcoming_events(limit=FETCH_WINDOW_LIMIT)
        return _pick_best_event(broad_events, cleaned_query)

    exact_match = _find_exact_name_match(events, cleaned_query)
    if exact_match is not None:
        return exact_match

    return _pick_best_event(events, cleaned_query)


def _pick_best_event(events: Sequence[Mapping[str, Any]], query: str) -> Optional[Dict[str, Any]]:
    normalized_query = _normalize_text(query)
    if not normalized_query:
        return None

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for event in events:
        event_dict = dict(event)
        name = str(event.get("name") or "")
        subtitle = str(event.get("subtitle") or "")
        haystack = _normalize_text(f"{name} {subtitle}")
        if not haystack:
            continue

        exact_bonus = 0.2 if haystack == normalized_query else 0.0
        contains_bonus = 0.15 if normalized_query in haystack or haystack in normalized_query else 0.0
        score = SequenceMatcher(None, normalized_query, haystack).ratio() + exact_bonus + contains_bonus
        scored.append((score, event_dict))

    if not scored:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_event = scored[0]
    return best_event if best_score >= 0.45 else None


def _find_exact_name_match(events: Sequence[Mapping[str, Any]], query: str) -> Optional[Dict[str, Any]]:
    normalized_query = _normalize_text(query)
    for event in events:
        name = _normalize_text(str(event.get("name") or ""))
        if name == normalized_query:
            return dict(event)
    return None


def _normalize_text(value: str) -> str:
    text = value.lower().replace("sutsang", "satsang")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _query_without_field_words(query: str) -> str:
    if not query:
        return ""
    cleaned = query.lower().replace("sutsang", "satsang")
    for keyword_group in FIELD_KEYWORDS.values():
        for keyword in sorted(keyword_group, key=len, reverse=True):
            cleaned = re.sub(rf"\b{re.escape(keyword)}\b", " ", cleaned)
    for filler in [
        "what's", "whats", "what", "when", "tell me about", "tell me", "about", "is there", "anything",
        "happening", "happens", "this weekend", "weekend", "today", "tonight", "tomorrow", "at",
        "for", "the", "event", "please",
    ]:
        cleaned = cleaned.replace(filler, " ")
    cleaned = re.sub(r"\b(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*(am|pm)\b", " ", cleaned)
    cleaned = re.sub(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _format_detail_answer(event: Mapping[str, Any], *, requested_field: Optional[str]) -> str:
    if requested_field == "timing":
        return _format_timing_only(event)
    if requested_field == "attire":
        return _format_attire(event)
    return _format_single_event(event)


def _format_timing_only(event: Mapping[str, Any]) -> str:
    return (
        f"*{_value_or_missing(event.get('name'))}*\n\n"
        f"When: {_format_date_time_plain(event)}\n"
        f"Where: {_format_short_location_text(event)}"
    )


def _format_attire(event: Mapping[str, Any]) -> str:
    attire_value = (
        event.get("attire")
        or event.get("dress_code")
        or event.get("attire_notes")
        or event.get("notes")
    )
    attire_text = _value_or_blank(attire_value)
    if not attire_text:
        attire_text = MISSING_FIELD_TEXT
    return (
        f"*Attire for {_value_or_missing(event.get('name'))}*\n\n"
        f"Attire: {attire_text}\n"
        f"When: {_format_date_time_plain(event)}\n"
        f"Where: {_format_short_location_text(event)}"
    )


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

    lines = [f"*{_value_or_missing(event.get('name'))}*"]
    if subtitle_line:
        lines.append(subtitle_line)
    lines.extend([
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
    ])
    return "\n".join(lines).strip()


def _format_event_list(events: Sequence[Mapping[str, Any]], query: str) -> str:
    lines = [f"Here are the events I found for *{query}*:", ""]
    for index, event in enumerate(events, start=1):
        lines.append(f"{index}) *{_value_or_missing(event.get('name'))}*")
        lines.append(f"   {_format_short_date_time(event)}")
        lines.append(f"   {_format_short_location(event)}")
        lines.append("")
    lines.extend([
        "Reply with:",
        "- 1, 2, or 3 for full details",
        "- timings for event time",
        "- logistics for parking, food, or travel info",
        "- sponsorship for donation, seva, or sponsorship options",
    ])
    return "\n".join(lines).strip()


def _format_no_results(query: str) -> str:
    return (
        f"I could not find any matching events for *{query}* right now.\n\n"
        "You can try:\n"
        "- an event name (example: *Holi*, *retreat*, *family camp*)\n"
        "- a day or time (example: *Sunday*, *this weekend*, *tonight*)\n"
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
        f"*Sponsorship / Donation Information for {_value_or_missing(event.get('name'))}*",
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
    return f"When: {_format_date_time_plain(event)}"


def _format_date_time_plain(event: Mapping[str, Any]) -> str:
    start = _parse_iso_datetime(event.get("start_datetime"))
    end = _parse_iso_datetime(event.get("end_datetime"))
    timezone = _value_or_blank(event.get("timezone"))

    if start is None and end is None:
        return MISSING_FIELD_TEXT
    if start is not None and end is not None:
        start_text = start.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        end_text = end.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        return f"{start_text} to {end_text}{_prefix_space(timezone)}"
    dt = start or end
    assert dt is not None
    return f"{dt.strftime('%b %d, %Y %I:%M %p').replace(' 0', ' ')}{_prefix_space(timezone)}"


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
    return f"Where: {_format_short_location_text(event)}"


def _format_short_location_text(event: Mapping[str, Any]) -> str:
    short = _value_or_blank(event.get("location_name")) or _city_state_postal(event)
    return short or MISSING_FIELD_TEXT


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
            pieces.append(f"${int(amount_number)}" if amount_number.is_integer() else f"${amount_number:.2f}")
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
    return str(value).strip()


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
