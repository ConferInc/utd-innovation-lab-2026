"""Response builder for Team 4A / Team 4B integration.

build_response(classified_intent: dict, session_context: dict) -> str
- Calls Team 4B event API through api_client.py
- Formats the response using Week 7 WhatsApp templates
- Enforces the 4096-character WhatsApp limit
- Never fabricates missing fields
- Uses "Not listed on the event page" when a requested field is unavailable
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from api_client import (
    APIClientError,
    APIConfig,
    EventAPIClient,
)

# Week 12 fix (Bug 1): Wire the canonical recurring_handler module.
# Previous code did `from schedule import get_current_schedule` which resolved
# to nothing (no `schedule.py` exists; `schedule-2.py` cannot be imported as
# `schedule` because of the hyphen, and itself imports a non-existent
# `schedule_data` module). The silent ImportError left `get_current_schedule`
# as None, so every `recurring_schedule` intent fell through to the empty
# Team 4B `/recurring` endpoint.
try:
    from recurring_handler import (
        get_current_schedule,
        get_next_occurrence,
        get_full_day_schedule,
        TIMEZONE as _SCHEDULE_TZ,
    )
except Exception:  # pragma: no cover — safety net only
    get_current_schedule = None
    get_next_occurrence = None
    get_full_day_schedule = None
    _SCHEDULE_TZ = None


# Canonical program names (lowercase) recognised by the local recurring handler.
RECURRING_PROGRAM_ALIASES: Dict[str, str] = {
    "darshan": "darshan",
    "darshana": "darshan",
    "aarti": "aarti",
    "arati": "aarti",
    "bhog": "bhog",
    "satsang": "satsang",
    "sunday satsang": "satsang",
    "kirtan": "bhajans",
    "kirtans": "bhajans",
    "bhajan": "bhajans",
    "bhajans": "bhajans",
    "daily bhajans": "bhajans",
    "mahaprasad": "mahaprasad",
    "prasad": "mahaprasad",
}


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
            # Week 12 fix (Bug 1): Use the local recurring handler. The Team 4B
            # `/recurring` endpoint returns an empty list for these temple
            # programs because they are not scraped — they are static data
            # owned by the bot.
            if get_current_schedule is not None:
                program_hint = _resolve_recurring_program(classified_intent, query)
                return _truncate_whatsapp(
                    _format_recurring_response(program_hint=program_hint)
                )
            # Fallback only if the local module failed to import.
            return _build_event_list_response(client, intent="recurring_events", query=query)

        if intent in {"event_list", "event_search", "today_events", "recurring_events"}:
            return _build_event_list_response(client, intent=intent, query=query)

        if intent == "time_based":
            # Bugfix (post-Week-12 audit, B1+B6): the previous code dropped
            # `time_based` into the generic fallback, which calls
            # `client.get_events()` with no filter and shows the same generic
            # upcoming list for "tomorrow", "this weekend", "at 3am tonight",
            # etc. Now we resolve the timeframe entity into a (start, end)
            # date pair and let `_build_event_list_response` filter the API
            # response client-side. The API doesn't honour `start_date=…` so
            # this is where filtering actually happens.
            timeframe = _resolve_timeframe(classified_intent)
            if timeframe == "today" or timeframe == "tonight":
                return _build_event_list_response(client, intent="today_events", query=query)
            date_range = _date_range_for_timeframe(timeframe)
            return _build_event_list_response(
                client,
                intent="event_list",
                query=query,
                date_filter=date_range,
                heading_override=_format_timeframe_heading(timeframe),
            )

        if intent == "discovery":
            # Bugfix (post-Week-12 audit, B12): give discovery an explicit
            # branch so it picks up the same past-event filter as the rest.
            return _build_event_list_response(client, intent="event_list", query=query)

        if intent in {"single_event_detail", "event_detail"}:
            # Week 12 fix (Bug 2): use raw-message fallback so "Tell me about
            # the Bhakti Kirtan Retreat" reaches /search even when the entity
            # extractor's hardcoded EVENT_NAMES list misses it.
            search_term = _search_term_with_message_fallback(query, classified_intent, session_context)
            event = _resolve_single_event(client, event_id=event_id, query=search_term)
            if event is None:
                return _format_no_results(search_term or "your request")
            return _truncate_whatsapp(_format_single_event(event))

        if intent in {"sponsorship", "sponsorship_tiers"}:
            # Week 12 fix (Bug 3): if no event target was extracted, return a
            # generic donation / seva message instead of "no matching events".
            search_term = _search_term_with_message_fallback(query, classified_intent, session_context)
            if not search_term and event_id is None:
                return _truncate_whatsapp(_format_generic_sponsorship())
            event = _resolve_single_event(client, event_id=event_id, query=search_term)
            if event is None:
                return _truncate_whatsapp(_format_generic_sponsorship())
            return _truncate_whatsapp(_format_sponsorship(event))

        if intent in {"logistics", "parking", "logistics_parking"}:
            # Week 12 fix (Bug 2): same raw-message fallback as event_specific.
            search_term = _search_term_with_message_fallback(query, classified_intent, session_context)
            event = _resolve_single_event(client, event_id=event_id, query=search_term)
            if event is None:
                return _format_no_results(search_term or "your request")
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
    """Pull the best search query string out of the classifier output and session.

    Week 12 fix (Bug 2): Previous version only looked at top-level keys on
    `classified_intent`. The intent classifier puts entity-extractor output
    under `classified_intent["entities"]`, so when the entity extractor put
    "Kirtan" into `entities.program_name` (because PROGRAM_NAMES matched it),
    the response builder saw nothing and routed to "no results". This patch
    walks both the top-level keys *and* the nested entities, so program/event
    name extraction in either slot reaches the search endpoint.

    Search priority:
      1. explicit query / event_name / entity / keyword on the classification
      2. nested entities.event_name (most specific)
      3. nested entities.program_name (e.g. recurring program user mentioned
         in a non-recurring context like logistics)
      4. session_context.last_query (carry-over)

    NOTE: This deliberately does NOT fall through to the raw user message,
    because intents like discovery / time_based should never treat the whole
    user sentence as a search term. The raw message is consulted only by
    intents that genuinely need a target (event_specific / logistics /
    sponsorship), via `_search_term_with_message_fallback`.
    """
    entities = classified_intent.get("entities") or {}
    nested_event_name = entities.get("event_name") if isinstance(entities, Mapping) else None
    nested_program_name = entities.get("program_name") if isinstance(entities, Mapping) else None

    candidates: Iterable[Any] = (
        classified_intent.get("query"),
        classified_intent.get("event_name"),
        classified_intent.get("entity"),
        classified_intent.get("keyword"),
        nested_event_name,
        nested_program_name,
        session_context.get("last_query"),
    )
    for value in candidates:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _search_term_with_message_fallback(
    query: Optional[str],
    classified_intent: Mapping[str, Any],
    session_context: Mapping[str, Any],
) -> Optional[str]:
    """Return a search term, falling back to noun-phrase extraction from the
    raw user message when the structured query is empty.

    This is for intents that *require* a target (event_specific, logistics,
    sponsorship of a specific event). It strips common question / filler
    words so that "Where is the Bhakti Kirtan Retreat?" becomes
    "Bhakti Kirtan Retreat" and reaches the search endpoint.
    """
    if query:
        return query
    raw = session_context.get("user_message")
    if not raw:
        return None
    cleaned = _strip_question_words(str(raw))
    return cleaned or None


_QUESTION_WORDS = {
    # Interrogatives + auxiliaries
    "what", "whats", "when", "where", "who", "why", "how", "which",
    "is", "are", "was", "were", "do", "does", "did", "can", "could",
    "should", "would", "will", "the", "a", "an", "to", "for", "of",
    "about", "tell", "me", "more", "info", "details", "please",
    # Common starters / fillers
    "hi", "hello", "hey", "i", "id", "i'd", "want", "need", "looking", "find",
    # Bugfix (post-Week-12 audit, B19 case): "Where is the temple?" used to
    # leak through with a residual "temple" search term and returned the
    # first event in the API. The temple itself is a venue, not an event —
    # strip these venue-only words so that bare venue questions fall to the
    # logistics no-target branch instead of returning a random event.
    "temple", "jkyog", "venue", "place", "located", "directions",
}


def _strip_question_words(text: str) -> str:
    tokens = [t for t in text.lower().replace("?", " ").replace(",", " ").split() if t]
    kept = [t for t in tokens if t not in _QUESTION_WORDS]
    # Recover original casing where possible
    if not kept:
        return ""
    cleaned = " ".join(kept)
    # If everything got stripped (e.g. the message was "info"), bail out
    if len(cleaned) < 2:
        return ""
    return cleaned


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


def _build_event_list_response(
    client: EventAPIClient,
    *,
    intent: str,
    query: Optional[str],
    date_filter: Optional[Tuple[Any, Any]] = None,
    heading_override: Optional[str] = None,
) -> str:
    """Build a list response. Pulls a candidate set from the API based on
    `intent` (and `query` for search), then filters out events whose end
    time is already in the past, then optionally restricts to a date range.

    Bugfix (post-Week-12 audit):
      - B6: the API doesn't honour `?upcoming_only=true`. We pull a wider
        page (limit=20) and filter client-side so the user never sees the
        Seattle LTP in the "upcoming" list on a date after it ended.
      - T5: `date_filter=(start_date, end_date)` lets the time_based handler
        reuse this function for "tomorrow", "this weekend", "May 23rd",
        etc. — the API ignores `start_date=…` so all the filtering happens
        here.
    """
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
        # Pull a wider window so client-side past-event filtering still
        # leaves enough rows to display.
        payload = client.get_events(limit=DEFAULT_LIST_LIMIT * 4, offset=0)
        heading_query = "upcoming events"

    events = _extract_events(payload)

    # Filter out events whose end_datetime has already passed.
    events = _filter_upcoming(events)

    # Optional date-range filter (used by time_based intent).
    if date_filter is not None:
        events = _filter_by_date_range(events, *date_filter)

    if heading_override:
        heading_query = heading_override

    if not events:
        return _format_no_results(heading_query)

    # Cap to 5 and trim to stay under WhatsApp size.
    for count in range(min(5, len(events)), 0, -1):
        candidate = _format_event_list(events[:count], heading_query)
        if len(candidate) <= WHATSAPP_CHAR_LIMIT:
            return candidate

    return _truncate_whatsapp(_format_event_list(events[:1], heading_query))


def _now_ct() -> datetime:
    """Return current time in Central Time (the temple's wall-clock zone).

    Used as the "is this event still relevant?" reference point. Falls back
    to a naive `datetime.now()` if the local timezone module failed to
    import (defensive — should never trigger in production).
    """
    if _SCHEDULE_TZ is not None:
        return datetime.now(_SCHEDULE_TZ)
    return datetime.now()


def _filter_upcoming(events: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Drop events whose end_datetime is already in the past.

    Multi-day events are preserved while at least their end date is in the
    future — e.g. on 2026-05-08 the Seattle LTP (May 4–9) still counts as
    "upcoming" until end-of-day May 9. Events with no end_datetime fall back
    to the start_datetime for this comparison.
    """
    now = _now_ct()
    keep: List[Dict[str, Any]] = []
    for event in events:
        end = _parse_iso_datetime(event.get("end_datetime")) or _parse_iso_datetime(event.get("start_datetime"))
        if end is None:
            # No date info at all — keep it; better to surface than to drop.
            keep.append(dict(event))
            continue
        # Naive datetimes from the API are treated as CT (see B3 bugfix).
        if end.tzinfo is None and _SCHEDULE_TZ is not None:
            end = end.replace(tzinfo=_SCHEDULE_TZ)
        if end >= now:
            keep.append(dict(event))
    return keep


def _resolve_timeframe(classified_intent: Mapping[str, Any]) -> Optional[str]:
    """Pull a timeframe label out of the classifier's entities.

    Accepts either a known label (today/tomorrow/this_weekend/this_week) or
    an ISO date string (the entity extractor's `parsed_date`).
    """
    entities = classified_intent.get("entities") or {}
    if not isinstance(entities, Mapping):
        return None
    value = entities.get("timeframe") or entities.get("parsed_date")
    if value is None:
        return None
    text = str(value).strip().lower()
    return text or None


def _format_timeframe_heading(timeframe: Optional[str]) -> Optional[str]:
    """Pretty-print a timeframe label for the event-list heading.

    Returns None to fall back to the default `upcoming events` heading when
    we can't make a nice phrase.
    """
    if not timeframe:
        return None
    if timeframe == "today" or timeframe == "tonight":
        return "today"
    if timeframe == "tomorrow":
        return "tomorrow"
    if timeframe == "this_weekend":
        return "this weekend"
    if timeframe == "this_week":
        return "this week"
    if timeframe == "next_week":
        return "next week"
    # ISO date — render a friendly form (Windows-safe: strftime("%b %d") then
    # strip any leading zero in the day number)
    try:
        d = date.fromisoformat(timeframe)
        return d.strftime("%b %d").replace(" 0", " ")
    except (TypeError, ValueError):
        return None


def _date_range_for_timeframe(
    timeframe: Optional[str],
) -> Optional[Tuple[Optional[date], Optional[date]]]:
    """Map a timeframe label or YYYY-MM-DD string to a (start, end) date pair.

    Returns None to mean "no filter" (defensive — caller can still fall
    through to the unfiltered upcoming list).

    Mapping rules (today is computed in CT):
      - "today"               → (today, today)              (handled separately by caller via /today endpoint)
      - "tonight"             → (today, today)
      - "tomorrow"            → (tomorrow, tomorrow)
      - "this_weekend"        → (next Saturday, next Sunday) (or today/tomorrow if today is already Sat/Sun)
      - "this_week"           → (today, end of this week, Sunday)
      - "next_week"           → (next Monday, next Sunday)
      - "YYYY-MM-DD"          → (that day, that day)
      - anything else         → None  (let the caller fall through unfiltered)
    """
    if not timeframe:
        return None

    today = _now_ct().date()

    if timeframe in {"today", "tonight"}:
        return (today, today)
    if timeframe == "tomorrow":
        d = today + timedelta(days=1)
        return (d, d)
    if timeframe == "this_weekend":
        # Saturday=5, Sunday=6
        wd = today.weekday()
        if wd >= 5:
            # Already weekend — show today + Sunday.
            sat = today if wd == 5 else today - timedelta(days=1)
            sun = sat + timedelta(days=1)
            return (today, sun)
        days_to_sat = 5 - wd
        sat = today + timedelta(days=days_to_sat)
        sun = sat + timedelta(days=1)
        return (sat, sun)
    if timeframe == "this_week":
        # Today through end-of-week (Sunday).
        wd = today.weekday()
        end = today + timedelta(days=(6 - wd))
        return (today, end)
    if timeframe == "next_week":
        wd = today.weekday()
        days_to_next_mon = (7 - wd) % 7 or 7
        mon = today + timedelta(days=days_to_next_mon)
        sun = mon + timedelta(days=6)
        return (mon, sun)

    # ISO date string e.g. "2026-05-23"
    try:
        parsed = date.fromisoformat(timeframe)
        return (parsed, parsed)
    except (TypeError, ValueError):
        return None


def _filter_by_date_range(
    events: Sequence[Mapping[str, Any]],
    range_start,
    range_end,
) -> List[Dict[str, Any]]:
    """Keep events whose [start, end] overlaps the [range_start, range_end] window.

    `range_start` and `range_end` are `date` (or naive `datetime`) objects in
    Central Time. Used for "tomorrow", "this weekend", a specific date,
    etc. — the API does not honour `start_date=` query params, so this is
    where the filtering actually happens.
    """
    if range_start is None and range_end is None:
        return [dict(e) for e in events]

    keep: List[Dict[str, Any]] = []
    for event in events:
        start_dt = _parse_iso_datetime(event.get("start_datetime"))
        end_dt = _parse_iso_datetime(event.get("end_datetime")) or start_dt
        if start_dt is None:
            continue
        start_d = start_dt.date()
        end_d = (end_dt or start_dt).date()
        # Inclusive overlap test on dates.
        if range_end is not None and start_d > range_end:
            continue
        if range_start is not None and end_d < range_start:
            continue
        keep.append(dict(event))
    return keep


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


def _resolve_recurring_program(
    classified_intent: Mapping[str, Any], query: Optional[str],
) -> Optional[str]:
    """Best-effort match of the user's recurring-program request to a canonical key.

    Looks at:
    1. classified_intent.entities.program_name (entity extractor's output)
    2. classified_intent.entities.event_name (in case it landed there instead)
    3. The query string / user message text

    Returns one of the canonical lowercase program keys understood by
    recurring_handler.SCHEDULE (darshan, aarti, bhog, satsang, bhajans,
    mahaprasad), or None if nothing matched.
    """
    candidates: List[str] = []

    entities = classified_intent.get("entities") or {}
    if isinstance(entities, Mapping):
        for key in ("program_name", "event_name"):
            value = entities.get(key)
            if value:
                candidates.append(str(value).strip().lower())

    if query:
        candidates.append(str(query).strip().lower())

    for candidate in candidates:
        if not candidate:
            continue
        # Exact alias hit
        if candidate in RECURRING_PROGRAM_ALIASES:
            return RECURRING_PROGRAM_ALIASES[candidate]
        # Substring match — handles "Bhakti Kirtans & Satsang" → satsang
        for alias, canonical in RECURRING_PROGRAM_ALIASES.items():
            if alias in candidate:
                return canonical
    return None


def _format_recurring_response(*, program_hint: Optional[str] = None) -> str:
    """Build the WhatsApp text for a recurring_schedule intent.

    If `program_hint` is set (canonical key like "satsang"), focus the response
    on the next occurrence of that program. Otherwise show the live + upcoming
    snapshot for the whole temple.
    """
    if get_current_schedule is None:  # safety net
        return "Recurring schedule data is unavailable right now."

    now = datetime.now(_SCHEDULE_TZ) if _SCHEDULE_TZ else datetime.now()

    # Specific program path
    if program_hint and get_next_occurrence is not None:
        try:
            next_occ = get_next_occurrence(program_hint, now)
        except Exception:
            next_occ = None
        snapshot = get_current_schedule(now)
        live_now = [p for p in snapshot.get("live", []) if p.lower() == program_hint]

        lines = [f"*{program_hint.capitalize()} schedule:*", ""]
        if live_now:
            lines.append(f"🔴 Happening right now ({_format_short_clock(now)}).")
            lines.append("")
        if next_occ:
            start = next_occ.get("start")
            end = next_occ.get("end")
            day = next_occ.get("day")
            when = _format_program_window(start, end, day)
            lines.append(f"Next: {when}")
        else:
            lines.append("No upcoming occurrences in the next 7 days.")

        exc = snapshot.get("exception")
        if exc:
            lines.extend(["", f"⚠ {exc}"])
        return "\n".join(lines).strip()

    # General schedule snapshot
    snapshot = get_current_schedule(now)
    live = snapshot.get("live") or []
    upcoming = snapshot.get("upcoming") or []
    exception = snapshot.get("exception")

    lines: List[str] = ["*Temple recurring schedule*", ""]

    if live:
        lines.append("🔴 *Happening now:*")
        for program in live:
            lines.append(f"- {program}")
        lines.append("")

    if upcoming:
        lines.append("🕒 *Starting within the next 2 hours:*")
        for program, when in upcoming:
            lines.append(f"- {program} at {_format_short_clock(when)}")
        lines.append("")

    if not live and not upcoming:
        lines.append("No temple programs are running right now.")
        lines.append("")
        lines.append("Daily programs include Darshan, Aarti, Bhog and Bhajans.")
        lines.append("Sunday Satsang runs 10:30 AM – 12:30 PM CT.")
        lines.append("")

    if exception:
        lines.append(f"⚠ {exception}")

    lines.append("Reply with a program name (Satsang, Aarti, Darshan, Bhog, Bhajans) for the next occurrence.")
    return "\n".join(lines).strip()


def _format_program_window(start: Any, end: Any, day: Any) -> str:
    if not isinstance(start, datetime):
        return MISSING_FIELD_TEXT
    day_text = str(day) if day else start.strftime("%A")
    start_clock = _format_short_clock(start)
    if isinstance(end, datetime):
        end_clock = _format_short_clock(end)
        return f"{day_text}, {start_clock} – {end_clock} CT"
    return f"{day_text}, {start_clock} CT"


def _format_short_clock(value: Any) -> str:
    if not isinstance(value, datetime):
        return MISSING_FIELD_TEXT
    return value.strftime("%I:%M %p").lstrip("0")


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


def _format_generic_sponsorship() -> str:
    """Generic sponsorship / donation response when no specific event target.

    Week 12 fix (Bug 3): Previously, "How can I donate?" classified as
    sponsorship → response builder tried to resolve a single event → returned
    "I could not find any matching events". Now we return real, non-fabricated
    seva / donation guidance with the temple's public links.
    """
    lines = [
        "*Donations & Seva at JKYog Radha Krishna Temple* 🙏",
        "",
        "Your support keeps daily worship, prasad and community programs running.",
        "",
        "Ways to contribute:",
        "- *General donation*: jkyog.org/donate",
        "- *Annadaan (food sponsorship)* — sponsor prasad for a day or week",
        "- *Sponsor a deity bhog or aarti* — single-day, weekly, or monthly",
        "- *Festival sponsorship* — Janmashtami, Holi, Diwali, etc.",
        "- *Life Transformation Program (LTP) sponsor* — covers a participant's stay",
        "",
        "If you are looking for sponsorship tiers for a *specific event*, reply with the event name (example: \"sponsorship for Holi\" or \"sponsor LTP\") and I will pull the tiers from the event page.",
    ]
    return "\n".join(lines).strip()


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
    """Render the When line for a single event detail.

    Bugfix (post-Week-12 audit, B3): the API returns naive datetime strings
    like `2026-05-04T01:30:00` with `timezone: null`, so the previous code
    rendered "May 4, 1:30 AM" with an empty TZ suffix. We now treat naive
    datetimes as Central Time (the temple's wall-clock zone) and always
    surface " CT" so users have an unambiguous time string. Multi-day
    events get the more compact "Apr 7, 2026 12:00 AM to Apr 12, 2026 1:30 AM CT".

    If the API ever does return an explicit timezone (e.g. "PST"), we honour
    it as a display label without re-converting the wall-clock time, since
    the underlying values are already local to whichever zone the scraper
    used. This is the least-wrong rendering until the 4B scraper populates
    `timezone` consistently.
    """
    start = _parse_iso_datetime(event.get("start_datetime"))
    end = _parse_iso_datetime(event.get("end_datetime"))
    api_tz = _value_or_blank(event.get("timezone"))
    tz_label = api_tz or "CT"

    if start is None and end is None:
        return f"When: {MISSING_FIELD_TEXT}"

    if start is not None and end is not None:
        start_text = start.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        end_text = end.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        return f"When: {start_text} to {end_text} {tz_label}"

    dt = start or end
    assert dt is not None
    return f"When: {dt.strftime('%b %d, %Y %I:%M %p').replace(' 0', ' ')} {tz_label}"


def _format_short_date_time(event: Mapping[str, Any]) -> str:
    """Render the When line in event-list rows (compact form).

    Bugfix mirror of `_format_date_time`: same naive-datetime / null-TZ
    behaviour, same " CT" default suffix.
    """
    start = _parse_iso_datetime(event.get("start_datetime"))
    api_tz = _value_or_blank(event.get("timezone"))
    tz_label = api_tz or "CT"
    if start is None:
        return f"When: {MISSING_FIELD_TEXT}"
    return f"When: {start.strftime('%b %d, %I:%M %p').replace(' 0', ' ')} {tz_label}"


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
