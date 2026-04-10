"""
End-to-end tests (Week 7).

Tier A: ``seed_from_file`` on ``fixtures/scraped_min.json`` → HTTP ``/api/v2/events`` and ``/search``.

Tier B: temple + JKYog scrapers with shared mock HTTP (fixture HTML) → bundle JSON → ``seed_from_file`` → HTTP.

Uses ``WEEK7_E2E_DATABASE_URL`` if set, otherwise ``DATABASE_URL`` (see ``conftest.py`` default).
Requires a reachable Postgres with the ``events`` table (migrations applied).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

_WEEK7 = Path(__file__).resolve().parents[1]
_4B_ROOT = Path(__file__).resolve().parents[2]
for p in (_4B_ROOT, _WEEK7):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from week7.api.events import router as events_router
from week7.database.models import get_db
from week7.database.schema import Event
from week7.events.services.event_query_cache import reset_shared_event_query_cache_for_tests
from week7.scripts.seed_from_scraped_json import seed_from_file

from integration_db import integration_database_url

_FIXTURES_HTML = Path(__file__).resolve().parent / "fixtures" / "html"


class _MappingHttpClient:
    """Duck-type ``RespectfulHttpClient`` for mocked scrape → seed (Tier B)."""

    def __init__(self, mapping: dict[str, str], default_html: str = "<html></html>") -> None:
        self._mapping = {k.split("?", 1)[0].rstrip("/"): v for k, v in mapping.items()}
        self._default = default_html

    def get_text(self, url: str) -> str:
        key = url.split("?", 1)[0].rstrip("/")
        return self._mapping.get(key, self._default)

    def close(self) -> None:
        return None


def _html_fixture(name: str) -> str:
    return (_FIXTURES_HTML / name).read_text(encoding="utf-8")


def _fixture_scrape_bundle(fake: _MappingHttpClient) -> dict:
    """Mirror ``scrape_all`` merge/dedup for tests without modifying ``scrape_all.py``."""
    from events.scrapers.datetime_extract import is_valid_storage_datetime
    from events.scrapers.jkyog import DEFAULT_JKYOG_CALENDAR_URL, scrape_jkyog_upcoming_events
    from events.scrapers.radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL, scrape_radhakrishnatemple

    temple = scrape_radhakrishnatemple(
        client=fake,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=20,
    )
    jkyog = scrape_jkyog_upcoming_events(
        client=fake,
        calendar_url=DEFAULT_JKYOG_CALENDAR_URL,
        extra_page_urls=(),
        max_events=50,
    )
    combined = temple.events + jkyog.events
    errors: list = [*temple.errors, *jkyog.errors]
    validated: list = []
    skipped = 0
    for ev in combined:
        if not is_valid_storage_datetime(ev.get("start_datetime")):
            skipped += 1
            continue
        validated.append(ev)
    seen: set[tuple[str, str, str]] = set()
    deduped: list = []
    for ev in validated:
        key = (
            str(ev.get("name") or "").strip().lower(),
            str(ev.get("start_datetime") or "").strip(),
            str(ev.get("location_name") or ev.get("location") or "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(ev)
    return {
        "scraped_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "events": deduped,
        "errors": errors,
        "skipped_invalid_datetime": skipped,
    }


@pytest.mark.integration
def test_seed_from_file_then_list_events_over_http() -> None:
    url = integration_database_url()
    engine = create_engine(url)
    SessionMaker = sessionmaker(bind=engine)
    json_path = str(Path(__file__).resolve().parent / "fixtures" / "scraped_min.json")

    reset_shared_event_query_cache_for_tests()

    with SessionMaker() as db:
        db.execute(delete(Event))
        db.commit()

    with SessionMaker() as db:
        stats = seed_from_file(db, json_path)
        assert stats["input_count"] >= 1

    app = FastAPI()
    app.include_router(events_router, prefix="/api/v2/events")

    def _db_override():
        s = SessionMaker()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _db_override

    with TestClient(app) as client:
        r = client.get("/api/v2/events", params={"limit": 20, "offset": 0})
        assert r.status_code == 200
        names = {e["name"] for e in r.json()["events"]}
        assert "Integration Hanuman" in names


@pytest.mark.integration
def test_seed_then_search_http() -> None:
    url = integration_database_url()
    engine = create_engine(url)
    SessionMaker = sessionmaker(bind=engine)
    json_path = str(Path(__file__).resolve().parent / "fixtures" / "scraped_min.json")

    reset_shared_event_query_cache_for_tests()

    with SessionMaker() as db:
        db.execute(delete(Event))
        db.commit()

    with SessionMaker() as db:
        seed_from_file(db, json_path)

    app = FastAPI()
    app.include_router(events_router, prefix="/api/v2/events")

    def _db_override():
        s = SessionMaker()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _db_override

    with TestClient(app) as client:
        r = client.get("/api/v2/events/search", params={"q": "Integration Hanuman", "limit": 10})
        assert r.status_code == 200
        assert any("Integration Hanuman" == ev["name"] for ev in r.json()["events"])


@pytest.mark.integration
def test_tier_b_mocked_scrape_then_seed_then_list_over_http() -> None:
    """
    Tier B: fixture HTML via both scrapers → bundle JSON → ``seed_from_file`` → GET /api/v2/events.
    """
    from events.scrapers.jkyog import DEFAULT_JKYOG_CALENDAR_URL
    from events.scrapers.radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL

    temple_home = _html_fixture("temple_home.html")
    temple_detail = _html_fixture("temple_detail.html")
    jkyog_html = _html_fixture("jkyog_calendar.html")
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-hanuman"
    fake = _MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): temple_home,
            detail_url: temple_detail,
            DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): jkyog_html,
        }
    )

    bundle = _fixture_scrape_bundle(fake)
    assert bundle.get("events"), "mocked scrape should yield at least one valid event"

    url = integration_database_url()
    engine = create_engine(url)
    SessionMaker = sessionmaker(bind=engine)

    reset_shared_event_query_cache_for_tests()

    with SessionMaker() as db:
        db.execute(delete(Event))
        db.commit()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(bundle, tmp)
        tmp_path = tmp.name

    try:
        with SessionMaker() as db:
            stats = seed_from_file(db, tmp_path)
            assert stats.get("inserted", 0) + stats.get("updated", 0) >= 1

        app = FastAPI()
        app.include_router(events_router, prefix="/api/v2/events")

        def _db_override():
            s = SessionMaker()
            try:
                yield s
            finally:
                s.close()

        app.dependency_overrides[get_db] = _db_override

        with TestClient(app) as client:
            r = client.get("/api/v2/events", params={"limit": 50, "offset": 0})
            assert r.status_code == 200
            names = {e["name"] for e in r.json()["events"]}
            assert len(names) >= 1
    finally:
        os.unlink(tmp_path)
