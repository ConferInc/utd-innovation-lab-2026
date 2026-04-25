"""In-process TTL cache for EventService query results.

LRU eviction caps memory when many distinct query keys are used; TTL limits staleness.
"""

from __future__ import annotations

import os
import threading
import time
from collections import OrderedDict
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


def _env_max_size(default: int = 500) -> int:
    raw = os.getenv("EVENT_QUERY_CACHE_MAX_SIZE")
    if raw is None:
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


class EventQueryCache:
    """Thread-safe TTL cache with LRU eviction (OrderedDict, O(1) ops per entry)."""

    def __init__(self, ttl_seconds: float = 60.0, max_size: int = 500) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_size = max(0, max_size)
        # key -> (expires_at_monotonic, value); LRU order: oldest at front
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    @property
    def ttl_seconds(self) -> float:
        return self._ttl_seconds

    @property
    def max_size(self) -> int:
        return self._max_size

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
            self._store.move_to_end(k)
            return value

    def set(self, key: tuple[Hashable, ...], value: Any) -> None:
        if self._ttl_seconds <= 0:
            return
        k = self._key_str(key)
        expires_at = time.monotonic() + self._ttl_seconds
        with _cache_lock:
            self._store[k] = (expires_at, value)
            self._store.move_to_end(k)
            while self._max_size and len(self._store) > self._max_size:
                self._store.popitem(last=False)

    def invalidate_all(self) -> None:
        with _cache_lock:
            self._store.clear()


def get_shared_event_query_cache(max_size: int | None = None) -> EventQueryCache:
    """Singleton used by FastAPI and invalidated after DB seed from scraped JSON.

    The optional *max_size* only applies when the singleton is first created; later
    calls return the existing instance. Tests should call ``reset_shared_event_query_cache_for_tests()``
    when a fresh configuration is required.
    """
    global _shared_cache
    resolved_max = _env_max_size() if max_size is None else max(0, max_size)
    with _cache_lock:
        if _shared_cache is None:
            _shared_cache = EventQueryCache(
                ttl_seconds=_env_ttl_seconds(),
                max_size=resolved_max,
            )
        return _shared_cache


def invalidate_events_cache() -> None:
    """Clear all cached event query entries (call after upserting scraped data)."""
    get_shared_event_query_cache().invalidate_all()


def reset_shared_event_query_cache_for_tests() -> None:
    """Drop the process-wide singleton so the next access picks up a fresh cache from env."""
    global _shared_cache
    with _cache_lock:
        _shared_cache = None
