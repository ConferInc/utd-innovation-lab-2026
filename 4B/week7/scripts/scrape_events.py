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
    n_errors = len(payload.get("errors", []))
    n_skipped = int(payload.get("skipped_invalid_datetime", 0))
    print(f"Wrote {n_events} events to {out_path}")
    if n_skipped:
        print(f"Skipped (missing/invalid start_datetime): {n_skipped}")
    if n_errors:
        print(f"Errors logged: {n_errors}")


if __name__ == "__main__":
    main()

