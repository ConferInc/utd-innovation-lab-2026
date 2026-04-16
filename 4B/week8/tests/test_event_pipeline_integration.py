"""
Full pipeline integration tests: mock scraper JSON → upsert_events → EventService → HTTP API.

Uses in-memory SQLite per test (StaticPool); no Render or Postgres required.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_4B_ROOT = Path(__file__).resolve().parents[2]
_WEEK8_ROOT = Path(__file__).resolve().parents[1]
for p in (str(_WEEK8_ROOT), str(_4B_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from api.events import router as events_router
    from database.models import Base, get_db
    from database.schema import Event
    from events.storage import event_storage as event_storage_module
    from events.services.event_query_cache import reset_shared_event_query_cache_for_tests
    from events.services.event_service import EventService
    from events.storage.event_storage import upsert_events
    from knowledge_base.ingestion import clear_ingested_events, ingest_events, search_kb
except ImportError:
    from week8.api.events import router as events_router
    from week8.database.models import Base, get_db
    from week8.database.schema import Event
    from week8.events.storage import event_storage as event_storage_module
    from week8.events.services.event_query_cache import reset_shared_event_query_cache_for_tests
    from week8.events.services.event_service import EventService
    from week8.events.storage.event_storage import upsert_events
    from week8.knowledge_base.ingestion import clear_ingested_events, ingest_events, search_kb


API_PREFIX = "/api/v2/events"


def _naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _base_payload(**overrides: object) -> dict:
    base = {
        "name": "Pipeline Test Event",
        "start_datetime": (_naive_utc_now() + timedelta(days=14)).isoformat(),
        "source_url": "https://example.org/pipeline-test",
        "source_site": "radhakrishnatemple",
        "scraped_at": _naive_utc_now().isoformat(),
        "location_name": "RKT Dallas",
    }
    merged = {**base, **overrides}
    return merged


@contextmanager
def _sqlite_session_scope():
    reset_shared_event_query_cache_for_tests()
    clear_ingested_events()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session, SessionLocal
    finally:
        session.close()
        engine.dispose()


def _make_app(SessionLocal) -> TestClient:
    app = FastAPI()
    app.include_router(events_router, prefix=API_PREFIX)

    def _override_get_db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_single_upsert_service_and_api():
    with _sqlite_session_scope() as (db, SessionLocal):
        p = _base_payload(name="Single Upsert Gala")
        upsert_events(db, [p])

        svc = EventService(db, cache=None)
        upcoming = svc.get_upcoming_events(limit=20)
        assert any(e["name"] == "Single Upsert Gala" for e in upcoming)

        client = _make_app(SessionLocal)
        r = client.get(API_PREFIX, params={"limit": 20})
        assert r.status_code == 200
        assert any(e["name"] == "Single Upsert Gala" for e in r.json()["events"])


def test_duplicate_upsert_dedup_no_extra_row():
    with _sqlite_session_scope() as (db, SessionLocal):
        start = (_naive_utc_now() + timedelta(days=20)).replace(microsecond=0)
        p1 = _base_payload(
            name="Dedup Hanuman",
            start_datetime=start.isoformat(),
            location_name="Allen TX",
            source_url="https://example.org/dedup-a",
        )
        p2 = dict(p1)
        p2["source_url"] = "https://example.org/dedup-b"
        stats = upsert_events(db, [p1, p2])
        assert stats["inserted"] == 1
        assert stats["updated"] == 1
        n = db.query(func.count(Event.id)).scalar()
        assert n == 1


def test_search_by_name_http():
    with _sqlite_session_scope() as (db, SessionLocal):
        upsert_events(
            db,
            [
                _base_payload(
                    name="Zyzzyva Special Satsang",
                    source_url="https://example.org/zyzzyva",
                )
            ],
        )
        client = _make_app(SessionLocal)
        r = client.get(f"{API_PREFIX}/search", params={"q": "Zyzzyva"})
        assert r.status_code == 200
        assert any("Zyzzyva" in e["name"] for e in r.json()["events"])


def test_today_filter_http():
    fixed_now = datetime(2026, 4, 15, 18, 0, 0)
    day_start = datetime(2026, 4, 15, 11, 0, 0)
    with _sqlite_session_scope() as (db, SessionLocal):
        upsert_events(
            db,
            [
                _base_payload(
                    name="Today Only Program",
                    start_datetime=day_start.isoformat(),
                    source_url="https://example.org/today-only",
                )
            ],
        )
        with patch.object(event_storage_module, "_now", return_value=fixed_now):
            client = _make_app(SessionLocal)
            r = client.get(f"{API_PREFIX}/today")
        assert r.status_code == 200
        names = {e["name"] for e in r.json()["events"]}
        assert "Today Only Program" in names


def test_recurring_filter_http():
    with _sqlite_session_scope() as (db, SessionLocal):
        upsert_events(
            db,
            [
                _base_payload(
                    name="Daily Aarti Loop",
                    is_recurring=True,
                    recurrence_text="daily",
                    start_datetime=_naive_utc_now().isoformat(),
                    source_url="https://example.org/recurring-daily",
                )
            ],
        )
        client = _make_app(SessionLocal)
        r = client.get(f"{API_PREFIX}/recurring")
        assert r.status_code == 200
        assert any(e["name"] == "Daily Aarti Loop" and e["is_recurring"] for e in r.json()["events"])


def test_sponsorship_tiers_in_detail_http():
    with _sqlite_session_scope() as (db, SessionLocal):
        upsert_events(
            db,
            [
                _base_payload(
                    name="Sponsor Gala Night",
                    sponsorship_tiers=[
                        {"tier_name": "Gold Patron", "price": 500.0, "description": "Banner + mention"},
                        {"tier_name": "Silver", "price": 100.0, "description": None},
                    ],
                    source_url="https://example.org/sponsor-gala",
                )
            ],
        )
        client = _make_app(SessionLocal)
        lst = client.get(API_PREFIX, params={"limit": 5})
        eid = next(e["id"] for e in lst.json()["events"] if e["name"] == "Sponsor Gala Night")
        r = client.get(f"{API_PREFIX}/{eid}")
        assert r.status_code == 200
        tiers = r.json()["sponsorship_tiers"]
        assert len(tiers) == 2
        assert tiers[0]["tier_name"] == "Gold Patron"
        assert tiers[0]["price"] == 500.0
        assert "Banner" in (tiers[0].get("description") or "")


def test_seed_pipeline_populates_kb_search():
    with _sqlite_session_scope() as (db, SessionLocal):
        upsert_events(
            db,
            [
                _base_payload(
                    name="KbSearchUniqueMela",
                    description="Outdoor festival with music.",
                    source_url="https://example.org/kb-mela",
                )
            ],
        )
        ingest_events(db)
        hits = search_kb("KbSearchUniqueMela festival", top_k=5)
        assert any(
            h.get("type") == "event" and h.get("payload", {}).get("name") == "KbSearchUniqueMela"
            for h in hits
        )


def test_ingest_events_paginates_all_upcoming():
    """Regression: KB ingest must page through every upcoming row, not only the first chunk."""
    with _sqlite_session_scope() as (db, SessionLocal):
        start = (_naive_utc_now() + timedelta(days=30)).isoformat()
        payloads = [
            _base_payload(
                name=f"KbPage{i}",
                start_datetime=start,
                source_url=f"https://example.org/kb-page-{i}",
            )
            for i in range(4)
        ]
        upsert_events(db, payloads)
        n = ingest_events(db, page_size=2)
        assert n == 4
        for i in range(4):
            hits = search_kb(f"KbPage{i}", top_k=3)
            assert any(h.get("payload", {}).get("name") == f"KbPage{i}" for h in hits)
