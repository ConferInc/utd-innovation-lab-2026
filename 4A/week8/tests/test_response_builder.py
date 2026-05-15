from datetime import date, datetime
from unittest.mock import patch

from entity_extractor import extract_entities
from response_builder import (
    _date_range_for_timeframe,
    _event_list_intro_heading,
    _format_event_list,
    _format_timeframe_heading,
    build_response,
)


class StubEventAPIClient:
    def __init__(self, results_by_query=None):
        self.results_by_query = results_by_query or {}
        self.search_queries = []

    def search_events(self, query, *, limit=10, offset=0):
        self.search_queries.append(query)
        return {"events": self.results_by_query.get(query.lower(), [])}

    def get_events(self, *, limit=10, offset=0):
        return {
            "events": [
                {
                    "id": 999,
                    "name": "Generic Upcoming Event",
                    "start_datetime": "2030-05-20T10:00:00",
                    "end_datetime": "2030-05-20T12:00:00",
                    "location_name": "Main Hall",
                    "city": "Cedar Park",
                    "state": "TX",
                }
            ]
        }

    def get_today(self):
        return {"events": []}

    def get_recurring(self):
        return {"events": []}

    def get_event_by_id(self, event_id):
        raise AssertionError("event id lookup should not be used in this test")


def _event(name: str):
    return {
        "id": 101,
        "name": name,
        "description": "Event description",
        "start_datetime": "2030-05-20T10:00:00",
        "end_datetime": "2030-05-20T12:00:00",
        "location_name": "Temple Hall",
        "city": "Cedar Park",
        "state": "TX",
        "source_url": "https://example.com/event",
    }


def test_event_specific_prefers_cleaned_user_message_over_program_alias():
    client = StubEventAPIClient(
        results_by_query={
            "bhakti kirtan retreat": [_event("Bhakti Kirtan Retreat")],
            "kirtan": [_event("Kirtan Night")],
        }
    )
    reply = build_response(
        {
            "intent": "event_specific",
            "entities": {"program_name": "Kirtan"},
        },
        {
            "api_client": client,
            "user_message": "Tell me about the Bhakti Kirtan Retreat",
        },
    )

    assert client.search_queries == ["bhakti kirtan retreat"]
    assert "Bhakti Kirtan Retreat" in reply
    assert "*upcoming events*" not in reply.lower()


def test_event_specific_no_results_does_not_fall_back_to_generic_upcoming_list():
    client = StubEventAPIClient(results_by_query={})
    reply = build_response(
        {
            "intent": "event_specific",
            "entities": {},
        },
        {
            "api_client": client,
            "user_message": "Tell me about Hanuman Jayanti",
        },
    )

    assert client.search_queries == ["hanuman jayanti"]
    assert "could not find any matching events" in reply.lower()
    assert "*upcoming events*" not in reply.lower()


def test_extract_entities_next_weekend_before_next_week():
    assert extract_entities("what is next weekend")["timeframe"] == "next_weekend"
    assert extract_entities("events next week")["timeframe"] == "next_week"


def test_date_range_tomorrow_and_next_weekend_ct():
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Chicago")
    wed = datetime(2026, 5, 13, 12, 0, 0, tzinfo=tz)
    with patch("response_builder._now_ct", return_value=wed):
        assert _date_range_for_timeframe("tomorrow") == (date(2026, 5, 14), date(2026, 5, 14))
        assert _date_range_for_timeframe("next_weekend") == (date(2026, 5, 23), date(2026, 5, 24))
        assert _format_timeframe_heading("next_weekend") == "next weekend"

    sat = datetime(2026, 5, 16, 10, 0, 0, tzinfo=tz)
    with patch("response_builder._now_ct", return_value=sat):
        assert _date_range_for_timeframe("next_weekend") == (date(2026, 5, 23), date(2026, 5, 24))


def test_format_event_list_footer_uses_dynamic_range():
    events = [
        {
            "name": "Alpha",
            "start_datetime": "2030-01-01T10:00:00",
            "end_datetime": "2030-01-01T12:00:00",
            "location_name": "Hall",
        },
        {
            "name": "Beta",
            "start_datetime": "2030-01-02T10:00:00",
            "end_datetime": "2030-01-02T12:00:00",
            "location_name": "Hall",
        },
    ]
    text = _format_event_list(events, "next weekend")
    assert "1-2 for full details" in text
    assert "1, 2, or 3" not in text


def test_format_temple_info_mentions_on_site_parking():
    from response_builder import _format_temple_info

    assert "on-site parking" in _format_temple_info().lower()


def test_format_event_list_footer_single_row():
    events = [
        {
            "name": "Only",
            "start_datetime": "2030-01-01T10:00:00",
            "end_datetime": "2030-01-01T12:00:00",
            "location_name": "Hall",
        },
    ]
    text = _format_event_list(events, "tomorrow")
    assert "1 for full details" in text
    assert "1-1" not in text


def test_format_event_list_heading_for_intro_overrides_display():
    events = [
        {
            "name": "E",
            "start_datetime": "2030-01-01T10:00:00",
            "end_datetime": "2030-01-01T12:00:00",
            "location_name": "Hall",
        },
    ]
    text = _format_event_list(events, "upcoming events", heading_for_intro="What's on this weekend?")
    assert "What's on this weekend?" in text
    assert "*upcoming events*" not in text


def test_event_list_intro_heading_prefers_trimmed_user_message():
    assert (
        _event_list_intro_heading("upcoming events", {"user_message": "  Any programs soon?  "})
        == "Any programs soon?"
    )
    assert _event_list_intro_heading("upcoming events", {"user_message": ""}) == "upcoming events"
    assert _event_list_intro_heading("next weekend", {"user_message": "ignored"}) == "next weekend"


def test_event_list_intro_heading_truncates_long_user_message():
    long_msg = "word " * 30
    out = _event_list_intro_heading("upcoming events", {"user_message": long_msg})
    assert len(out) <= 80
    assert out.endswith("…")
