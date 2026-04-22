"""Offline tests for events.scrapers.datetime_extract."""

from events.scrapers.datetime_extract import (
    extract_event_datetimes,
    is_valid_storage_datetime,
    parse_storage_datetime,
)


def test_parse_storage_datetime_z() -> None:
    dt = parse_storage_datetime("2026-04-04T10:00:00Z")
    assert dt is not None
    assert dt.tzinfo is None
    assert dt.year == 2026 and dt.month == 4 and dt.day == 4


def test_parse_storage_datetime_offset() -> None:
    dt = parse_storage_datetime("2026-04-04T10:00:00-05:00")
    assert dt is not None
    assert dt.tzinfo is None


def test_is_valid_storage_datetime_rejects_empty() -> None:
    assert is_valid_storage_datetime(None) is False
    assert is_valid_storage_datetime("") is False


def test_extract_iso_from_text() -> None:
    text = "Join us on 2026-04-04T14:30:00Z for the fair."
    start, end = extract_event_datetimes(text)
    assert start is not None
    assert end is None
    assert is_valid_storage_datetime(start)


def test_extract_march_range_same_month() -> None:
    text = "Chaitra Navratri Mar 19-29, 2026 at the temple."
    start, end = extract_event_datetimes(text)
    assert start is not None
    assert end is not None
    assert is_valid_storage_datetime(start)
    assert is_valid_storage_datetime(end)


def test_extract_april_date_phrase() -> None:
    text = "Health Fair — April 4, 2026 — Allen, TX"
    start, end = extract_event_datetimes(text)
    assert start is not None
    assert is_valid_storage_datetime(start)


def test_extract_ordinal_month_day_year() -> None:
    text = "Hanuman Jayanti Apr 1st, 2026, 06:00 PM — Apr 4th, 2026, 10:30 AM"
    start, end = extract_event_datetimes(text)
    assert start is not None
    assert is_valid_storage_datetime(start)


def test_extract_same_month_range_without_year() -> None:
    text = "RKT Spiritual Retreat & Family Camp 2026 Jul 4th – Jul 10th Allen, US"
    start, end = extract_event_datetimes(text)
    assert start is not None and end is not None
    sdt = parse_storage_datetime(start)
    edt = parse_storage_datetime(end)
    assert sdt is not None and edt is not None
    assert sdt.month == 7 and sdt.day == 4
    assert edt.month == 7 and edt.day == 10


def test_extract_cross_month_range_without_year() -> None:
    text = "Sacramento Life Transformation Program Apr 30th – May 2nd, In Person"
    start, end = extract_event_datetimes(text)
    assert start is not None and end is not None
    sdt = parse_storage_datetime(start)
    edt = parse_storage_datetime(end)
    assert sdt is not None and edt is not None
    assert sdt.month == 4 and sdt.day == 30
    assert edt.month == 5 and edt.day == 2


def test_extract_returns_none_for_empty() -> None:
    assert extract_event_datetimes("") == (None, None)
    assert extract_event_datetimes("   ") == (None, None)
