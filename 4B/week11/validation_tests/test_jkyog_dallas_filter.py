"""Offline tests for inclusive JKYog event context filtering."""

from events.scrapers.jkyog import _should_include_event_context


def test_includes_general_non_dallas_event_text() -> None:
    assert _should_include_event_context("Weekend bhajans in Houston")


def test_includes_dallas_like_event_text() -> None:
    assert _should_include_event_context("Radha Krishna Temple of Dallas")


def test_rejects_empty_or_whitespace_context() -> None:
    assert not _should_include_event_context("")
    assert not _should_include_event_context("   ")
