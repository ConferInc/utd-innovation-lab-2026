"""SQLite-backed endpoint tests for all Week 8 event routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_4B_ROOT = Path(__file__).resolve().parents[2]
if str(_4B_ROOT) not in sys.path:
    sys.path.insert(0, str(_4B_ROOT))

from week8.api.events import router as events_router
from week8.database.models import Base, get_db
from week8.database.schema import Event, EventSourceSite
from week8.events.services.event_query_cache import reset_shared_event_query_cache_for_tests
from fastapi import FastAPI


def _naive_utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=timezone.utc).replace(tzinfo=None)


@pytest.fixture
def events_client() -> TestClient:
    reset_shared_event_query_cache_for_tests()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add_all(
        [
            Event(
                name="Hanuman Jayanti",
                subtitle=None,
                category="festival",
                event_type="in_person",
                is_recurring=False,
                recurrence_pattern=None,
                recurrence_text=None,
                start_datetime=now + timedelta(days=1),
                end_datetime=None,
                timezone="America/Chicago",
                location_name="RKT Dallas",
                address="1450 N Watters Rd",
                city="Allen",
                state="TX",
                postal_code="75013",
                country="USA",
                description="Festival celebration",
                registration_required=False,
                registration_status="open",
                registration_url=None,
                contact_email=None,
                contact_phone=None,
                parking_notes=None,
                transportation_notes=None,
                food_info=None,
                price={"amount": 0, "notes": "Free"},
                sponsorship_tiers=[],
                source_url="https://example.org/hanuman",
                source_site=EventSourceSite.RADHAKRISHNATEMPLE,
                source_page_type="event_detail",
                scraped_at=now - timedelta(days=5),
                source_confidence="high",
                notes="Canonical test event",
                dedup_key="a" * 64,
            ),
            Event(
                name="Sunday Satsang",
                subtitle=None,
                category="satsang",
                event_type="in_person",
                is_recurring=True,
                recurrence_pattern="weekly:sunday",
                recurrence_text="weekly:sunday",
                start_datetime=now - timedelta(days=3),
                end_datetime=None,
                timezone="America/Chicago",
                location_name="RKT Dallas",
                address=None,
                city="Allen",
                state="TX",
                postal_code="75013",
                country="USA",
                description="Recurring program",
                registration_required=None,
                registration_status="unknown",
                registration_url=None,
                contact_email=None,
                contact_phone=None,
                parking_notes=None,
                transportation_notes=None,
                food_info=None,
                price={"amount": None, "notes": None},
                sponsorship_tiers=[],
                source_url="https://example.org/sunday-satsang",
                source_site=EventSourceSite.JKYOG,
                source_page_type="upcoming_events",
                scraped_at=now - timedelta(days=40),
                source_confidence="medium",
                notes="Recurring weekly event",
                dedup_key="b" * 64,
            ),
        ]
    )
    db.commit()
    db.close()

    app = FastAPI()
    app.include_router(events_router, prefix="/api/v2/events")

    def _override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_list_upcoming_events_sqlite(events_client: TestClient) -> None:
    response = events_client.get("/api/v2/events", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 10
    assert len(body["events"]) >= 1
    assert body["events"][0]["name"] in {"Hanuman Jayanti", "Sunday Satsang"}


def test_today_events_sqlite(events_client: TestClient) -> None:
    response = events_client.get("/api/v2/events/today")
    assert response.status_code == 200
    assert "events" in response.json()


def test_recurring_events_sqlite(events_client: TestClient) -> None:
    response = events_client.get("/api/v2/events/recurring")
    assert response.status_code == 200
    events = response.json()["events"]
    assert any(item["is_recurring"] is True for item in events)


def test_search_events_sqlite(events_client: TestClient) -> None:
    response = events_client.get("/api/v2/events/search", params={"q": "hanuman"})
    assert response.status_code == 200
    assert any("Hanuman" in item["name"] for item in response.json()["events"])


def test_get_event_by_id_sqlite(events_client: TestClient) -> None:
    list_response = events_client.get("/api/v2/events", params={"limit": 10, "offset": 0})
    first_id = list_response.json()["events"][0]["id"]
    response = events_client.get(f"/api/v2/events/{first_id}")
    assert response.status_code == 200
    assert response.json()["id"] == first_id
