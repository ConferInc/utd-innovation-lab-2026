from __future__ import annotations

import sys
from pathlib import Path

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..events.services.event_query_cache import invalidate_events_cache
    from ..events.storage.event_storage import upsert_events
except ImportError:
    from events.services.event_query_cache import invalidate_events_cache
    from events.storage.event_storage import upsert_events

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_FIXTURE_INPUT = _DATA_DIR / "scraped_events.fixture.json"


def _strip_fixture_meta(obj: Dict[str, Any]) -> Dict[str, Any]:
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


def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    invalidate_events_cache()
    return stats
