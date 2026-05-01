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
    assert any("Dallas" in (ev.get("name") or "") or "dallas" in (ev.get("notes") or "").lower() for ev in result.events)


def test_jkyog_malformed_calendar_returns_no_events_without_uncaught_exception() -> None:
    client = MappingHttpClient({DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): "<html><div notclosed"})
    result = scrape_jkyog_upcoming_events(
        client=client,
        calendar_url=DEFAULT_JKYOG_CALENDAR_URL,
        extra_page_urls=(),
        max_events=5,
    )
    assert result.events == []


def test_jkyog_skips_placeholder_loading_title() -> None:
    """Pre-hydration skeleton cards titled 'Loading Event Details' must not leak into output.

    Chakradhar's Week 10 diagnostic caught one such row; we log it as a
    ``stage=placeholder_title`` error instead of shipping a useless event.
    """
    html = """
    <html><body><main>
      <div class="w-dyn-list">
        <div class="w-dyn-item">
          <a href="https://www.jkyog.org/placeholder-event">
            <h3>Loading Event Details</h3>
            Allen, TX 75013 — Radha Krishna Temple of Dallas, 1450 North Watters Road
          </a>
        </div>
      </div>
    </main></body></html>
    """
    client = MappingHttpClient({DEFAULT_JKYOG_CALENDAR_URL.rstrip("/"): html})
    result = scrape_jkyog_upcoming_events(
        client=client,
        calendar_url=DEFAULT_JKYOG_CALENDAR_URL,
        extra_page_urls=(),
        max_events=5,
    )
    assert result.events == []
    assert any(e.get("stage") == "placeholder_title" for e in result.errors)


def test_temple_scraper_skips_placeholder_detail_page() -> None:
    """Temple detail pages whose title resolves to 'Loading...' must be skipped."""
    home = (
        '<html><body><div class="carousel">'
        '<a href="/event/fixture-placeholder">x</a>'
        "</div></body></html>"
    )
    placeholder_detail = (
        "<html><body><h1>Loading Event Details</h1>"
        "<article><p>April 10, 2026 6:00 PM Central</p></article>"
        "</body></html>"
    )
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-placeholder"
    client = MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): home,
            detail_url: placeholder_detail,
        }
    )
    result = scrape_radhakrishnatemple(
        client=client,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=3,
    )
    assert result.events == []
    assert any(e.get("stage") == "placeholder_title" for e in result.errors)


def test_temple_multi_day_range_populates_end_datetime() -> None:
    """``Mar 26-29, 2026`` style ranges must produce both start and end datetimes."""
    home = (
        '<html><body><div class="carousel">'
        '<a href="/event/fixture-navratri">x</a>'
        "</div></body></html>"
    )
    multi_day_detail = (
        "<html><body>"
        "<h1>Chaitra Navratri</h1>"
        "<article><p>Chaitra Navratri Mar 26-29, 2026 at the temple.</p></article>"
        "</body></html>"
    )
    detail_url = "https://www.radhakrishnatemple.net/event/fixture-navratri"
    client = MappingHttpClient(
        {
            DEFAULT_TEMPLE_HOMEPAGE_URL.rstrip("/"): home,
            detail_url: multi_day_detail,
        }
    )
    result = scrape_radhakrishnatemple(
        client=client,
        homepage_url=DEFAULT_TEMPLE_HOMEPAGE_URL,
        supplemental_event_urls=(),
        max_events=3,
    )
    assert len(result.events) == 1
    event = result.events[0]
    assert is_valid_storage_datetime(event.get("start_datetime"))
    assert is_valid_storage_datetime(event.get("end_datetime"))


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
