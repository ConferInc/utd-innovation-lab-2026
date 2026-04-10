"""
Event storage layer — upsert, query, deduplication.

Two-stage dedup with per-upsert savepoints and deterministic SHA-256 keying.
Schema aligned with Team 4A (Chanakya) canonical event model —
sponsorship_tiers use {tier_name, price, description}.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

try:
    from ...database.schema import Event, EventSourceSite
    from ..schemas.event_payload import EventPayload
except ImportError:
    from database.schema import Event, EventSourceSite
    from events.schemas.event_payload import EventPayload


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


def _coerce_bool(value: Any) -> Optional[bool]:
    """Coerce a value to bool or None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"true", "1", "yes"}:
            return True
        if lower in {"false", "0", "no", ""}:
            return False
    return bool(value)


def _validate_sponsorship_tiers(value: Any) -> List[Dict[str, Any]]:
    """Validate sponsorship tiers using aligned format {tier_name, price, description}."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_tiers must be a list of sponsorship tier objects")

    validated: List[Dict[str, Any]] = []

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"sponsorship_tiers[{index}] must be an object with tier_name, price, description")

        tier_name = item.get("tier_name")
        if not isinstance(tier_name, str) or not tier_name.strip():
            raise ValueError(f"sponsorship_tiers[{index}].tier_name must be a non-empty string")

        price = item.get("price")
        if price is not None:
            try:
                price = float(price)
            except (TypeError, ValueError):
                raise ValueError(f"sponsorship_tiers[{index}].price must be a number or null")

        description = _clean_optional_text(item.get("description"))

        validated.append({
            "tier_name": tier_name.strip(),
            "price": price,
            "description": description,
        })

    return validated


def _validate_price(value: Any) -> Dict[str, Any]:
    """Validate price object {amount, notes}."""
    if value is None:
        return {"amount": None, "notes": None}
    if not isinstance(value, dict):
        raise ValueError("price must be an object with keys: amount, notes")
    result: Dict[str, Any] = {}
    amount = value.get("amount")
    if amount is not None:
        try:
            result["amount"] = float(amount)
        except (TypeError, ValueError):
            raise ValueError("price.amount must be a number or null")
    else:
        result["amount"] = None
    result["notes"] = _clean_optional_text(value.get("notes"))
    return result


def _coerce_price_for_api(value: Any) -> Dict[str, Any]:
    """Return canonical price shape for API output, even for bad stored values."""
    if value is None:
        return {"amount": None, "notes": None}
    if not isinstance(value, dict):
        logger.warning("Invalid stored price type %s; returning null price shape", type(value).__name__)
        return {"amount": None, "notes": None}

    amount_raw = value.get("amount")
    if amount_raw is None:
        amount = None
    else:
        try:
            amount = float(amount_raw)
        except (TypeError, ValueError):
            logger.warning("Invalid stored price.amount value %r; returning null amount", amount_raw)
            amount = None

    return {
        "amount": amount,
        "notes": _clean_optional_text(value.get("notes")),
    }


# ---------------------------------------------------------------------------
# Dedup key
# ---------------------------------------------------------------------------

def build_dedup_key(name: str, start_datetime: datetime, location_name: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location_name),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Payload normalization
# ---------------------------------------------------------------------------

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Normalize and validate a raw event payload dict for database insertion.

    Handles both the old format (location, special_notes, sponsorship_data)
    and the new aligned format (location_name, notes, sponsorship_tiers)
    for backwards compatibility during the migration period.
    """
    canonical_payload = dict(payload)
    if canonical_payload.get("location_name") in (None, "") and canonical_payload.get("location"):
        canonical_payload["location_name"] = canonical_payload.get("location")
    if canonical_payload.get("notes") in (None, "") and canonical_payload.get("special_notes"):
        canonical_payload["notes"] = canonical_payload.get("special_notes")
    if canonical_payload.get("sponsorship_tiers") is None and canonical_payload.get("sponsorship_data") is not None:
        canonical_payload["sponsorship_tiers"] = canonical_payload.get("sponsorship_data")
    if canonical_payload.get("recurrence_text") in (None, "") and canonical_payload.get("recurrence_pattern"):
        canonical_payload["recurrence_text"] = canonical_payload.get("recurrence_pattern")
    if not canonical_payload.get("scraped_at"):
        canonical_payload["scraped_at"] = default_scraped_at or _now()

    parsed = EventPayload.model_validate(canonical_payload)

    name = parsed.name
    source_url = str(parsed.source_url)
    start_datetime = _parse_datetime(parsed.start_datetime)
    if start_datetime is None:
        raise ValueError("start_datetime is required")
    end_datetime = _parse_datetime(parsed.end_datetime)
    scraped_at = _parse_datetime(parsed.scraped_at) or _now()
    source_site = _coerce_source_site(parsed.source_site)
    location_name = _clean_optional_text(parsed.location_name)
    notes = _clean_optional_text(parsed.notes)
    sponsorship_tiers = _validate_sponsorship_tiers(parsed.model_dump().get("sponsorship_tiers"))
    price = _validate_price(parsed.model_dump().get("price"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location_name=location_name)

    return {
        # Identity
        "name": name,
        "subtitle": _clean_optional_text(payload.get("subtitle")),
        "description": _clean_optional_text(payload.get("description")),
        # Categorization
        "category": _clean_optional_text(parsed.category),
        "event_type": _clean_optional_text(parsed.event_type),
        # Recurrence
        "is_recurring": bool(parsed.is_recurring),
        "recurrence_pattern": _clean_optional_text(parsed.recurrence_text),
        "recurrence_text": _clean_optional_text(parsed.recurrence_text),
        # Date / Time
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "timezone": _clean_optional_text(parsed.timezone),
        # Location
        "location_name": location_name,
        "address": _clean_optional_text(parsed.address),
        "city": _clean_optional_text(parsed.city),
        "state": _clean_optional_text(parsed.state),
        "postal_code": _clean_optional_text(parsed.postal_code),
        "country": _clean_optional_text(parsed.country),
        # Registration
        "registration_required": _coerce_bool(parsed.registration_required),
        "registration_status": _clean_optional_text(parsed.registration_status),
        "registration_url": _clean_optional_text(parsed.registration_url),
        # Contact
        "contact_email": _clean_optional_text(parsed.contact_email),
        "contact_phone": _clean_optional_text(parsed.contact_phone),
        # Logistics
        "parking_notes": _clean_optional_text(parsed.parking_notes),
        "transportation_notes": _clean_optional_text(parsed.transportation_notes),
        "food_info": _clean_optional_text(parsed.food_info),
        # Pricing & Sponsorship
        "price": price,
        "sponsorship_tiers": sponsorship_tiers,
        # Source metadata
        "source_url": source_url,
        "source_site": source_site,
        "source_page_type": _clean_optional_text(parsed.source_page_type),
        "image_url": _clean_optional_text(canonical_payload.get("image_url")),
        "scraped_at": scraped_at,
        "source_confidence": _clean_optional_text(parsed.source_confidence),
        # Notes
        "notes": notes,
        # Dedup
        "dedup_key": dedup_key,
    }


# ---------------------------------------------------------------------------
# Staleness
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        # Identity
        "id": event.id,
        "name": event.name,
        "subtitle": event.subtitle,
        "description": event.description,
        # Categorization
        "category": event.category,
        "event_type": event.event_type,
        # Recurrence
        "is_recurring": event.is_recurring,
        "recurrence_text": event.recurrence_text,
        # Date / Time
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "timezone": event.timezone,
        # Location
        "location_name": event.location_name,
        "address": event.address,
        "city": event.city,
        "state": event.state,
        "postal_code": event.postal_code,
        "country": event.country,
        # Registration
        "registration_required": event.registration_required,
        "registration_status": event.registration_status,
        "registration_url": event.registration_url,
        # Contact
        "contact_email": event.contact_email,
        "contact_phone": event.contact_phone,
        # Logistics
        "parking_notes": event.parking_notes,
        "transportation_notes": event.transportation_notes,
        "food_info": event.food_info,
        # Pricing & Sponsorship
        "price": _coerce_price_for_api(event.price),
        "sponsorship_tiers": event.sponsorship_tiers if event.sponsorship_tiers else [],
        # Source
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "source_page_type": event.source_page_type,
        "image_url": event.image_url,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "source_confidence": event.source_confidence,
        # Notes
        "notes": event.notes,
        # Timestamps
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


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

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
    """
    Paginated upcoming events: one-off sessions that have not ended, plus recurring
    programs that are still active (no end date or end in the future).

    Non-recurring rows sort before recurring so near-term dated events surface first.
    """
    now = now_utc or _now()
    one_off_upcoming = and_(
        Event.is_recurring.is_(False),
        or_(
            Event.start_datetime >= now,
            and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
        ),
    )
    recurring_active = and_(
        Event.is_recurring.is_(True),
        or_(Event.end_datetime.is_(None), Event.end_datetime >= now),
    )
    return (
        db.query(Event)
        .filter(or_(one_off_upcoming, recurring_active))
        .order_by(Event.is_recurring.asc(), Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )


def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    """Check whether a recurring event is active on *reference_dt*.

    Supported patterns: daily, weekdays, weekends, weekly:<dayname>.
    Unsupported patterns now log a warning (previously silently returned False).
    """
    if not event.is_recurring:
        return False
    pattern = _normalize_text(event.recurrence_text)
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

    logger.warning(
        "Unsupported recurrence_text %r for event id=%s name=%r — treating as inactive",
        event.recurrence_text,
        event.id,
        event.name,
    )
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
    name_match = Event.name.ilike(like_pattern)
    return (
        db.query(Event)
        .filter(
            or_(
                name_match,
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.notes.ilike(like_pattern),
            )
        )
        .order_by(
            case((name_match, 0), else_=1),
            Event.start_datetime.asc(),
            Event.id.asc(),
        )
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
