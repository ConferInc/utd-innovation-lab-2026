"""Offline tests for events.scrapers.datetime_extract."""

import warnings

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


def test_extract_returns_none_for_empty() -> None:
    assert extract_event_datetimes("") == (None, None)
    assert extract_event_datetimes("   ") == (None, None)


def test_extract_handles_cst_abbreviation() -> None:
    """CST (UTC-6) must convert to UTC, not be dropped or treated as local default."""
    text = "Community Kirtan April 10, 2026 at 6:00 PM CST"
    start, _end = extract_event_datetimes(text)
    assert start is not None
    dt = parse_storage_datetime(start)
    assert dt is not None
    # 6:00 PM CST -> 00:00 next day UTC
    assert dt.year == 2026 and dt.month == 4 and dt.day == 11
    assert dt.hour == 0 and dt.minute == 0


def test_extract_handles_est_abbreviation() -> None:
    """EST (UTC-5) must round-trip to the correct UTC moment."""
    text = "Satsang April 10, 2026 at 8:00 PM EST"
    start, _end = extract_event_datetimes(text)
    assert start is not None
    dt = parse_storage_datetime(start)
    assert dt is not None
    # 8:00 PM EST -> 01:00 next day UTC
    assert dt.year == 2026 and dt.month == 4 and dt.day == 11
    assert dt.hour == 1


def test_extract_handles_pst_abbreviation() -> None:
    text = "Retreat April 10, 2026 at 5:00 PM PST"
    start, _end = extract_event_datetimes(text)
    assert start is not None
    dt = parse_storage_datetime(start)
    assert dt is not None
    # 5:00 PM PST -> 01:00 next day UTC
    assert dt.year == 2026 and dt.month == 4 and dt.day == 11
    assert dt.hour == 1


def test_extract_does_not_emit_unknown_timezone_warning_for_known_abbrevs() -> None:
    """The Week 10 diagnostic ran hot with UnknownTimezoneWarning for CST/EST/PST/T."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        extract_event_datetimes("Class April 10, 2026 at 6 PM CST")
        extract_event_datetimes("Class 2026-04-10T18:00 EST")
        extract_event_datetimes("Workshop April 10, 2026 at 6 PM PST")
    messages = " ".join(str(w.message) for w in caught)
    assert "CST" not in messages
    assert "EST" not in messages
    assert "PST" not in messages
