"""Unit tests for EventQueryCache TTL + LRU eviction."""

from __future__ import annotations

import time

from week8.events.services.event_query_cache import EventQueryCache


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
