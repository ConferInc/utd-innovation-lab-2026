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
