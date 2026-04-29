"""JKYog.org upcoming-events scraper — static HTML only.

Fetches public pages with ``httpx`` and parses cards with BeautifulSoup. Rows
that are injected purely via JavaScript after load will not be present in the
fetched HTML and are therefore skipped without raising an error.

When debugging empty results, compare against the live site in a browser with
JS enabled; if content only appears after scripts run, plan a Playwright or
Selenium-based fetch before expanding parsers here.
"""

from __future__ import annotations

import codecs
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .category_from_title import guess_event_category
from .datetime_extract import extract_event_datetimes
from .http_client import RespectfulHttpClient

logger = logging.getLogger(__name__)

JKYOG_SITE_URL = "https://www.jkyog.org"
DEFAULT_JKYOG_CALENDAR_URL = "https://www.jkyog.org/upcoming_events"
# Extra JKYog pages to scrape and merge with ``upcoming_events``.
DEFAULT_JKYOG_EXTRA_PAGE_URLS: Tuple[str, ...] = ("https://www.jkyog.org/yuva",)

# Reject nodes whose plain text is huge (usually a section wrapper or document root).
_MAX_CARD_TEXT_CHARS = 4000

# Titles that indicate a skeleton/loading state or a page wrapper rather than a real event.
# Cards that render these strings before JS hydration pollute the scrape output
# (e.g. Chakradhar's Week 10 diagnostic caught one "Loading Event Details" row).
_PLACEHOLDER_TITLE_RE = re.compile(
    r"^\s*(loading|untitled|tbd|coming soon|event details?|no title)\b",
    re.IGNORECASE,
)

_SERIALIZED_EVENT_BLOCK_RE = re.compile(
    r'\\"id\\":\d+,\\"attributes\\":\{.*?\}\}(?=,\{\\"id\\":|])',
    re.IGNORECASE | re.DOTALL,
)


def _is_placeholder_title(title: str | None) -> bool:
    if not title:
        return True
    return bool(_PLACEHOLDER_TITLE_RE.match(title))

@dataclass(frozen=True)
class JkyogScrapeResult:
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


def _now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


def _should_include_event_context(text: str) -> bool:
    """Include all non-empty candidate events (no city-specific filtering)."""
    return bool((text or "").strip())


def _rich_card_context_text(card: BeautifulSoup) -> str:
    """
    Include a few ancestor levels so date/location lines split across DOM nodes still
    parse correctly. Bounded so a wrong root node does not pull in the whole page.
    """
    chunks: List[str] = []
    seen: set[str] = set()
    node: BeautifulSoup | None = card
    for _ in range(3):
        if node is None:
            break
        raw = node.get_text(" ", strip=True) if hasattr(node, "get_text") else ""
        txt = " ".join(raw.split())
        if txt and txt not in seen:
            chunks.append(txt)
            seen.add(txt)
        node = getattr(node, "parent", None)
    return " ".join(chunks)


def _decode_escaped_text(raw: str | None) -> str:
    if not raw:
        return ""
    t = raw.replace(r"\/", "/")
    t = t.replace(r"\\", "\\")
    try:
        return codecs.decode(t, "unicode_escape").strip()
    except Exception:
        return t.strip()


def _normalize_iso_utc(value: str | None) -> str | None:
    if not value:
        return None
    try:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"
    except Exception:
        return None


def _extract_escaped_field(blob: str, key: str) -> str:
    m = re.search(rf'\\"{re.escape(key)}\\":\\"(.*?)\\"', blob, re.IGNORECASE | re.DOTALL)
    return _decode_escaped_text(m.group(1)) if m else ""


