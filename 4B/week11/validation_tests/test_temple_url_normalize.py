"""Offline tests for temple homepage href normalization (radhakrishnatemple)."""

from events.scrapers.radhakrishnatemple import (
    _finalize_temple_url,
    _normalize_temple_href,
    normalize_explicit_temple_event_url,
)

BASE_WWW = "https://www.radhakrishnatemple.net/"
BASE_APEX = "https://radhakrishnatemple.net/"


def test_protocol_relative_event_slug_rewrites_to_path() -> None:
    assert (
        _normalize_temple_href(BASE_WWW, "//event/advent-reflection-series")
        == "https://www.radhakrishnatemple.net/event/advent-reflection-series"
    )


def test_protocol_relative_events_slider_hosts_dropped() -> None:
    assert _normalize_temple_href(BASE_WWW, "//events") is None
    assert _normalize_temple_href(BASE_WWW, "//events-2") is None
    assert _normalize_temple_href(BASE_WWW, "//events-3") is None


def test_hub_and_gallery_paths_dropped() -> None:
    assert _normalize_temple_href(BASE_WWW, "https://www.radhakrishnatemple.net/upcoming-events") is None
    assert (
        _normalize_temple_href(BASE_WWW, "https://www.radhakrishnatemple.net/events-photo-gallery/home")
        is None
    )


def test_same_host_absolute_kept_for_detail_only() -> None:
    assert (
        _normalize_temple_href(BASE_WWW, "https://www.radhakrishnatemple.net/event/hanuman-jayanti")
        == "https://www.radhakrishnatemple.net/event/hanuman-jayanti"
    )


def test_protocol_relative_real_host_non_detail_dropped() -> None:
    assert _finalize_temple_url("https://www.radhakrishnatemple.net/hanuman-jayanti") is None


def test_explicit_supplemental_hanuman_accepted() -> None:
    assert (
        normalize_explicit_temple_event_url("https://www.radhakrishnatemple.net/hanuman-jayanti")
        == "https://www.radhakrishnatemple.net/hanuman-jayanti"
    )


def test_explicit_supplemental_rejects_unknown_path() -> None:
    assert normalize_explicit_temple_event_url("https://www.radhakrishnatemple.net/random-page") is None


def test_protocol_relative_real_host_detail_kept() -> None:
    assert (
        _normalize_temple_href(BASE_WWW, "//www.radhakrishnatemple.net/event/hanuman-jayanti")
        == "https://www.radhakrishnatemple.net/event/hanuman-jayanti"
    )


def test_relative_path_on_base() -> None:
    assert (
        _normalize_temple_href(BASE_WWW, "/event/some-slug")
        == "https://www.radhakrishnatemple.net/event/some-slug"
    )


def test_bogus_host_uses_apex_base_netloc() -> None:
    assert (
        _normalize_temple_href(BASE_APEX, "//event/foo")
        == "https://radhakrishnatemple.net/event/foo"
    )


def test_off_site_rejected() -> None:
    assert _normalize_temple_href(BASE_WWW, "https://example.com/event") is None
    assert _normalize_temple_href(BASE_WWW, "https://www.jkyog.org/upcoming_events") is None


def test_non_http_skipped() -> None:
    assert _normalize_temple_href(BASE_WWW, "mailto:devotee@example.org") is None
    assert _normalize_temple_href(BASE_WWW, "javascript:void(0)") is None
    assert _normalize_temple_href(BASE_WWW, "#section") is None
