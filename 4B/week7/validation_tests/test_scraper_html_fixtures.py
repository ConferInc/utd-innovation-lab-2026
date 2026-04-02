"""Scraper tests using saved HTML fixtures (Week 7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from events.scrapers.datetime_extract import is_valid_storage_datetime
from events.scrapers.jkyog import DEFAULT_JKYOG_CALENDAR_URL, scrape_jkyog_upcoming_events
from events.scrapers.radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL, scrape_radhakrishnatemple

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "html"


class MappingHttpClient:
    """Minimal HTTP shim for scrapers (duck-types RespectfulHttpClient)."""

    def __init__(self, mapping: dict[str, str], default_html: str = "<html></html>") -> None:
        self._mapping = {k.split("?", 1)[0].rstrip("/"): v for k, v in mapping.items()}
        self._default = default_html

    def get_text(self, url: str) -> str:
        key = url.split("?", 1)[0].rstrip("/")
        return self._mapping.get(key, self._default)

    def close(self) -> None:
        return None


def _load(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def test_temple_scraper_fixture_returns_valid_event() -> None:
    temple_home = _load("temple_home.html")
    temple_detail = _load("temple_detail.html")
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-hanuman"
    client = MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): temple_home,
            detail_url: temple_detail,
        }
    )
    result = scrape_radhakrishnatemple(
        client=client,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=5,
    )
    assert len(result.events) >= 1
    first = result.events[0]
    assert "Hanuman" in first.get("name", "")
    assert is_valid_storage_datetime(first.get("start_datetime"))


def test_temple_homepage_without_links_records_error() -> None:
    client = MappingHttpClient({DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): "<html><body></body></html>"})
    result = scrape_radhakrishnatemple(
        client=client,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=5,
    )
    assert result.events == []
    assert any(e.get("stage") == "parse_homepage" for e in result.errors)


def test_temple_malformed_detail_html_does_not_raise() -> None:
    """Broken markup should not crash the scraper (best-effort parse)."""
    home = '<html><body><div class="carousel"><a href="/event/fixture-hanuman">x</a></div></body></html>'
    detail = "<html><head><h1>Unclosed and broken"
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-hanuman"
    client = MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): home,
            detail_url: detail,
        }
    )
    result = scrape_radhakrishnatemple(
        client=client,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=3,
    )
    assert isinstance(result.events, list)
    assert isinstance(result.errors, list)


def test_jkyog_scraper_fixture_finds_dallas_event() -> None:
    html = _load("jkyog_calendar.html")
    client = MappingHttpClient({DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): html})
    result = scrape_jkyog_upcoming_events(
        client=client,
        calendar_url=DEFAULT_JKYOG_CALENDAR_URL,
        extra_page_urls=(),
        max_events=10,
    )
    assert len(result.events) >= 1
    assert any("Dallas" in (ev.get("name") or "") or "dallas" in (ev.get("special_notes") or "").lower() for ev in result.events)


def test_jkyog_malformed_calendar_returns_no_events_without_uncaught_exception() -> None:
    client = MappingHttpClient({DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): "<html><div notclosed"})
    result = scrape_jkyog_upcoming_events(
        client=client,
        calendar_url=DEFAULT_JKYOG_CALENDAR_URL,
        extra_page_urls=(),
        max_events=5,
    )
    assert result.events == []


def test_fixture_html_temple_and_jkyog_combine_with_valid_datetimes() -> None:
    """Subodh tests: both scrapers on shared mock client (no changes to ``scrape_all``)."""
    temple_home = _load("temple_home.html")
    temple_detail = _load("temple_detail.html")
    jkyog_html = _load("jkyog_calendar.html")
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-hanuman"
    fake = MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): temple_home,
            detail_url: temple_detail,
            DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): jkyog_html,
        }
    )
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
    payload_events = temple.events + jkyog.events
    assert len(payload_events) >= 1
    validated = [ev for ev in payload_events if is_valid_storage_datetime(ev.get("start_datetime"))]
    assert len(validated) >= 1
