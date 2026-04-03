"""Search behavior and relevance ordering (Week 7)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

_WEEK7 = Path(__file__).resolve().parents[1]
if str(_WEEK7) not in sys.path:
    sys.path.insert(0, str(_WEEK7))

from events.storage.event_storage import search_events

_4B_ROOT = Path(__file__).resolve().parents[2]
if str(_4B_ROOT) not in sys.path:
    sys.path.insert(0, str(_4B_ROOT))

from week7.database.schema import Event, EventSourceSite
from week7.events.services.event_query_cache import EventQueryCache
from week7.events.services.event_service import EventService

from integration_db import integration_database_url


def test_search_events_whitespace_only_returns_empty_without_db_query() -> None:
    db = MagicMock()
    out = search_events(db, "   ")
    assert out == []
    db.query.assert_not_called()


def test_event_service_search_cache_normalizes_query_case() -> None:
    db = MagicMock()
    cache = EventQueryCache(ttl_seconds=60.0)
    svc = EventService(db, cache=cache)
    with patch("week7.events.services.event_service.event_storage.search_events") as m_search, patch(
        "week7.events.services.event_service.event_storage.serialize_events"
    ) as m_ser:
        m_search.return_value = []
        m_ser.return_value = []
        svc.search_events("Hanuman")
        svc.search_events("hanuman")
        assert m_search.call_count == 1


@pytest.mark.integration
def test_search_orders_name_match_before_description_only() -> None:
    url = integration_database_url()
    engine = create_engine(url)
    SessionMaker = sessionmaker(bind=engine)
    same_start = "2026-07-01T18:00:00"
    from datetime import datetime, timezone

    dt = datetime.fromisoformat(same_start.replace("Z", "")).replace(tzinfo=timezone.utc).replace(tzinfo=None)

    with SessionMaker() as db:
        db.execute(delete(Event))
        db.commit()

    with SessionMaker() as db:
        db.add_all(
            [
                Event(
                    name="Aarati Program",
                    description="Special notes mention hanuman devotion only in body",
                    start_datetime=dt,
                    end_datetime=None,
                    location="Allen, TX",
                    venue_details=None,
                    parking_notes=None,
                    food_info=None,
                    sponsorship_data=[],
                    image_url=None,
                    source_url="https://example.org/search-order-a",
                    source_site=EventSourceSite.JKYOG,
                    is_recurring=False,
                    recurrence_pattern=None,
                    category=None,
                    special_notes=None,
                    scraped_at=dt,
                    created_at=dt,
                    updated_at=dt,
                    dedup_key="d" * 64,
                ),
                Event(
                    name="Hanuman Jayanti Gala",
                    description="Other",
                    start_datetime=dt,
                    end_datetime=None,
                    location="Allen, TX",
                    venue_details=None,
                    parking_notes=None,
                    food_info=None,
                    sponsorship_data=[],
                    image_url=None,
                    source_url="https://example.org/search-order-b",
                    source_site=EventSourceSite.JKYOG,
                    is_recurring=False,
                    recurrence_pattern=None,
                    category=None,
                    special_notes=None,
                    scraped_at=dt,
                    created_at=dt,
                    updated_at=dt,
                    dedup_key="e" * 64,
                ),
            ]
        )
        db.commit()

    with SessionMaker() as db:
        rows = search_events(db, "hanuman", limit=10, offset=0)
        assert [r.name for r in rows[:2]] == ["Hanuman Jayanti Gala", "Aarati Program"]


@pytest.mark.integration
def test_search_case_insensitive_on_postgres() -> None:
    url = integration_database_url()
    engine = create_engine(url)
    SessionMaker = sessionmaker(bind=engine)
    from datetime import datetime, timezone

    dt = datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc).replace(tzinfo=None)
    with SessionMaker() as db:
        db.execute(delete(Event))
        db.commit()
    with SessionMaker() as db:
        db.add(
            Event(
                name="Unique XYZ Festival",
                description=None,
                start_datetime=dt,
                end_datetime=None,
                location=None,
                venue_details=None,
                parking_notes=None,
                food_info=None,
                sponsorship_data=[],
                image_url=None,
                source_url="https://example.org/unique-xyz",
                source_site=EventSourceSite.RADHAKRISHNATEMPLE,
                is_recurring=False,
                recurrence_pattern=None,
                category=None,
                special_notes=None,
                scraped_at=dt,
                created_at=dt,
                updated_at=dt,
                dedup_key="f" * 64,
            )
        )
        db.commit()
    with SessionMaker() as db:
        rows = search_events(db, "unique xyz", limit=10, offset=0)
        assert len(rows) == 1
        assert rows[0].name == "Unique XYZ Festival"
