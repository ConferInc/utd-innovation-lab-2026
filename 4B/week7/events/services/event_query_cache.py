"""In-process TTL cache for EventService query results."""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Hashable, Optional

_cache_lock = threading.Lock()
_shared_cache: Optional[EventQueryCache] = None


def _env_ttl_seconds() -> float:
    raw = os.getenv("EVENT_CACHE_TTL_SECONDS")
    if raw is None:
        return 60.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 60.0


class EventQueryCache:
    """Simple thread-safe TTL cache keyed by tuples of hashable arguments."""

    def __init__(self, ttl_seconds: float = 60.0) -> None:
        self._ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    @property
    def ttl_seconds(self) -> float:
        return self._ttl_seconds

    @staticmethod
    def _key_str(key: tuple[Hashable, ...]) -> str:
        return repr(key)

    def get(self, key: tuple[Hashable, ...]) -> Any | None:
        if self._ttl_seconds <= 0:
            return None
        k = self._key_str(key)
        now = time.monotonic()
        with _cache_lock:
            entry = self._store.get(k)
            if entry is None:
                return None
            expires_at, value = entry
            if now >= expires_at:
                del self._store[k]
                return None
            return value

    def set(self, key: tuple[Hashable, ...], value: Any) -> None:
        if self._ttl_seconds <= 0:
            return
        k = self._key_str(key)
        expires_at = time.monotonic() + self._ttl_seconds
        with _cache_lock:
            self._store[k] = (expires_at, value)

    def invalidate_all(self) -> None:
        with _cache_lock:
            self._store.clear()


def get_shared_event_query_cache() -> EventQueryCache:
    """Singleton used by FastAPI and invalidated after DB seed from scraped JSON."""
    global _shared_cache
    with _cache_lock:
        if _shared_cache is None:
            _shared_cache = EventQueryCache(ttl_seconds=_env_ttl_seconds())
        return _shared_cache


def invalidate_events_cache() -> None:
    """Clear all cached event query entries (call after upserting scraped data)."""
    get_shared_event_query_cache().invalidate_all()


def reset_shared_event_query_cache_for_tests() -> None:
    """Drop the process-wide singleton so the next access picks up a fresh TTL from env."""
    global _shared_cache
    with _cache_lock:
        _shared_cache = None
