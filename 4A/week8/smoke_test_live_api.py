"""Live smoke test for Team 4A / Team 4B integration.

Uses the latest attached files:
- api_client.py
- response_builder_fixed.py

What it checks:
1. All 5 Team 4B endpoints are reachable through EventAPIClient.
2. List payloads can be parsed by response_builder_fixed._extract_events(...).
3. Single-event detail works whether /{id} returns a direct event dict or {"event": {...}}.
4. build_response(...) produces readable WhatsApp-safe output for key intents.
5. Extra fields in payloads do not break formatting.
6. WhatsApp truncation marker appears and output stays within 4096 chars.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence

from api_client import APIClientError, EventAPIClient
from response_builder_fixed import (
    WHATSAPP_CHAR_LIMIT,
    _extract_events,
    _format_single_event,
    _resolve_single_event,
    _truncate_whatsapp,
    build_response,
)

SEARCH_QUERY = os.getenv("SMOKE_TEST_QUERY", "krishna")


class SmokeTestFailure(RuntimeError):
    """Raised when a smoke-test assertion fails."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeTestFailure(message)


def _print_header(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def _ensure_dict(payload: Any, label: str) -> Dict[str, Any]:
    _assert(isinstance(payload, dict), f"{label}: expected dict, got {type(payload).__name__}")
    return payload


def _pick_event_id(*payloads: Mapping[str, Any]) -> Optional[int]:
    for payload in payloads:
        events = _extract_events(payload)
        for event in events:
            event_id = event.get("id")
            if isinstance(event_id, int):
                return event_id
            try:
                if event_id is not None:
                    return int(str(event_id).strip())
            except (TypeError, ValueError):
                continue
    return None


def _add_extra_fields(event: Mapping[str, Any]) -> Dict[str, Any]:
    enriched = dict(event)
    enriched.update(
        {
            "image_url": "https://example.com/fake-image.jpg",
            "created_at": "2026-04-20T12:00:00Z",
            "updated_at": "2026-04-20T12:05:00Z",
            "dedup_key": "smoke-test-key",
            "is_stale": False,
        }
    )
    return enriched


def _test_endpoint_list(label: str, payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    payload = _ensure_dict(payload, label)
    events = _extract_events(payload)
    print(f"PASS - {label}: parsed {len(events)} event(s)")
    return events


def _test_builder_intent(intent: str, session_context: Mapping[str, Any], **extra_intent: Any) -> str:
    classified_intent = {"intent": intent, **extra_intent}
    text = build_response(classified_intent, dict(session_context))
    _assert(isinstance(text, str), f"build_response({intent}) did not return a string")
    _assert(text.strip(), f"build_response({intent}) returned empty text")
    _assert(len(text) <= WHATSAPP_CHAR_LIMIT, f"build_response({intent}) exceeded WhatsApp limit")
    print(f"PASS - build_response intent={intent!r} produced {len(text)} chars")
    return text


def run_smoke_test() -> None:
    base_url = os.getenv("EVENTS_API_BASE_URL", "http://127.0.0.1:8000")
    print(f"Using EVENTS_API_BASE_URL={base_url}")
    print("Using response builder module: response_builder_fixed.py")

    client = EventAPIClient()
    session_context: Dict[str, Any] = {"api_client": client}

    _print_header("1) Testing GET /api/v2/events")
    events_payload = client.get_events(limit=5, offset=0)
    events = _test_endpoint_list("GET /api/v2/events", events_payload)

    _print_header("2) Testing GET /api/v2/events/today")
    today_payload = client.get_today()
    today_events = _test_endpoint_list("GET /api/v2/events/today", today_payload)

    _print_header(f"3) Testing GET /api/v2/events/search?q={SEARCH_QUERY}")
    search_payload = client.search_events(SEARCH_QUERY, limit=5, offset=0)
    search_events = _test_endpoint_list("GET /api/v2/events/search", search_payload)

    _print_header("4) Testing GET /api/v2/events/recurring")
    recurring_payload = client.get_recurring()
    recurring_events = _test_endpoint_list("GET /api/v2/events/recurring", recurring_payload)

    _print_header("5) Testing GET /api/v2/events/{id}")
    event_id = _pick_event_id(search_payload, events_payload, today_payload, recurring_payload)
    _assert(event_id is not None, "Could not find a valid event id from list/search payloads")
    detail_payload = _ensure_dict(client.get_event_by_id(event_id), "GET /api/v2/events/{id}")
    resolved_event = _resolve_single_event(client, event_id=event_id, query=None)
    _assert(isinstance(resolved_event, dict), "_resolve_single_event did not return an event dict")
    _assert(bool(resolved_event.get("name")), "Resolved single event is missing a usable name")
    print(f"PASS - event detail loaded for id={event_id}")
    if isinstance(detail_payload.get("event"), dict):
        print("PASS - detail endpoint returned wrapped {'event': {...}} shape and was unwrapped correctly")
    else:
        print("PASS - detail endpoint returned direct event shape")

    _print_header("6) Testing extra fields do not break formatting")
    enriched_event = _add_extra_fields(resolved_event)
    single_text = _format_single_event(enriched_event)
    _assert(isinstance(single_text, str) and single_text.strip(), "Single-event formatter failed with extra fields")
    print("PASS - extra fields did not break single-event formatting")

    _print_header("7) Testing build_response(...) integration")
    _test_builder_intent("event_list", session_context)
    _test_builder_intent("today_events", session_context)
    _test_builder_intent("event_search", session_context, query=SEARCH_QUERY)
    _test_builder_intent("single_event_detail", session_context, event_id=event_id)
    _test_builder_intent("sponsorship", session_context, event_id=event_id)
    _test_builder_intent("logistics", session_context, event_id=event_id)

    _print_header("8) Testing explicit truncation behavior")
    base_response = build_response({"intent": "event_list"}, dict(session_context))
    long_text = (base_response + "\n\n") * 80
    truncated = _truncate_whatsapp(long_text)
    _assert(len(truncated) <= WHATSAPP_CHAR_LIMIT, "Truncated text still exceeds WhatsApp limit")
    _assert(truncated.endswith("... [truncated]"), "Truncation marker missing or unreadable")
    print(f"PASS - truncation marker appears and final text is {len(truncated)} chars")

    _print_header("Summary")
    print(f"PASS - /events count: {len(events)}")
    print(f"PASS - /today count: {len(today_events)}")
    print(f"PASS - /search count: {len(search_events)}")
    print(f"PASS - /recurring count: {len(recurring_events)}")
    print(f"PASS - tested detail event id: {event_id}")
    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    try:
        run_smoke_test()
    except APIClientError as exc:
        print(f"API ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except SmokeTestFailure as exc:
        print(f"SMOKE TEST FAILURE: {exc}", file=sys.stderr)
        sys.exit(3)
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(4)
