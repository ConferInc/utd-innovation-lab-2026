from __future__ import annotations

import sys
from pathlib import Path

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import argparse

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file


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
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")


if __name__ == "__main__":
    main()
