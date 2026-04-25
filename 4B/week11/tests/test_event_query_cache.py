"""Unit tests for EventQueryCache TTL + LRU eviction."""

from __future__ import annotations

import time
from pathlib import Path
import sys

_4B_ROOT = Path(__file__).resolve().parents[2]
_WEEK8_ROOT = Path(__file__).resolve().parents[1]
for p in (str(_WEEK8_ROOT), str(_4B_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from events.services.event_query_cache import (
        EventQueryCache,
        get_shared_event_query_cache,
        reset_shared_event_query_cache_for_tests,
    )
except ImportError:
    from week8.events.services.event_query_cache import (
        EventQueryCache,
        get_shared_event_query_cache,
        reset_shared_event_query_cache_for_tests,
    )


def test_lru_evicts_oldest_when_max_size_exceeded() -> None:
    cache = EventQueryCache(ttl_seconds=300.0, max_size=3)
    cache.set(("a",), "A")
    cache.set(("b",), "B")
    cache.set(("c",), "C")
    assert cache.get(("a",)) == "A"
    cache.set(("d",), "D")
    assert cache.get(("b",)) is None
    assert cache.get(("a",)) == "A"
    assert cache.get(("c",)) == "C"
    assert cache.get(("d",)) == "D"


def test_get_refreshes_lru_order() -> None:
    cache = EventQueryCache(ttl_seconds=300.0, max_size=3)
    for key in ("a", "b", "c"):
        cache.set((key,), key.upper())
    cache.get(("a",))
    cache.set(("d",), "D")
    assert cache.get(("b",)) is None
    assert cache.get(("a",)) == "A"


def test_ttl_expires_entries() -> None:
    cache = EventQueryCache(ttl_seconds=0.05, max_size=100)
    cache.set(("x",), 42)
    assert cache.get(("x",)) == 42
    time.sleep(0.06)
    assert cache.get(("x",)) is None


def test_zero_ttl_skips_cache() -> None:
    cache = EventQueryCache(ttl_seconds=0.0, max_size=10)
    cache.set(("a",), 1)
    assert cache.get(("a",)) is None


def test_zero_max_size_disables_eviction_cap() -> None:
    cache = EventQueryCache(ttl_seconds=60.0, max_size=0)
    for i in range(10):
        cache.set((i,), i)
    assert len(cache._store) == 10  # noqa: SLF001


def test_shared_cache_honors_max_size_and_lru_on_first_create() -> None:
    reset_shared_event_query_cache_for_tests()
    shared = get_shared_event_query_cache(max_size=2)
    shared.set(("a",), "A")
    shared.set(("b",), "B")
    assert shared.get(("a",)) == "A"  # refresh a => b becomes LRU
    shared.set(("c",), "C")
    assert shared.get(("b",)) is None
    assert shared.get(("a",)) == "A"
    assert shared.get(("c",)) == "C"


def test_lru_boundary_evicts_oldest_and_keeps_newest() -> None:
    """Week 10 explicit boundary: insert max_size+1 and verify eviction."""
    cache = EventQueryCache(ttl_seconds=300.0, max_size=3)
    cache.set(("k1",), "v1")
    cache.set(("k2",), "v2")
    cache.set(("k3",), "v3")
    cache.set(("k4",), "v4")

    assert cache.get(("k1",)) is None  # oldest evicted
    assert cache.get(("k2",)) == "v2"
    assert cache.get(("k3",)) == "v3"
    assert cache.get(("k4",)) == "v4"  # newest retained
