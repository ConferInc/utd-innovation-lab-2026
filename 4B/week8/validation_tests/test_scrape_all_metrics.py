"""Tests for scrape_all._compute_metrics, focused on the Week 10 parse-rate field."""

from __future__ import annotations

import pytest

from events.scrapers.scrape_all import _compute_metrics


def _event(*, name: str, site: str, start: str | None, category: str = "other") -> dict:
    return {
        "name": name,
        "source_site": site,
        "start_datetime": start,
        "category": category,
    }


def test_compute_metrics_exposes_start_datetime_parse_rate() -> None:
    combined = [
        _event(name="A", site="jkyog", start="2026-05-01T00:00:00Z"),
        _event(name="B", site="jkyog", start="2026-05-02T00:00:00Z"),
        _event(name="C", site="radhakrishnatemple", start=None),
    ]
    validated = [c for c in combined if c["start_datetime"]]
    deduped = validated
    metrics = _compute_metrics(
        combined=combined,
        validated=validated,
        deduped=deduped,
        skipped_invalid=1,
        errors=[],
    )
    assert "start_datetime_parse_rate" in metrics
    rate = metrics["start_datetime_parse_rate"]
    assert isinstance(rate, float)
    assert 0.0 <= rate <= 1.0
    # 2 of 3 parsed -> ~0.6667
    assert rate == pytest.approx(2 / 3, rel=1e-3)


def test_compute_metrics_parse_rate_handles_empty_input() -> None:
    metrics = _compute_metrics(
        combined=[],
        validated=[],
        deduped=[],
        skipped_invalid=0,
        errors=[],
    )
    assert metrics["start_datetime_parse_rate"] == 0.0
    assert metrics["total_scraped"] == 0


def test_compute_metrics_parse_rate_all_valid() -> None:
    events = [
        _event(name="A", site="jkyog", start="2026-05-01T00:00:00Z"),
        _event(name="B", site="jkyog", start="2026-05-02T00:00:00Z"),
    ]
    metrics = _compute_metrics(
        combined=events,
        validated=events,
        deduped=events,
        skipped_invalid=0,
        errors=[],
    )
    assert metrics["start_datetime_parse_rate"] == 1.0