def _extract_embedded_upcoming_events(html: str, page_url: str) -> List[Dict[str, Any]]:
    """
    Parse Next.js serialized event payload embedded in the upcoming_events page.
    This captures the canonical cards (All/Events/Retreats/LTP) even when the DOM
    selectors pick wrappers or mixed content nodes.
    """
    out: List[Dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    for block_match in _SERIALIZED_EVENT_BLOCK_RE.finditer(html):
        block = block_match.group(0)
        title = _extract_escaped_field(block, "EventTitle")
        if _is_placeholder_title(title):
            continue

        subtitle = _extract_escaped_field(block, "EventSubtitle")
        website_url = _extract_escaped_field(block, "WebsiteURL")
        slug = _extract_escaped_field(block, "EventURLSlug")
        uuid_value = _extract_escaped_field(block, "uuid")
        city_m = re.search(r'\\"city\\":\\"(?P<city>.*?)\\"', block, re.IGNORECASE | re.DOTALL)
        address_m = re.search(r'\\"address\\":\\"(?P<addr>.*?)\\"', block, re.IGNORECASE | re.DOTALL)
        city = _decode_escaped_text(city_m.group("city") if city_m else "")
        address = _decode_escaped_text(address_m.group("addr") if address_m else "")
        event_location = _extract_escaped_field(block, "EventLocation")
        tz_name = _extract_escaped_field(block, "TimeZone")

        context = " ".join(
            part for part in (title, subtitle, city, address, event_location, tz_name) if part
        )
        if not _should_include_event_context(context):
            continue

        start_iso = _normalize_iso_utc(_extract_escaped_field(block, "StartTime"))
        end_iso = _normalize_iso_utc(_extract_escaped_field(block, "EndTime"))
        if not start_iso:
            continue

        key = (title.lower(), start_iso, website_url.lower(), slug.lower(), uuid_value.lower())
        if key in seen:
            continue
        seen.add(key)

        normalized_source_url: str
        if website_url:
            normalized_source_url = website_url
        elif slug:
            normalized_source_url = urljoin(JKYOG_SITE_URL + "/", slug.lstrip("/"))
        elif uuid_value:
            normalized_source_url = f"{page_url}#event-{uuid_value}"
        else:
            normalized_source_url = page_url

        out.append(
            {
                "name": title,
                "description": subtitle or None,
                "start_datetime": start_iso,
                "end_datetime": end_iso,
                "location_name": "JKYog Radha Krishna Temple",
                "parking_notes": None,
                "food_info": None,
                "sponsorship_tiers": [],
                "image_url": None,
                "source_url": normalized_source_url,
                "source_site": "jkyog",
                "is_recurring": False,
                "category": guess_event_category(" ".join(x for x in (title, subtitle) if x)),
                "notes": context or None,
                "scraped_at": _now_iso_z(),
            }
        )
    return out


def _filter_card_nodes(nodes: List[BeautifulSoup]) -> List[BeautifulSoup]:
    out: List[BeautifulSoup] = []
    for node in nodes:
        if node.find_parent("nav") or node.find_parent("header") or node.find_parent("footer"):
            continue
        raw = node.get_text(" ", strip=True) if hasattr(node, "get_text") else ""
        if len(raw) > _MAX_CARD_TEXT_CHARS:
            continue
        if not raw.strip():
            continue
        out.append(node)
    return out


def _extract_event_cards(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """
    Prefer Webflow/CMS list rows and Next.js carousel items; avoid leading with ``[class*='event']``,
    which matches large wrappers on jkyog.org (Next + Tailwind).
    """
    selectors = (
        "main .w-dyn-list .w-dyn-item",
        ".w-dyn-list .w-dyn-item",
        "main section ul.flex > li",
        "main ul.flex > li",
        "main article",
        "[class*='w-dyn-item']",
        "[class*='collection-item']",
        "[class*='event-item']",
        "article",
    )
    for sel in selectors:
        found = soup.select(sel)
        filtered = _filter_card_nodes(found)
        if len(filtered) >= 2:
            return filtered
    for sel in selectors:
        found = soup.select(sel)
        filtered = _filter_card_nodes(found)
        if len(filtered) == 1:
            return filtered

    narrow = _filter_card_nodes(soup.select("main [class*='event'], main [class*='Event']"))
    if narrow:
        return narrow

    broad = _filter_card_nodes(soup.select("[class*='event'], [class*='Event']"))
    if broad:
        return broad

    fallback = [
        a
        for a in soup.select("a[href]")
        if re.search(r"event", a.get("href") or "", re.IGNORECASE) and len(a.get_text(" ", strip=True) or "") <= _MAX_CARD_TEXT_CHARS
    ]
    return fallback


def _dedupe_jkyog_urls(urls: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for u in urls:
        u = u.strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def _is_jkyog_http_url(url: str) -> bool:
    p = urlparse(url.strip())
    if p.scheme.lower() not in ("http", "https"):
        return False
    host = p.netloc.lower().split(":")[0]
    return host == "www.jkyog.org" or host == "jkyog.org"


def scrape_jkyog_upcoming_events(
    *,
    client: RespectfulHttpClient,
    calendar_url: str = DEFAULT_JKYOG_CALENDAR_URL,
    extra_page_urls: Optional[Sequence[str]] = None,
    max_events: int = 50,
) -> JkyogScrapeResult:
    errors: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []

    if extra_page_urls is None:
        extras = list(DEFAULT_JKYOG_EXTRA_PAGE_URLS)
    else:
        extras = list(extra_page_urls)

    page_urls = _dedupe_jkyog_urls([calendar_url] + [u for u in extras if u and u != calendar_url])

    for page_url in page_urls:
        if not _is_jkyog_http_url(page_url):
            logger.warning("Skipping non-JKYog page URL: %s", page_url)
            continue
        try:
            html = client.get_text(page_url)
        except Exception as exc:
            logger.exception("Failed to fetch JKYog page: %s", exc)
            errors.append({"source": "jkyog", "stage": "fetch_calendar", "url": page_url, "error": str(exc)})
            continue

        soup = BeautifulSoup(html, "lxml")
        if "/upcoming_events" in page_url:
            embedded_events = _extract_embedded_upcoming_events(html, page_url)
            if embedded_events:
                for e in embedded_events:
                    if len(events) >= max_events:
                        break
                    events.append(e)
                if len(events) >= max_events:
                    break
                # Continue to next page; embedded payload is canonical for this route.
                continue

        cards = _extract_event_cards(soup)
        for card in cards:
            if len(events) >= max_events:
                break
            try:
                card_text = _clean_text(card.get_text(" ", strip=True)) or ""
                rich_text = _clean_text(_rich_card_context_text(card)) or card_text
                if not _should_include_event_context(rich_text):
                    continue

                link = None
                a = card.select_one("a[href]") if hasattr(card, "select_one") else None
                if a and a.get("href"):
                    link = urljoin(page_url, a.get("href"))

                title = None
                if hasattr(card, "select_one"):
                    title_node = card.select_one("h1, h2, h3, [class*='title']")
                    if title_node:
                        title = _clean_text(title_node.get_text(" ", strip=True))
                title = title or _clean_text(rich_text.split("|")[0]) or "Untitled Event"

                start_dt, end_dt = extract_event_datetimes(rich_text)
                if not start_dt and link:
                    try:
                        detail_html = client.get_text(link)
                        detail_soup = BeautifulSoup(detail_html, "lxml")
                        detail_blob = detail_soup.get_text("\n", strip=True)
                        start_dt, end_dt = extract_event_datetimes(detail_blob)
                    except Exception as fetch_exc:
                        logger.debug("JKYog detail fetch skipped for %s: %s", link, fetch_exc)

                events.append(
                    {
                        "name": title,
                        "description": None,
                        "start_datetime": start_dt,
                        "end_datetime": end_dt,
                        "location_name": "JKYog Radha Krishna Temple",
                        "parking_notes": None,
                        "food_info": None,
                        "sponsorship_tiers": [],
                        "image_url": None,
                        "source_url": link or page_url,
                        "source_site": "jkyog",
                        "is_recurring": False,
                        "category": guess_event_category(rich_text or card_text or title or ""),
                        "notes": rich_text or card_text or None,
                        "scraped_at": _now_iso_z(),
                    }
                )
            except Exception as exc:
                logger.exception("Failed to parse JKYog event card: %s", exc)
                errors.append({"source": "jkyog", "stage": "parse_card", "url": page_url, "error": str(exc)})
                continue

        if len(events) >= max_events:
            break

    if not events:
        errors.append(
            {"source": "jkyog", "stage": "filter", "url": calendar_url, "error": "No events found"}
        )

    return JkyogScrapeResult(events=events, errors=errors)

