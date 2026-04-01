from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

try:
    from ...database.schema import Event, EventSourceSite
except ImportError:
    from database.schema import Event, EventSourceSite


WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")


def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")


def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_data must be a list of sponsorship tier objects")

    validated: List[Dict[str, str]] = []
    required_fields = ("name", "amount", "link")

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"sponsorship_data[{index}] must be an object with name, amount, and link")

        normalized_item: Dict[str, str] = {}
        for field in required_fields:
            raw_value = item.get(field)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(f"sponsorship_data[{index}].{field} must be a non-empty string")
            normalized_item[field] = raw_value.strip()

        validated.append(normalized_item)

    return validated


def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
    sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }


def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))


def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(event.scraped_at, now_utc=now_utc, stale_after_days=stale_after_days)
        if event.scraped_at
        else False,
    }


def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days) for event in events]


def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()


def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()
    if existing is None:
        existing = (
            db.query(Event)
            .filter(Event.source_site == values["source_site"], Event.source_url == values["source_url"])
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action


def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            logger.exception(
                "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                payload.get("name"),
                payload.get("source_url"),
                payload.get("source_site"),
                extra={
                    "event_name": payload.get("name"),
                    "source_url": payload.get("source_url"),
                    "source_site": payload.get("source_site"),
                },
            )
            stats["failed"] += 1

    db.commit()
    return stats


def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}


def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()


def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(Event.start_datetime >= now, and_(Event.end_datetime.isnot(None), Event.end_datetime >= now)),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )


def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False
    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]
    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name
    return False


def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )


def get_today_events(db: Session, *, now_utc: Optional[datetime] = None) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(Event.start_datetime >= start_of_day, Event.start_datetime < end_of_day),
                and_(Event.end_datetime.isnot(None), Event.start_datetime < end_of_day, Event.end_datetime >= start_of_day),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [event for event in get_recurring_events(db) if _matches_recurrence(event, now)]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(combined_by_id.values(), key=lambda event: (event.start_datetime or datetime.min, event.id))


def search_events(db: Session, query: str, *, limit: int = 10, offset: int = 0) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
