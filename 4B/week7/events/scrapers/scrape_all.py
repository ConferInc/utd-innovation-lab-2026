from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .http_client import RespectfulHttpClient, ScraperConfig
from .jkyog import scrape_jkyog_upcoming_events
from .radhakrishnatemple import scrape_radhakrishnatemple

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
    temple_homepage_url: str = "https://radhakrishnatemple.net/",
    jkyog_calendar_url: str = "https://jkyog.org/upcoming_events",
    config: Optional[ScraperConfig] = None,
) -> Dict[str, Any]:
    """
    Scrape both sources and return a DB-friendly payload bundle.

    Returns:
      {
        "scraped_at": "...Z",
        "events": [ {event_payload}, ... ],
        "errors": [ {source, stage, url, error}, ... ]
      }
    """

    client = RespectfulHttpClient(config=config)
    try:
        temple = scrape_radhakrishnatemple(client=client, homepage_url=temple_homepage_url)
        jkyog = scrape_jkyog_upcoming_events(client=client, calendar_url=jkyog_calendar_url)

        combined: List[Dict[str, Any]] = []
        combined.extend(temple.events)
        combined.extend(jkyog.events)

        # De-dupe across sources in-memory (best-effort). DB upsert layer will do final dedup.
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for event in combined:
            k = _dedup_key(event)
            if k in seen:
                continue
            seen.add(k)
            deduped.append(event)

        return {
            "scraped_at": _now_iso_z(),
            "events": deduped,
            "errors": [*temple.errors, *jkyog.errors],
        }
    finally:
        client.close()

