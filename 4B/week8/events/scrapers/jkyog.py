"""JKYog.org upcoming-events scraper — static HTML only.

Fetches public pages with ``httpx`` and parses cards with BeautifulSoup. Rows
that are injected purely via JavaScript after load will not be present in the
fetched HTML and are therefore skipped without raising an error.

When debugging empty results, compare against the live site in a browser with
JS enabled; if content only appears after scripts run, plan a Playwright or
Selenium-based fetch before expanding parsers here.

Scraped event payload schema
----------------------------
Each dict appended to ``JkyogScrapeResult.events`` (and later bundled into
``scraped_events.json`` by ``events.scrapers.scrape_all.scrape_all_events``)
uses exactly the keys below. The downstream Pydantic ``EventPayload`` /
``events.storage`` pipeline enforces these invariants; producing a value that
violates them will cause the row to be rejected at validation time.

Guaranteed (never None):
    name: str                    - Human title; placeholder titles (``Loading
                                   Event Details``, ``Untitled`` ...) are
                                   filtered out before emission.
    location_name: str           - Always ``"JKYog Radha Krishna Temple"``.
    source_url: str              - Either the event detail URL or the page URL
                                   the card was scraped from.
    source_site: str             - Always ``"jkyog"``.
    is_recurring: bool           - Always ``False`` for scraper output; the
                                   recurring ingester handles periodic programs
                                   separately.
    category: Category literal   - One of ``festival | retreat | satsang |
                                   youth | class | workshop | health |
                                   special_event | other`` (see
                                   ``category_from_title.guess_event_category``).
    sponsorship_tiers: list      - Always ``[]`` from the scraper; populated
                                   downstream when known.
    scraped_at: str              - ISO-8601 UTC with ``Z`` suffix.

Nullable (may be ``None`` - downstream treats ``None`` as "unknown"):
    description: Optional[str]
    start_datetime: Optional[str] - ISO-8601; rows with ``None`` are dropped by
                                    ``scrape_all_events`` (counted in
                                    ``failed_start_datetime_parse``).
    end_datetime: Optional[str]   - ISO-8601; populated for multi-day ranges
                                    (``Mar 26-29, 2026``). ``None`` for
                                    single-day events.
    parking_notes: Optional[str]
    food_info: Optional[str]
    image_url: Optional[str]
    notes: Optional[str]          - Full card text for debugging.

Pydantic validation will reject null ``start_datetime``, unknown ``category``
literals, and any field with the wrong type. See ``events.schemas`` for the
authoritative contract.
"""

from __future__ import annotations

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
# Extra JKYog pages to scrape for Dallas-area rows (e.g. YUVA / UTD). Merged with ``upcoming_events``.
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


def _is_placeholder_title(title: str | None) -> bool:
    if not title:
        return True
    return bool(_PLACEHOLDER_TITLE_RE.match(title))


@dataclass(frozen=True)
class JkyogScrapeResult:
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


TEMPLE_ADDRESS_FRAGMENT = "1450 north watters road"
TEMPLE_CITY_FRAGMENT = "allen"


def _now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


def _looks_like_dallas_event(text: str) -> bool:
    """Match Dallas / Allen RKT rows; allow Allen + Texas without requiring ``TX``."""
    t = text.lower()
    if TEMPLE_ADDRESS_FRAGMENT in t or "north watters" in t:
        return True
    if "75013" in t:
        return True
    if TEMPLE_CITY_FRAGMENT in t and ("tx" in t or "texas" in t):
        return True
    if TEMPLE_CITY_FRAGMENT in t and any(
        x in t for x in ("temple", "radha", "krishna", "rkt", "dallas", "watters", "1450")
    ):
        return True
    if "dallas" in t and any(
        x in t
        for x in ("temple", "radha", "krishna", "rkt", "allen", "tx", "texas", "75013", "watters")
    ):
        return True
    if "radha krishna temple" in t and "dallas" in t:
        return True
    if "temple of dallas" in t or "rkt dallas" in t:
        return True
    return False


def _rich_card_context_text(card: BeautifulSoup) -> str:
    """
    Include a few ancestor levels so venue lines split across DOM nodes still match the Dallas
    filter and date extraction sees full copy. Bounded (fewer levels than before) so a wrong
    root node does not pull in the whole page.
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
        cards = _extract_event_cards(soup)
        for card in cards:
            if len(events) >= max_events:
                break
            try:
                card_text = _clean_text(card.get_text(" ", strip=True)) or ""
                rich_text = _clean_text(_rich_card_context_text(card)) or card_text
                if not _looks_like_dallas_event(rich_text):
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
                title = title or _clean_text(rich_text.split("|")[0])

                if _is_placeholder_title(title):
                    errors.append(
                        {
                            "source": "jkyog",
                            "stage": "placeholder_title",
                            "url": page_url,
                            "error": f"Skipped card with placeholder title: {title!r}",
                        }
                    )
                    continue

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
            {"source": "jkyog", "stage": "filter", "url": calendar_url, "error": "No Dallas/Allen events found"}
        )

    return JkyogScrapeResult(events=events, errors=errors)

