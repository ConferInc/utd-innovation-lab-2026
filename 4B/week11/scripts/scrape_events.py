from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

from events.scrapers.http_client import ScraperConfig
from events.scrapers.jkyog import DEFAULT_JKYOG_CALENDAR_URL
from events.scrapers.radhakrishnatemple import DEFAULT_TEMPLE_HOMEPAGE_URL
from events.scrapers.scrape_all import scrape_all_events


def _default_output_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape temple events and output normalized JSON")
    parser.add_argument("--output", default=str(_default_output_path()), help="Output JSON path")
    parser.add_argument(
        "--temple-url",
        default=os.getenv("RADHAKRISHNA_TEMPLE_HOMEPAGE_URL", DEFAULT_TEMPLE_HOMEPAGE_URL),
        help="Temple homepage URL",
    )
    parser.add_argument(
        "--jkyog-url",
        default=os.getenv("JKYOG_UPCOMING_EVENTS_URL", DEFAULT_JKYOG_CALENDAR_URL),
        help="JKYog upcoming events URL",
    )
    args = parser.parse_args()

    payload = scrape_all_events(
        temple_homepage_url=args.temple_url,
        jkyog_calendar_url=args.jkyog_url,
        config=ScraperConfig(),
    )

    out_path = Path(args.output).resolve()
    _write_json(out_path, payload)
    n_events = len(payload.get("events", []))
    n_skipped = int(payload.get("skipped_invalid_datetime", 0))
    metrics = payload.get("metrics") or {}
    n_scraper_errors = int(metrics.get("scraper_errors_logged", 0))
    print(f"Wrote {n_events} events to {out_path}")
    print(f"Skipped (missing/invalid start_datetime): {n_skipped}")
    print(f"Scraper errors logged: {n_scraper_errors}")
    if metrics:
        parse_rate_pct = float(metrics.get("start_datetime_parse_rate", 0.0)) * 100.0
        print(
            "Scrape quality: "
            f"total={int(metrics.get('total_scraped', 0))} "
            f"parsed_dt={int(metrics.get('passed_start_datetime_parse', 0))} "
            f"parse_rate={parse_rate_pct:.1f}% "
            f"category_not_other={int(metrics.get('passed_category_not_other', 0))} "
            f"duplicates={int(metrics.get('duplicate_count', 0))} "
            f"deduped={int(metrics.get('deduped_event_count', 0))}"
        )
        raw_count_by_site = metrics.get("raw_count_by_source_site") or {}
        if raw_count_by_site:
            summary = ", ".join(
                f"{site}={count}" for site, count in sorted(raw_count_by_site.items())
            )
            print(f"Raw by source_site: {summary}")
        validated_count_by_site = metrics.get("validated_count_by_source_site") or {}
        if validated_count_by_site:
            summary = ", ".join(
                f"{site}={count}" for site, count in sorted(validated_count_by_site.items())
            )
            print(f"Validated by source_site: {summary}")
        deduped_count_by_site = metrics.get("deduped_count_by_source_site") or {}
        if deduped_count_by_site:
            summary = ", ".join(
                f"{site}={count}" for site, count in sorted(deduped_count_by_site.items())
            )
            print(f"Deduped by source_site: {summary}")


if __name__ == "__main__":
    main()

