from datetime import datetime, timedelta, timezone

import pytest

from events.storage.event_storage import build_dedup_key, is_event_stale, normalize_event_payload


def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    key_1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    key_2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert key_1 == key_2


def test_normalize_event_payload_parses_required_fields() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-30T12:00:00Z",
        "sponsorship_data": [
            {"name": "Gold Sponsor", "amount": "501", "link": "https://example.org/gold"}
        ],
        "recurrence_text": None,
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]
    assert normalized["sponsorship_tiers"][0]["tier_name"] == "Gold Sponsor"


def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})


def test_normalize_event_payload_rejects_dict_root_sponsorship_data() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "sponsorship_data": {"name": "Gold Sponsor", "amount": "$501", "link": "https://x"},
    }

    with pytest.raises(ValueError):
        normalize_event_payload(payload)


def test_normalize_event_payload_rejects_invalid_sponsorship_tier_item() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "sponsorship_data": [{"name": "Gold Sponsor", "amount": "", "link": "https://x"}],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["sponsorship_tiers"][0]["price"] is None


def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True


def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False


def test_normalize_event_payload_rejects_invalid_source_site() -> None:
    payload = {
        "name": "Hanuman Jayanti",
        "source_url": "https://example.org/hanuman-jayanti",
        "source_site": "unknown_site",
        "start_datetime": "2026-04-04T10:00:00Z",
    }

    with pytest.raises(ValueError):
        normalize_event_payload(payload)


def test_normalize_event_payload_rejects_invalid_datetime_string() -> None:
    payload = {
        "name": "Hanuman Jayanti",
        "source_url": "https://example.org/hanuman-jayanti",
        "source_site": "jkyog",
        "start_datetime": "not-a-datetime",
    }

    with pytest.raises(ValueError):
        normalize_event_payload(payload)


def test_is_event_stale_rejects_non_positive_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    with pytest.raises(ValueError):
        is_event_stale(now, now_utc=now, stale_after_days=0)
