"""
Seed the events database from a scraped JSON file.

After a successful upsert, refreshes the in-process knowledge base index via
`ingest_events` (see `knowledge_base/ingestion.py`) and returns `kb_events_ingested`
in the stats dict.

Usage:
    # Normal mode — load scraped_events.json
    python -m scripts.seed_from_scraped_json

    # Fixture mode — use the committed snapshot (see data/scraped_events.fixture.json)
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
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy.orm import Session

try:
    from ..events.services.event_query_cache import invalidate_events_cache
    from ..events.storage.event_storage import upsert_events
    from ..knowledge_base.ingestion import ingest_events
    from ..database.schema import Event
except ImportError:
    from events.services.event_query_cache import invalidate_events_cache
    from events.storage.event_storage import upsert_events
    from knowledge_base.ingestion import ingest_events
    from database.schema import Event

logger = logging.getLogger(__name__)

# Default paths
_DATA_DIR = _week_dir / "data"
_DEFAULT_INPUT = _DATA_DIR / "scraped_events.json"
# Committed dev snapshot (not live scrape output); safe to version-control.
_FIXTURE_INPUT = _DATA_DIR / "scraped_events.fixture.json"
_DEFAULT_MANAGED_SOURCE_SITES: Tuple[str, ...] = ("jkyog", "radhakrishnatemple")


def _strip_fixture_meta(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-ingestion keys (fixture disclaimers, tooling metadata)."""
    return {k: v for k, v in obj.items() if not k.startswith("__")}


def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = _strip_fixture_meta(payload)
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    cleaned: List[Dict[str, Any]] = []
    for item in events:
        if isinstance(item, dict):
            cleaned.append(_strip_fixture_meta(item))
    return cleaned


def _event_key(source_site: Any, source_url: Any) -> Tuple[str, str]:
    site_value = getattr(source_site, "value", source_site)
    site = str(site_value or "").strip().lower()
    url = str(source_url or "").strip()
    return site, url


def _prune_missing_events(
    db: Session,
    *,
    fresh_events: List[Dict[str, Any]],
    managed_source_sites: Tuple[str, ...],
    dry_run: bool,
) -> Dict[str, int]:
    managed = {site.strip().lower() for site in managed_source_sites if site and site.strip()}
    if not managed:
        return {"pruned_candidates": 0, "pruned_deleted": 0}

    fresh_keys: Set[Tuple[str, str]] = set()
    for event in fresh_events:
        site, url = _event_key(event.get("source_site"), event.get("source_url"))
        if site in managed and url:
            fresh_keys.add((site, url))

    existing_rows = (
        db.query(Event.id, Event.source_site, Event.source_url)
        .filter(Event.source_site.in_(list(managed)))
        .all()
    )

    stale_ids: List[int] = []
    for row in existing_rows:
        site, url = _event_key(row.source_site, row.source_url)
        if not url:
            stale_ids.append(int(row.id))
            continue
        if (site, url) not in fresh_keys:
            stale_ids.append(int(row.id))

    deleted = 0
    if stale_ids and not dry_run:
        deleted = (
            db.query(Event)
            .filter(Event.id.in_(stale_ids))
            .delete(synchronize_session=False)
        )
        db.commit()

    return {
        "pruned_candidates": len(stale_ids),
        "pruned_deleted": int(deleted),
    }


def seed_from_file(
    db: Session,
    input_path: str,
    *,
    prune_missing: bool = False,
    prune_dry_run: bool = False,
) -> Dict[str, int]:
    """Load events from *input_path*, upsert into DB, optionally prune stale rows, refresh KB, invalidate cache."""
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    if prune_missing:
        prune_stats = _prune_missing_events(
            db,
            fresh_events=events,
            managed_source_sites=_DEFAULT_MANAGED_SOURCE_SITES,
            dry_run=prune_dry_run,
        )
        stats.update(prune_stats)
        if prune_dry_run:
            logger.info(
                "Prune dry-run complete: %d candidates (no deletes applied)",
                prune_stats["pruned_candidates"],
            )
    else:
        stats["pruned_candidates"] = 0
        stats["pruned_deleted"] = 0
    invalidate_events_cache()
    ingested = ingest_events(db)
    stats["kb_events_ingested"] = ingested
    return stats


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the events database from scraped JSON."
    )
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Use the committed data/scraped_events.fixture.json snapshot for offline "
             "dev testing without re-scraping live websites.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a custom JSON file to seed from.",
    )
    parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="Delete existing scraper-managed DB rows not present in this seed input. "
             "Default behavior remains non-destructive when omitted.",
    )
    parser.add_argument(
        "--dry-run-prune",
        action="store_true",
        help="Show prune candidates without deleting rows (requires --prune-missing).",
    )
    args = parser.parse_args()
    if args.dry_run_prune and not args.prune_missing:
        parser.error("--dry-run-prune requires --prune-missing")

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
        stats = seed_from_file(
            db,
            str(input_path),
            prune_missing=args.prune_missing,
            prune_dry_run=args.dry_run_prune,
        )
        print(f"Seed complete: {stats}")
    except Exception:
        logger.exception("Seed failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
