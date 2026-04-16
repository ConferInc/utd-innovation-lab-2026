"""HTTP tests for /api/v2/events (Week 7 — Team 4A contract)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Parent of `week7/` on path so `week7.api` resolves (`api` uses relative .. imports).
_4B_ROOT = Path(__file__).resolve().parents[2]
if str(_4B_ROOT) not in sys.path:
    sys.path.insert(0, str(_4B_ROOT))

from week7.api.events import router as events_router
from week7.database.models import get_db
from week7.database.schema import Event, EventSourceSite
from week7.events.services.event_query_cache import reset_shared_event_query_cache_for_tests


def _naive_utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=timezone.utc).replace(tzinfo=None)


def _sample_event(**overrides) -> Event:
    base = {
        "id": 1,
        "name": "Hanuman Jayanti",
        "description": "Festival celebration",
        "start_datetime": _naive_utc(2026, 4, 10, 18, 0, 0),
        "end_datetime": None,
        "location": "Allen, TX",
        "venue_details": None,
        "parking_notes": None,
        "food_info": None,
        "sponsorship_data": [],
        "image_url": None,
        "source_url": "https://example.org/hanuman",
        "source_site": EventSourceSite.RADHAKRISHNATEMPLE,
        "is_recurring": False,
        "recurrence_pattern": None,
        "category": "jayanti",
        "special_notes": None,
        "scraped_at": _naive_utc(2026, 4, 1, 12, 0, 0),
        "created_at": _naive_utc(2026, 4, 1, 12, 0, 0),
        "updated_at": _naive_utc(2026, 4, 1, 12, 0, 0),
        "dedup_key": "a" * 64,
    }
    base.update(overrides)
    return Event(**base)


_STORAGE = "week7.events.services.event_service.event_storage"


@pytest.fixture
def events_client():
    reset_shared_event_query_cache_for_tests()
    app = FastAPI()
    app.include_router(events_router, prefix="/api/v2/events")

    def _empty_db():
        yield None

    app.dependency_overrides[get_db] = _empty_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@patch(f"{_STORAGE}.get_upcoming_events")
def test_list_upcoming_events_pagination_ok(mock_get, events_client) -> None:
    mock_get.return_value = [_sample_event(id=1)]
    r = events_client.get("/api/v2/events", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert len(body["events"]) == 1
    assert body["events"][0]["name"] == "Hanuman Jayanti"


def test_list_upcoming_events_bad_limit(events_client) -> None:
    r = events_client.get("/api/v2/events", params={"limit": 0})
    assert r.status_code == 400


def test_list_upcoming_events_bad_offset(events_client) -> None:
    r = events_client.get("/api/v2/events", params={"offset": -1})
    assert r.status_code == 400


@patch(f"{_STORAGE}.get_event_by_id")
def test_get_event_by_id_found(mock_get, events_client) -> None:
    mock_get.return_value = _sample_event(id=42)
    r = events_client.get("/api/v2/events/42")
    assert r.status_code == 200
    assert r.json()["id"] == 42


@patch(f"{_STORAGE}.get_event_by_id")
def test_get_event_by_id_not_found(mock_get, events_client) -> None:
    mock_get.return_value = None
    r = events_client.get("/api/v2/events/999")
    assert r.status_code == 404


@patch(f"{_STORAGE}.search_events")
def test_search_events_requires_q(mock_search, events_client) -> None:
    r = events_client.get("/api/v2/events/search")
    assert r.status_code == 400
    mock_search.assert_not_called()


@patch(f"{_STORAGE}.search_events")
def test_search_events_case_insensitive(mock_search, events_client) -> None:
    mock_search.return_value = [_sample_event(name="Hanuman Jayanti")]
    r = events_client.get("/api/v2/events/search", params={"q": "hanuman"})
    assert r.status_code == 200
    mock_search.assert_called_once()
    assert r.json()["events"][0]["name"] == "Hanuman Jayanti"


@patch(f"{_STORAGE}.search_events")
def test_search_events_empty_result_200(mock_search, events_client) -> None:
    mock_search.return_value = []
    r = events_client.get("/api/v2/events/search", params={"q": "nomatch"})
    assert r.status_code == 200
    assert r.json()["events"] == []


@patch(f"{_STORAGE}.search_events")
def test_search_events_forwards_limit_and_offset(mock_search, events_client) -> None:
    mock_search.return_value = []
    r = events_client.get("/api/v2/events/search", params={"q": "temple", "limit": 2, "offset": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 2
    assert body["offset"] == 3
    _args, kwargs = mock_search.call_args
    assert kwargs.get("limit") == 2
    assert kwargs.get("offset") == 3


@patch(f"{_STORAGE}.get_today_events")
def test_today_events(mock_get, events_client) -> None:
    mock_get.return_value = [_sample_event()]
    r = events_client.get("/api/v2/events/today")
    assert r.status_code == 200
    assert len(r.json()["events"]) == 1


@patch(f"{_STORAGE}.get_recurring_events")
def test_recurring_events(mock_get, events_client) -> None:
    mock_get.return_value = [_sample_event(id=2, is_recurring=True, recurrence_pattern="weekly:sunday")]
    r = events_client.get("/api/v2/events/recurring")
    assert r.status_code == 200
    assert r.json()["events"][0]["is_recurring"] is True


@patch(f"{_STORAGE}.get_upcoming_events")
def test_list_upcoming_events_surfaces_is_stale_for_old_scraped_at(mock_get, events_client) -> None:
    old = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=40)
    mock_get.return_value = [_sample_event(id=9, scraped_at=old)]
    r = events_client.get("/api/v2/events", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    assert r.json()["events"][0].get("is_stale") is True


@patch(f"{_STORAGE}.get_upcoming_events")
def test_list_upcoming_events_surfaces_is_stale_false_for_recent_scrape(mock_get, events_client) -> None:
    recent = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)
    mock_get.return_value = [_sample_event(id=10, scraped_at=recent)]
    r = events_client.get("/api/v2/events", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    assert r.json()["events"][0].get("is_stale") is False
