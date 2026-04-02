"""HTTP API for scraped / stored temple events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.models import get_db
from ..events.services.event_query_cache import get_shared_event_query_cache
from ..events.services.event_service import EventService

router = APIRouter(tags=["events"])

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 100


def get_event_service(db: Session = Depends(get_db)) -> EventService:
    return EventService(db, cache=get_shared_event_query_cache())


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
    service: EventService = Depends(get_event_service),
    limit: int = Query(_DEFAULT_LIMIT),
    offset: int = Query(0),
) -> Dict[str, Any]:
    """All upcoming events (paginated): active one-offs and active recurring programs."""
    _validate_pagination(limit, offset)
    events = service.get_upcoming_events(limit=limit, offset=offset)
    return {
        "events": events,
        "limit": limit,
        "offset": offset,
    }


@router.get("/today")
def list_today_events(service: EventService = Depends(get_event_service)) -> Dict[str, List[Dict[str, Any]]]:
    """Today's one-off events plus recurring programs active today."""
    return {"events": service.get_today_events()}


@router.get("/recurring")
def list_recurring_programs(
    service: EventService = Depends(get_event_service),
) -> Dict[str, List[Dict[str, Any]]]:
    """All recurring programs."""
    return {"events": service.get_recurring_events()}


@router.get("/search")
def search_event_list(
    service: EventService = Depends(get_event_service),
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
    events = service.search_events(q, limit=limit, offset=offset)
    return {
        "events": events,
        "limit": limit,
        "offset": offset,
        "q": q.strip(),
    }


@router.get("/{event_id}")
def get_event_detail(event_id: int, service: EventService = Depends(get_event_service)) -> Dict[str, Any]:
    """Single event by primary key."""
    event = service.get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
