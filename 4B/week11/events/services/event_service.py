"""
Application-facing API for stored temple events.

Assignment naming (for graders): getUpcomingEvents, getTodayEvents, searchEvents,
getEventById, getRecurringSchedule map to get_upcoming_events, get_today_events,
search_events, get_event_by_id, get_recurring_events.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..storage import event_storage
from .event_query_cache import EventQueryCache


class EventService:
    def __init__(self, db: Session, cache: Optional[EventQueryCache] = None) -> None:
        self._db = db
        self._cache = cache

    def _use_cache(self, *, now_utc: Optional[datetime]) -> bool:
        return (
            self._cache is not None
            and self._cache.ttl_seconds > 0
            and now_utc is None
        )

    def get_upcoming_events(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        key = ("upcoming", limit, offset)
        if self._use_cache(now_utc=now_utc):
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        rows = event_storage.get_upcoming_events(self._db, limit=limit, offset=offset, now_utc=now_utc)
        out = event_storage.serialize_events(rows, now_utc=now_utc, stale_after_days=stale_after_days)
        if self._use_cache(now_utc=now_utc):
            self._cache.set(key, out)
        return out

    def get_today_events(
        self,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        key = ("today",)
        if self._use_cache(now_utc=now_utc):
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        rows = event_storage.get_today_events(self._db, now_utc=now_utc)
        out = event_storage.serialize_events(rows, now_utc=now_utc, stale_after_days=stale_after_days)
        if self._use_cache(now_utc=now_utc):
            self._cache.set(key, out)
        return out

    def get_recurring_events(
        self,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Recurring programs schedule (assignment: getRecurringSchedule)."""
        key = ("recurring",)
        if self._use_cache(now_utc=now_utc):
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        rows = event_storage.get_recurring_events(self._db)
        out = event_storage.serialize_events(rows, now_utc=now_utc, stale_after_days=stale_after_days)
        if self._use_cache(now_utc=now_utc):
            self._cache.set(key, out)
        return out

    def search_events(
        self,
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        key = ("search", query.strip().lower(), limit, offset)
        if self._use_cache(now_utc=now_utc):
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        rows = event_storage.search_events(self._db, query, limit=limit, offset=offset)
        out = event_storage.serialize_events(rows, now_utc=now_utc, stale_after_days=stale_after_days)
        if self._use_cache(now_utc=now_utc):
            self._cache.set(key, out)
        return out

    def get_event_by_id(
        self,
        event_id: int,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        key = ("by_id", event_id)
        if self._use_cache(now_utc=now_utc):
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        row = event_storage.get_event_by_id(self._db, event_id)
        if row is None:
            return None
        out = event_storage.event_to_dict(row, now_utc=now_utc, stale_after_days=stale_after_days)
        if self._use_cache(now_utc=now_utc):
            self._cache.set(key, out)
        return out
