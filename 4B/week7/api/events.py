"""HTTP API for scraped / stored temple events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.models import get_db
from ..events.storage.event_storage import (
    event_to_dict,
    get_event_by_id,
    get_recurring_events,
    get_today_events,
    get_upcoming_events,
    search_events,
    serialize_events,
)

router = APIRouter(tags=["events"])

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 100


def _validate_pagination(limit: int, offset: int) -> None:
    if limit < 1 or limit > _MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"limit must be between 1 and {_MAX_LIMIT}",
        )
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")


@router.get("")
def list_upcoming_events(
    db: Session = Depends(get_db),
    limit: int = Query(_DEFAULT_LIMIT),
    offset: int = Query(0),
) -> Dict[str, Any]:
    """All upcoming events (paginated): active one-offs and active recurring programs."""
    _validate_pagination(limit, offset)
    rows = get_upcoming_events(db, limit=limit, offset=offset)
    return {
        "events": serialize_events(rows),
        "limit": limit,
        "offset": offset,
    }


@router.get("/today")
def list_today_events(db: Session = Depends(get_db)) -> Dict[str, List[Dict[str, Any]]]:
    """Today's one-off events plus recurring programs active today."""
    rows = get_today_events(db)
    return {"events": serialize_events(rows)}


@router.get("/recurring")
def list_recurring_programs(db: Session = Depends(get_db)) -> Dict[str, List[Dict[str, Any]]]:
    """All recurring programs."""
    rows = get_recurring_events(db)
    return {"events": serialize_events(rows)}


@router.get("/search")
def search_event_list(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    limit: int = Query(_DEFAULT_LIMIT),
    offset: int = Query(0),
) -> Dict[str, Any]:
    """Case-insensitive search on name, description, category, and special notes."""
    if q is None or not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Query parameter 'q' is required and must be non-empty",
        )
    _validate_pagination(limit, offset)
    rows = search_events(db, q, limit=limit, offset=offset)
    return {
        "events": serialize_events(rows),
        "limit": limit,
        "offset": offset,
        "q": q.strip(),
    }


@router.get("/{event_id}")
def get_event_detail(event_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Single event by primary key."""
    event = get_event_by_id(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_to_dict(event)
