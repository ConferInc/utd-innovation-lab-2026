from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .http_client import RespectfulHttpClient

logger = logging.getLogger(__name__)


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
    t = text.lower()
    return (TEMPLE_ADDRESS_FRAGMENT in t) or (TEMPLE_CITY_FRAGMENT in t and "tx" in t)


def _extract_event_cards(soup: BeautifulSoup) -> List[BeautifulSoup]:
    # This page structure can change; use broad heuristics.
    cards = soup.select("[class*='event'], [class*='Event']")
    if cards:
        return cards
    # Fallback to links that look like event detail pages.
    return [a for a in soup.select("a[href]") if re.search(r"event", a.get("href") or "", re.IGNORECASE)]


def scrape_jkyog_upcoming_events(
    *,
    client: RespectfulHttpClient,
    calendar_url: str = "https://jkyog.org/upcoming_events",
    max_events: int = 50,
) -> JkyogScrapeResult:
    errors: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []

    try:
        html = client.get_text(calendar_url)
    except Exception as exc:
        logger.exception("Failed to fetch JKYog upcoming events: %s", exc)
        return JkyogScrapeResult(
            events=[],
            errors=[{"source": "jkyog", "stage": "fetch_calendar", "url": calendar_url, "error": str(exc)}],
        )

    soup = BeautifulSoup(html, "lxml")
    cards = _extract_event_cards(soup)
    for card in cards[:max_events]:
        try:
            card_text = _clean_text(card.get_text(" ", strip=True)) or ""
            if not _looks_like_dallas_event(card_text):
                continue

            link = None
            a = card.select_one("a[href]") if hasattr(card, "select_one") else None
            if a and a.get("href"):
                link = urljoin(calendar_url, a.get("href"))

            title = None
            if hasattr(card, "select_one"):
                title_node = card.select_one("h1, h2, h3, [class*='title']")
                if title_node:
                    title = _clean_text(title_node.get_text(" ", strip=True))
            title = title or _clean_text(card_text.split("|")[0]) or "Untitled Event"

            # JKYog pages often include date/time strings but parsing is inconsistent.
            # Emit null start/end unless an ISO-like datetime is present.
            start_dt = None
            iso_match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?", card_text)
            if iso_match:
                start_dt = iso_match.group(0)

            events.append(
                {
                    "name": title,
                    "description": None,
                    "start_datetime": start_dt,
                    "end_datetime": None,
                    "location": "JKYog Radha Krishna Temple",
                    "venue_details": None,
                    "parking_notes": None,
                    "food_info": None,
                    "sponsorship_data": [],
                    "image_url": None,
                    "source_url": link or calendar_url,
                    "source_site": "jkyog",
                    "is_recurring": False,
                    "recurrence_pattern": None,
                    "category": None,
                    "special_notes": card_text or None,
                    "scraped_at": _now_iso_z(),
                }
            )
        except Exception as exc:
            logger.exception("Failed to parse JKYog event card: %s", exc)
            errors.append({"source": "jkyog", "stage": "parse_card", "url": calendar_url, "error": str(exc)})
            continue

    if not events:
        errors.append({"source": "jkyog", "stage": "filter", "url": calendar_url, "error": "No Dallas/Allen events found"})

    return JkyogScrapeResult(events=events, errors=errors)

