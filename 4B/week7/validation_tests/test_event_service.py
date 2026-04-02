"""EventService delegation and TTL cache (Week 7)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_4B_ROOT = Path(__file__).resolve().parents[2]
if str(_4B_ROOT) not in sys.path:
    sys.path.insert(0, str(_4B_ROOT))

from week7.database.schema import Event, EventSourceSite
from week7.events.services.event_query_cache import EventQueryCache
from week7.events.services.event_service import EventService

_STORAGE = "week7.events.services.event_service.event_storage"


def test_upcoming_cache_miss_then_hit() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=120.0)
    svc = EventService(db, cache=cache)
    with patch(f"{_STORAGE}.get_upcoming_events") as m_get, patch(f"{_STORAGE}.serialize_events") as m_ser:
        m_get.return_value = []
        m_ser.return_value = [{"id": 1, "name": "A"}]
        a = svc.get_upcoming_events(limit=5, offset=0)
        b = svc.get_upcoming_events(limit=5, offset=0)
        assert a == b
        assert m_get.call_count == 1
        assert m_ser.call_count == 1


def test_upcoming_bypasses_cache_when_now_utc_provided() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=120.0)
    svc = EventService(db, cache=cache)
    fixed = datetime(2026, 4, 1, 12, 0, 0)
    with patch(f"{_STORAGE}.get_upcoming_events") as m_get, patch(f"{_STORAGE}.serialize_events") as m_ser:
        m_get.return_value = []
        m_ser.return_value = []
        svc.get_upcoming_events(limit=3, offset=0, now_utc=fixed)
        svc.get_upcoming_events(limit=3, offset=0, now_utc=fixed)
        assert m_get.call_count == 2


def test_zero_ttl_never_caches() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=0)
    svc = EventService(db, cache=cache)
    with patch(f"{_STORAGE}.get_today_events") as m_get, patch(f"{_STORAGE}.serialize_events") as m_ser:
        m_get.return_value = []
        m_ser.return_value = []
        svc.get_today_events()
        svc.get_today_events()
        assert m_get.call_count == 2


def test_invalidate_cache_via_new_instance_store_cleared() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=120.0)
    svc = EventService(db, cache=cache)
    with patch(f"{_STORAGE}.get_recurring_events") as m_get, patch(f"{_STORAGE}.serialize_events") as m_ser:
        m_get.return_value = []
        m_ser.return_value = [{"k": 1}]
        svc.get_recurring_events()
        cache.invalidate_all()
        svc.get_recurring_events()
        assert m_get.call_count == 2


def test_get_event_by_id_caches_positive_result() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=60.0)
    svc = EventService(db, cache=cache)
    row = MagicMock()
    with patch(f"{_STORAGE}.get_event_by_id") as m_get, patch(f"{_STORAGE}.event_to_dict") as m_dict:
        m_get.return_value = row
        m_dict.return_value = {"id": 7}
        a = svc.get_event_by_id(7)
        b = svc.get_event_by_id(7)
        assert a == b
        assert m_get.call_count == 1
        assert m_dict.call_count == 1


def test_get_event_by_id_does_not_cache_miss(monkeypatch: pytest.MonkeyPatch) -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=60.0)
    svc = EventService(db, cache=cache)
    with patch(f"{_STORAGE}.get_event_by_id") as m_get:
        m_get.return_value = None
        assert svc.get_event_by_id(404) is None
        assert svc.get_event_by_id(404) is None
        assert m_get.call_count == 2


def test_stale_serialization_respects_now_utc() -> None:
    db = MagicMock()
    svc = EventService(db, cache=None)
    now = datetime(2026, 6, 1, 0, 0, 0, tzinfo=timezone.utc).replace(tzinfo=None)
    scraped = now - timedelta(days=40)
    row = Event(
        id=1,
        name="X",
        description=None,
        start_datetime=scraped,
        end_datetime=None,
        location=None,
        venue_details=None,
        parking_notes=None,
        food_info=None,
        sponsorship_data=[],
        image_url=None,
        source_url="https://example.org/x",
        source_site=EventSourceSite.JKYOG,
        is_recurring=False,
        recurrence_pattern=None,
        category=None,
        special_notes=None,
        scraped_at=scraped,
        created_at=scraped,
        updated_at=scraped,
        dedup_key="b" * 64,
    )
    with patch(f"{_STORAGE}.get_event_by_id", return_value=row):
        out = svc.get_event_by_id(1, now_utc=now, stale_after_days=30)
        assert out is not None
        assert out["is_stale"] is True
