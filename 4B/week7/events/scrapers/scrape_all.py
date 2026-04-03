from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .datetime_extract import is_valid_storage_datetime
from .http_client import RespectfulHttpClient, ScraperConfig
from .jkyog import DEFAULT_JKYOG_CALENDAR_URL, scrape_jkyog_upcoming_events
from .radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL, scrape_radhakrishnatemple

logger = logging.getLogger(__name__)


def _now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _dedup_key(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    name = str(payload.get("name") or "").strip().lower()
    start = str(payload.get("start_datetime") or "").strip()
    location = str(payload.get("location") or "").strip().lower()
    return (name, start, location)


def scrape_all_events(
    *,
    temple_homepage_url: str = DEFAULT_TEMPLE_HOMEPAGE_URL,
    jkyog_calendar_url: str = DEFAULT_JKYOG_CALENDAR_URL,
    config: Optional[ScraperConfig] = None,
) -> Dict[str, Any]:
    """
    Scrape both sources and return a DB-friendly payload bundle.

    Returns:
      {
        "scraped_at": "...Z",
        "events": [ {event_payload}, ... ],
        "errors": [ {source, stage, url, error}, ... ],
        "skipped_invalid_datetime": int
      }
    """

    client = RespectfulHttpClient(config=config)
    try:
        temple = scrape_radhakrishnatemple(client=client, homepage_url=temple_homepage_url)
        jkyog = scrape_jkyog_upcoming_events(client=client, calendar_url=jkyog_calendar_url)

        combined: List[Dict[str, Any]] = []
        combined.extend(temple.events)
        combined.extend(jkyog.events)

        errors: List[Dict[str, Any]] = [*temple.errors, *jkyog.errors]
        skipped_invalid = 0
        validated: List[Dict[str, Any]] = []
        for event in combined:
            if not is_valid_storage_datetime(event.get("start_datetime")):
                skipped_invalid += 1
                errors.append(
                    {
                        "source": event.get("source_site", "unknown"),
                        "stage": "missing_or_invalid_start_datetime",
                        "url": event.get("source_url", ""),
                        "name": event.get("name"),
                        "detail": "start_datetime missing or not parseable by storage layer",
                    }
                )
                continue
            validated.append(event)

        # De-dupe across sources in-memory (best-effort). DB upsert layer will do final dedup.
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for event in validated:
            k = _dedup_key(event)
            if k in seen:
                continue
            seen.add(k)
            deduped.append(event)

        return {
            "scraped_at": _now_iso_z(),
            "events": deduped,
            "errors": errors,
            "skipped_invalid_datetime": skipped_invalid,
        }
    finally:
        client.close()

