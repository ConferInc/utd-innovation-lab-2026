"""
Seed the events database from a scraped JSON file.

Usage:
    # Normal mode — load scraped_events.json
    python -m scripts.seed_from_scraped_json

    # Fixture mode — use the committed snapshot for offline dev testing
    python -m scripts.seed_from_scraped_json --fixture

    # Custom file
    python -m scripts.seed_from_scraped_json --file path/to/events.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import json
import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..events.services.event_query_cache import invalidate_events_cache
    from ..events.storage.event_storage import upsert_events
except ImportError:
    from events.services.event_query_cache import invalidate_events_cache
    from events.storage.event_storage import upsert_events

logger = logging.getLogger(__name__)

# Default paths
_DATA_DIR = _week_dir / "data"
_DEFAULT_INPUT = _DATA_DIR / "scraped_events.json"
_FIXTURE_INPUT = _DATA_DIR / "scraped_events.json"  # same file, used for --fixture flag


def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]


def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    """Load events from *input_path*, upsert into DB, and invalidate cache."""
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    invalidate_events_cache()
    return stats


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the events database from scraped JSON."
    )
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Use the committed scraped_events.json snapshot for offline dev testing "
             "without re-scraping live websites.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a custom JSON file to seed from.",
    )
    args = parser.parse_args()

    # Determine input file
    if args.file:
        input_path = Path(args.file).resolve()
    elif args.fixture:
        input_path = _FIXTURE_INPUT
        print(f"[fixture mode] Using committed snapshot: {input_path}")
    else:
        input_path = _DEFAULT_INPUT

    # Set up database session
    from database.models import SessionLocal, init_db

    logging.basicConfig(level=logging.INFO)
    init_db()
    db = SessionLocal()

    try:
        stats = seed_from_file(db, str(input_path))
        print(f"Seed complete: {stats}")
    except Exception:
        logger.exception("Seed failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
