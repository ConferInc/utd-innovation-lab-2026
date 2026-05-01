from __future__ import annotations

from collections import Counter
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .datetime_extract import is_valid_storage_datetime, parse_storage_datetime
from .http_client import RespectfulHttpClient, ScraperConfig
from .jkyog import DEFAULT_JKYOG_CALENDAR_URL, scrape_jkyog_upcoming_events
from .radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL, scrape_radhakrishnatemple

logger = logging.getLogger(__name__)


def _now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _dedup_key(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    name = str(payload.get("name") or "").strip().lower()
    start = str(payload.get("start_datetime") or "").strip()
    location = str(payload.get("location_name") or payload.get("location") or "").strip().lower()
    return (name, start, location)


def _compute_metrics(
    *,
    combined: List[Dict[str, Any]],
    validated: List[Dict[str, Any]],
    deduped: List[Dict[str, Any]],
    skipped_invalid: int,
    rejected_synthetic_second: int,
    errors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    raw_count_by_source_site = Counter(
        str(event.get("source_site") or "unknown") for event in combined
    )
    validated_count_by_source_site = Counter(
        str(event.get("source_site") or "unknown") for event in validated
    )
    deduped_count_by_source_site = Counter(
        str(event.get("source_site") or "unknown") for event in deduped
    )
    passed_category_not_other = sum(
        1 for event in validated if str(event.get("category") or "other").strip().lower() != "other"
    )
    duplicate_count = len(validated) - len(deduped)
    ignored_error_stages = {
        "missing_or_invalid_start_datetime",
        "rejected_synthetic_second",
    }
    scraper_errors_logged = sum(
        1
        for error in errors
        if str(error.get("stage") or "").strip().lower() not in ignored_error_stages
    )
    total_scraped = len(combined)
    # Observability signal for the data-quality funnel (Week 10): share of scraped
    # cards whose start_datetime survived parsing. Complements raw counts so the
    # failure rate is obvious at a glance without division on the consumer side.
    start_datetime_parse_rate = (
        round(len(validated) / total_scraped, 4) if total_scraped else 0.0
    )
    return {
        "total_scraped": total_scraped,
        "passed_start_datetime_parse": len(validated),
        "failed_start_datetime_parse": skipped_invalid,
        "rejected_synthetic_second": rejected_synthetic_second,
        "start_datetime_parse_rate": start_datetime_parse_rate,
        "passed_category_not_other": passed_category_not_other,
        "duplicate_count": duplicate_count,
        "deduped_event_count": len(deduped),
        "raw_count_by_source_site": dict(raw_count_by_source_site),
        "validated_count_by_source_site": dict(validated_count_by_source_site),
        "deduped_count_by_source_site": dict(deduped_count_by_source_site),
        "scraper_errors_logged": scraper_errors_logged,
    }


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
        "skipped_invalid_datetime": int,
        "rejected_synthetic_second": int,
        "metrics": {
          "total_scraped": int,
          "passed_start_datetime_parse": int,
          "failed_start_datetime_parse": int,
          "rejected_synthetic_second": int,
          "start_datetime_parse_rate": float,  # validated / total, in [0.0, 1.0]
          "passed_category_not_other": int,
          "duplicate_count": int,
          "deduped_event_count": int,
          "raw_count_by_source_site": {source_site: int},
          "validated_count_by_source_site": {source_site: int},
          "deduped_count_by_source_site": {source_site: int},
          "scraper_errors_logged": int
        }
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
        rejected_synthetic_second = 0
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
            # Week 11 data-quality guard: real calendar times are minute-granular
            # (HH:MM:00). Non-zero seconds typically come from dateutil fuzzy
            # parsing inheriting `now_local` seconds when source text lacks an
            # explicit time. See Week 10 Task 2 analysis.
            parsed_start = parse_storage_datetime(event.get("start_datetime"))
            if parsed_start is not None and parsed_start.second != 0:
                rejected_synthetic_second += 1
                errors.append(
                    {
                        "source": event.get("source_site", "unknown"),
                        "stage": "rejected_synthetic_second",
                        "url": event.get("source_url", ""),
                        "name": event.get("name"),
                        "detail": (
                            "start_datetime seconds != 0; treated as synthetic "
                            "timestamp from fuzzy parse fallback"
                        ),
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

        metrics = _compute_metrics(
            combined=combined,
            validated=validated,
            deduped=deduped,
            skipped_invalid=skipped_invalid,
            rejected_synthetic_second=rejected_synthetic_second,
            errors=errors,
        )
        logger.info("scrape quality metrics: %s", metrics)

        return {
            "scraped_at": _now_iso_z(),
            "events": deduped,
            "errors": errors,
            "skipped_invalid_datetime": skipped_invalid,
            "rejected_synthetic_second": rejected_synthetic_second,
            "metrics": metrics,
        }
    finally:
        client.close()

