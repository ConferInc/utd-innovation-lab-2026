"""Radha Krishna Temple (Allen) event scraper — static HTML only.

This module uses ``httpx`` + BeautifulSoup to parse server-rendered HTML. Any
event listings or calendars that are built client-side with JavaScript will
not appear in the DOM we fetch, so those events are silently missed (no error).

If this scraper suddenly returns far fewer events than expected, first verify
the upstream site did not switch to a JS-rendered calendar or move content
behind different URLs.

Upgrade path for JS-heavy sites: drive a headless browser (Playwright or
Selenium), wait for selectors, then parse the rendered HTML or intercept XHR
JSON responses.

Scraped event payload schema
----------------------------
Each dict appended to ``TempleScrapeResult.events`` (and later bundled into
``scraped_events.json`` by ``events.scrapers.scrape_all.scrape_all_events``)
uses exactly the keys below. Downstream Pydantic ``EventPayload`` and
``events.storage`` enforce these invariants; values that break them cause the
row to be rejected at validation time.

Guaranteed (never None):
    name: str                    - Extracted from the detail page title;
                                   placeholder titles (``Loading Event
                                   Details`` ...) are filtered before emission.
    location_name: str           - Always ``"JKYog Radha Krishna Temple"``.
    source_url: str              - The ``/event/<slug>`` detail page URL, or
                                   a supplemental public event URL.
    source_site: str             - Always ``"radhakrishnatemple"``.
    is_recurring: bool           - Always ``False`` from the scraper.
    category: Category literal   - One of ``festival | retreat | satsang |
                                   youth | class | workshop | health |
                                   special_event | other`` (see
                                   ``category_from_title.guess_event_category``).
    sponsorship_tiers: list      - Always ``[]`` from the scraper; populated
                                   downstream when known.
    scraped_at: str              - ISO-8601 UTC with ``Z`` suffix.

Nullable (may be ``None``):
    description: Optional[str]    - ``meta[name=description]`` or first
                                    article paragraph.
    start_datetime: Optional[str] - ISO-8601; rows with ``None`` are dropped by
                                    ``scrape_all_events`` (counted in
                                    ``failed_start_datetime_parse``).
    end_datetime: Optional[str]   - ISO-8601; populated for multi-day ranges
                                    parsed from phrases like ``Mar 26-29,
                                    2026``. ``None`` for single-day events.
    parking_notes: Optional[str]
    food_info: Optional[str]
    image_url: Optional[str]      - From ``meta[property=og:image]`` if present.
    notes: Optional[str]          - Full ``.entry-content`` / ``article`` text.

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
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from .category_from_title import guess_event_category
from .datetime_extract import extract_event_datetimes
from .http_client import RespectfulHttpClient

logger = logging.getLogger(__name__)

# Canonical public URLs (www)
DEFAULT_TEMPLE_HOMEPAGE_URL = "https://www.radhakrishnatemple.net/"
TEMPLE_UPCOMING_EVENTS_URL = "https://www.radhakrishnatemple.net/upcoming-events"
RKT_CALENDAR_PDF_URL = (
    "https://d11n2py6p6cfxh.cloudfront.net/2026_RKT_Calendar_fe7bae1910.pdf"
)

# Curated public event pages (Webflow-style paths; not under /event/<slug>). Merged with
# homepage-discovered /event/... links. See normalize_explicit_temple_event_url.
DEFAULT_SUPPLEMENTAL_TEMPLE_EVENT_URLS: Tuple[str, ...] = (
    "https://www.radhakrishnatemple.net/hanuman-jayanti",
    "https://www.radhakrishnatemple.net/community-health-fair-biometric-screening",
    "https://www.radhakrishnatemple.net/annamacharya-aradhanotsavam-dallas",
    "https://www.radhakrishnatemple.net/community-cleanup",
    "https://www.radhakrishnatemple.net/gita-parayanam",
    "https://www.radhakrishnatemple.net/bhakti-kirtan-retreat",
    "https://www.radhakrishnatemple.net/akshaya-tritiya",
    "https://www.radhakrishnatemple.net/hindu-vivah-dallas",
)


@dataclass(frozen=True)
class TempleScrapeResult:
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


# Titles that indicate a pre-hydration skeleton or a non-event landing page. Keeping a
# single source of truth here so both homepage-discovered and supplemental detail pages
# are filtered uniformly. Mirrors the jkyog.py regex - keep them in sync.
_PLACEHOLDER_TITLE_RE = re.compile(
    r"^\s*(loading|untitled|tbd|coming soon|event details?|no title)\b",
    re.IGNORECASE,
)


def _is_placeholder_title(title: Optional[str]) -> bool:
    if not title:
        return True
    return bool(_PLACEHOLDER_TITLE_RE.match(title))


def _now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


def _extract_first(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    for sel in selectors:
        node = soup.select_one(sel)
        if node:
            text = _clean_text(node.get_text(" ", strip=True))
            if text:
                return text
    return None


def _host_only(netloc: str) -> str:
    return netloc.lower().split(":")[0]


def _is_radhakrishna_host(netloc: str) -> bool:
    """True if netloc is radhakrishnatemple.net or a subdomain (e.g. www)."""
    h = _host_only(netloc)
    return h == "radhakrishnatemple.net" or h.endswith(".radhakrishnatemple.net")


def _is_junk_temple_path(path: str) -> bool:
    """
    Paths that are hubs, Webflow slider indices, or galleries — not event detail pages.
    Crawling these yields 404s or pages with no parseable event datetime.
    """
    if not path:
        return True
    low = path.lower()
    if "events-photo-gallery" in low:
        return True
    pl = path.rstrip("/") or "/"
    if pl in ("/events", "/upcoming-events"):
        return True
    if re.match(r"^/events-\d+$", pl, re.IGNORECASE):
        return True
    return False


def _is_event_detail_path(path: str) -> bool:
    """Webflow-style single event pages: /event/<slug> (singular ``event``)."""
    pl = (path or "").rstrip("/")
    return bool(re.match(r"^/event/[^/]+$", pl, re.IGNORECASE))


def _path_key(path: str) -> str:
    return (path or "").rstrip("/") or "/"


_SUPPLEMENTAL_PATH_KEYS: frozenset[str] = frozenset(
    _path_key(urlparse(u).path) for u in DEFAULT_SUPPLEMENTAL_TEMPLE_EVENT_URLS
)


def _is_supplemental_path(path: str) -> bool:
    return _path_key(path) in _SUPPLEMENTAL_PATH_KEYS


def normalize_explicit_temple_event_url(url: str) -> Optional[str]:
    """
    Validate a full URL for a temple event detail page: either ``/event/<slug>`` or a
    path in ``DEFAULT_SUPPLEMENTAL_TEMPLE_EVENT_URLS``. Used for curated lists; homepage
    href normalization still uses _finalize_temple_url (``/event/`` only).
    """
    raw = (url or "").strip()
    if not raw:
        return None
    p = urlparse(raw)
    if p.scheme.lower() not in ("http", "https"):
        return None
    netloc = p.netloc.lower()
    if not _is_radhakrishna_host(netloc):
        return None
    path = p.path or "/"
    if _is_junk_temple_path(path):
        return None
    if not (_is_event_detail_path(path) or _is_supplemental_path(path)):
        return None
    pk = _path_key(path)
    return urlunparse(("https", netloc, pk if pk != "/" else "/", "", "", ""))


def _merge_unique_temple_urls(primary: List[str], secondary: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for u in primary + secondary:
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def _normalize_temple_href(base_url: str, href: str) -> Optional[str]:
    """
    Resolve href against the temple base URL, fix broken protocol-relative links where
    the site uses ``//event/...`` (parsed as host ``event``), and drop off-site URLs.
    """
    h = (href or "").strip()
    if not h or h.startswith("#"):
        return None
    low = h.lower()
    if low.startswith(("javascript:", "mailto:", "tel:", "data:")):
        return None

    base_p = urlparse(base_url)
    scheme = (base_p.scheme or "https").lower()
    if scheme not in ("http", "https"):
        scheme = "https"
    base_host = base_p.netloc.lower()
    if not base_host:
        return None

    joined = urljoin(base_url, h)
    p = urlparse(joined)
    if p.scheme.lower() not in ("http", "https"):
        return None

    netloc = p.netloc.lower()
    path = p.path or ""
    query = p.query
    fragment = p.fragment

    if _is_radhakrishna_host(netloc):
        out_path = path if path else "/"
        if _is_junk_temple_path(out_path):
            return None
        cand = urlunparse((scheme, netloc, out_path, p.params, query, fragment))
        return _finalize_temple_url(cand)

    # ``urljoin`` turns ``//event/slug`` into https://event/slug — single-label "host".
    host_only = _host_only(netloc)
    if "." not in host_only:
        if not host_only:
            return None
        new_path = "/" + host_only.rstrip("/")
        if path and path != "/":
            new_path += path if path.startswith("/") else "/" + path
        fixed = urlunparse((scheme, base_host, new_path, "", query, fragment))
        fp = urlparse(fixed)
        if _is_radhakrishna_host(fp.netloc):
            return _finalize_temple_url(fixed)
        return None

    return None


def _finalize_temple_url(url: str) -> Optional[str]:
    """Drop junk paths; keep only same-host /event/<slug> detail URLs."""
    p = urlparse(url)
    path = p.path or ""
    if not _is_radhakrishna_host(p.netloc):
        return None
    if _is_junk_temple_path(path):
        return None
    if not _is_event_detail_path(path):
        return None
    return url


def _append_temple_link(links: List[str], base_url: str, href: Optional[str]) -> None:
    url = _normalize_temple_href(base_url, href or "")
    if url:
        links.append(url)


def _extract_event_links_from_homepage(home_html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(home_html, "lxml")
    links: List[str] = []

    # Heuristic: capture links in carousel-like regions first.
    for container_sel in [
        "[class*='carousel']",
        "[id*='carousel']",
        ".carousel",
        ".slider",
        ".swiper",
    ]:
        for a in soup.select(f"{container_sel} a[href]"):
            href = a.get("href")
            if not href:
                continue
            _append_temple_link(links, base_url, href)

    # Fallback: detail URLs use the singular /event/<slug> path (not "events", gallery, etc.).
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        low = href.lower()
        if "/event/" in low or low.startswith("//event/"):
            _append_temple_link(links, base_url, href)

    # De-dupe while preserving order.
    seen = set()
    deduped = []
    for url in links:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def _parse_detail_page(detail_html: str, *, url: str) -> Optional[Dict[str, Any]]:
    soup = BeautifulSoup(detail_html, "lxml")

    title = _extract_first(soup, ["h1", "h2", ".entry-title", "[class*='title']"])
    if _is_placeholder_title(title):
        return None

    description = _extract_first(
        soup,
        [
            "meta[name='description']",
            ".entry-content p",
            "article p",
            ".content p",
        ],
    )

    # Attempt to find an image.
    image_url = None
    og_img = soup.select_one("meta[property='og:image']")
    if og_img and og_img.get("content"):
        image_url = og_img.get("content")

    body_text = soup.get_text("\n", strip=True)
    text_blob = "\n".join(
        part
        for part in (title, description or "", body_text)
        if part
    )
    start_dt, end_dt = extract_event_datetimes(text_blob)

    notes = _extract_first(
        soup,
        [
            ".entry-content",
            "article",
        ],
    )

    return {
        "name": title,
        "description": description,
        "start_datetime": start_dt,
        "end_datetime": end_dt,
        "location_name": "JKYog Radha Krishna Temple",
        "parking_notes": None,
        "food_info": None,
        "sponsorship_tiers": [],
        "image_url": image_url,
        "source_url": url,
        "source_site": "radhakrishnatemple",
        "is_recurring": False,
        "category": guess_event_category(title),
        "notes": notes,
        "scraped_at": _now_iso_z(),
    }


def scrape_radhakrishnatemple(
    *,
    client: RespectfulHttpClient,
    homepage_url: str = DEFAULT_TEMPLE_HOMEPAGE_URL,
    supplemental_event_urls: Optional[Sequence[str]] = None,
    max_events: int = 20,
) -> TempleScrapeResult:
    errors: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []

    try:
        home_html = client.get_text(homepage_url)
    except Exception as exc:
        logger.exception("Failed to fetch temple homepage: %s", exc)
        return TempleScrapeResult(
            events=[],
            errors=[{"source": "radhakrishnatemple", "stage": "fetch_homepage", "url": homepage_url, "error": str(exc)}],
        )

    if supplemental_event_urls is None:
        supplemental_urls = DEFAULT_SUPPLEMENTAL_TEMPLE_EVENT_URLS
    else:
        supplemental_urls = tuple(supplemental_event_urls)

    explicit: List[str] = []
    for u in supplemental_urls:
        nu = normalize_explicit_temple_event_url(u)
        if nu:
            explicit.append(nu)
        else:
            logger.warning("Skipping invalid supplemental temple URL: %s", u)

    discovered = _extract_event_links_from_homepage(home_html, homepage_url)
    links = _merge_unique_temple_urls(explicit, discovered)[:max_events]
    if not links:
        errors.append(
            {"source": "radhakrishnatemple", "stage": "parse_homepage", "url": homepage_url, "error": "No event links found"}
        )
        return TempleScrapeResult(events=[], errors=errors)

    for url in links:
        try:
            detail_html = client.get_text(url)
            payload = _parse_detail_page(detail_html, url=url)
            if payload is None:
                errors.append(
                    {
                        "source": "radhakrishnatemple",
                        "stage": "placeholder_title",
                        "url": url,
                        "error": "Skipped detail page with placeholder/loading title",
                    }
                )
                continue
            events.append(payload)
        except httpx.HTTPStatusError as exc:
            err = str(exc)
            if exc.response is not None and exc.response.status_code == 404:
                logger.warning("Temple detail page not found (404) url=%s", url)
            else:
                logger.exception("Failed to fetch temple detail page url=%s err=%s", url, exc)
            errors.append({"source": "radhakrishnatemple", "stage": "parse_detail", "url": url, "error": err})
            continue
        except Exception as exc:
            logger.exception("Failed to parse temple detail page url=%s err=%s", url, exc)
            errors.append({"source": "radhakrishnatemple", "stage": "parse_detail", "url": url, "error": str(exc)})
            continue

    return TempleScrapeResult(events=events, errors=errors)

