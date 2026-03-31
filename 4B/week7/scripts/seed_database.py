from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

from database.models import SessionLocal, init_db


def _load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input JSON not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        events = raw.get("events", [])
    elif isinstance(raw, list):
        events = raw
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    return [item for item in events if isinstance(item, dict)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        events = _load_events(Path(args.input).resolve())

        try:
            from database.event_storage import upsert_events  # type: ignore
        except Exception:
            upsert_events = None  # type: ignore

        if upsert_events is None:
            print(f"Loaded {len(events)} events from JSON. Upsert layer not available yet.")
            print("Waiting for database.event_storage.upsert_events to be implemented.")
            return

        stats = upsert_events(db, events)
        stats["input_count"] = len(events)
        print("Seed complete")
        print(f"Input events: {stats['input_count']}")
        print(f"Inserted: {stats.get('inserted', 0)}")
        print(f"Updated: {stats.get('updated', 0)}")
        print(f"Failed: {stats.get('failed', 0)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

