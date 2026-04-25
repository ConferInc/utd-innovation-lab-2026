"""Offline tests for JKYog Dallas/Allen row matching."""

from events.scrapers.jkyog import _looks_like_dallas_event


def test_address_fragments() -> None:
    assert _looks_like_dallas_event("1450 North Watters Road Allen")
    assert _looks_like_dallas_event("75013")


def test_allen_with_texas_not_tx() -> None:
    assert _looks_like_dallas_event("Venue in Allen, Texas")


def test_allen_with_temple_context_without_state() -> None:
    assert _looks_like_dallas_event("Radha Krishna Temple Allen weekend")


def test_dallas_with_temple_context() -> None:
    assert _looks_like_dallas_event("Radha Krishna Temple of Dallas")


def test_dallas_with_allen() -> None:
    assert _looks_like_dallas_event("Dallas Allen retreat at temple")


def test_negative_unrelated_dallas() -> None:
    assert not _looks_like_dallas_event("Unrelated flight to Dallas only")
