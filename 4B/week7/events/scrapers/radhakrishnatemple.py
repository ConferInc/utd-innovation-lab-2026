from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .datetime_extract import extract_event_datetimes
from .http_client import RespectfulHttpClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TempleScrapeResult:
    events: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


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


def _guess_category(title: str) -> Optional[str]:
    t = title.lower()
    if "navratri" in t:
        return "navratri"
    if "jayanti" in t:
        return "jayanti"
    if "ram" in t:
        return "ram"
    if "health" in t:
        return "health"
    return None


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
            url = urljoin(base_url, href)
            links.append(url)

    # Fallback: any obvious event links mentioning "event".
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if re.search(r"event", href, re.IGNORECASE):
            links.append(urljoin(base_url, href))

    # De-dupe while preserving order.
    seen = set()
    deduped = []
    for url in links:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def _parse_detail_page(detail_html: str, *, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(detail_html, "lxml")

    title = _extract_first(soup, ["h1", "h2", ".entry-title", "[class*='title']"]) or "Untitled Event"
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

    special_notes = _extract_first(
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
        "location": "JKYog Radha Krishna Temple",
        "venue_details": None,
        "parking_notes": None,
        "food_info": None,
        "sponsorship_data": [],
        "image_url": image_url,
        "source_url": url,
        "source_site": "radhakrishnatemple",
        "is_recurring": False,
        "recurrence_pattern": None,
        "category": _guess_category(title),
        "special_notes": special_notes,
        "scraped_at": _now_iso_z(),
    }


def scrape_radhakrishnatemple(
    *,
    client: RespectfulHttpClient,
    homepage_url: str = "https://radhakrishnatemple.net/",
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

    links = _extract_event_links_from_homepage(home_html, homepage_url)[:max_events]
    if not links:
        errors.append(
            {"source": "radhakrishnatemple", "stage": "parse_homepage", "url": homepage_url, "error": "No event links found"}
        )
        return TempleScrapeResult(events=[], errors=errors)

    for url in links:
        try:
            detail_html = client.get_text(url)
            payload = _parse_detail_page(detail_html, url=url)
            events.append(payload)
        except Exception as exc:
            logger.exception("Failed to parse temple detail page url=%s err=%s", url, exc)
            errors.append({"source": "radhakrishnatemple", "stage": "parse_detail", "url": url, "error": str(exc)})
            # partial failure is allowed; continue
            continue

    return TempleScrapeResult(events=events, errors=errors)

