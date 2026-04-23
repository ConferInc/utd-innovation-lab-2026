"""Tests for events.scrapers.category_from_title."""

from __future__ import annotations

import sys
from pathlib import Path

_WEEK = Path(__file__).resolve().parents[1]
if str(_WEEK) not in sys.path:
    sys.path.insert(0, str(_WEEK))

import pytest

from events.scrapers.category_from_title import guess_event_category


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hanuman Jayanti Celebration", "festival"),
        ("Community Health Fair — Biometric Screening", "health"),
        ("Bhakti Kirtan Retreat Weekend", "retreat"),
        ("Weekly Satsang and Aarti", "satsang"),
        ("YUVA UTD Campus Program", "youth"),
        ("Kriya Yoga Meditation Class", "class"),
        ("Two-Day Workshop on Gita", "workshop"),
        ("Guest Speaker Lecture Series", "special_event"),
        ("Random Community Gathering", "other"),
        ("", "other"),
    ],
)
def test_guess_event_category(text: str, expected: str) -> None:
    assert guess_event_category(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        # Week 10: word-boundary regex must reject substring collisions that
        # the pre-regex ``if kw in t`` version silently matched.
        # "class" inside "classical" -> previously bucketed as class.
        ("Classical Music Night", "other"),
        # "class" inside "reclassification" -> previously bucketed as class.
        ("Reclassification Notice", "other"),
        # Plurals that we deliberately added to the keyword tuples must still match.
        ("Morning Prayers and Kirtans", "satsang"),
        ("Weekly Meditation Classes", "class"),
        # "spiritual camp" (compound) is still an explicit keyword for retreat.
        ("Spiritual Camp Weekend", "retreat"),
    ],
)
def test_guess_event_category_word_boundary(text: str, expected: str) -> None:
    assert guess_event_category(text) == expected
