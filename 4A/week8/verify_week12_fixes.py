"""
Week 12 Fix Verification Harness
================================

Exhaustive integration test that exercises classify() + build_response()
across many permutations of user input and verifies the bot's reply
against the live Team 4B API at EVENTS_API_BASE_URL.

For each test case we assert one or more "expectations" — substrings or
forbidden substrings that the reply must contain or must not contain.
Expectations are derived from real, current data on the live API where
applicable (e.g., "Holi Sadhana Shivir" is the actual scraped event for a
Holi search).

Run from 4A/week8/:
    .venv/Scripts/python.exe verify_week12_fixes.py

Exit code is 0 if every expectation passes, 1 otherwise.
"""
from __future__ import annotations

import os
import re
import sys
import json
import logging
import traceback
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
# Quiet down noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)

log = logging.getLogger("verify_week12")

from intent_classifier import classify, warm_up
from response_builder import build_response

API_BASE = os.getenv("EVENTS_API_BASE_URL")
CTX = lambda message: {
    "phone_number": "+10000000000",
    "api_base_url": API_BASE,
    "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN") or None,
    "user_id": "verify-user",
    "conversation_id": "verify-conv",
    "last_intent": None,
    "selected_event_id": None,
    "user_message": message,
}


# ----------------------------------------------------------------------
# Live data probe — derive ground-truth expectations from current API.
# ----------------------------------------------------------------------
def _live_search(q: str) -> List[dict]:
    try:
        r = httpx.get(f"{API_BASE}/api/v2/events/search", params={"q": q, "limit": 5}, timeout=15)
        r.raise_for_status()
        return r.json().get("events", []) or []
    except Exception as exc:
        log.warning("Live search failed for %r: %s", q, exc)
        return []


def _live_upcoming(limit: int = 5) -> List[dict]:
    try:
        r = httpx.get(f"{API_BASE}/api/v2/events", params={"limit": limit, "offset": 0}, timeout=15)
        r.raise_for_status()
        return r.json().get("events", []) or []
    except Exception as exc:
        log.warning("Live upcoming failed: %s", exc)
        return []


# ----------------------------------------------------------------------
# Test case schema
# ----------------------------------------------------------------------
@dataclass
class Case:
    name: str
    message: str
    expect_intent_in: Optional[List[str]] = None  # any-of
    must_contain: List[str] = field(default_factory=list)
    must_not_contain: List[str] = field(default_factory=list)
    custom_check: Optional[Callable[[str, dict], Optional[str]]] = None  # returns error message or None


@dataclass
class Result:
    case: Case
    classification: dict
    reply: str
    failures: List[str]


# ----------------------------------------------------------------------
# Build the suite
# ----------------------------------------------------------------------
def build_cases() -> List[Case]:
    upcoming = _live_upcoming(5)
    upcoming_names = [ev["name"] for ev in upcoming if ev.get("name")]
    log.info("Live upcoming sample: %s", upcoming_names[:3])

    holi_events = _live_search("Holi")
    holi_name = holi_events[0]["name"] if holi_events else "Holi"
    log.info("Live Holi search top hit: %s", holi_name)

    kirtan_events = _live_search("Kirtan")
    kirtan_name = kirtan_events[0]["name"] if kirtan_events else "Kirtan"
    log.info("Live Kirtan search top hit: %s", kirtan_name)

    cases: List[Case] = []

    # ---------- Discovery (generic upcoming) ----------
    cases += [
        Case(
            "discovery_basic",
            "What events are coming up?",
            expect_intent_in=["discovery", "event_list"],
            must_contain=["upcoming events"],
            must_not_contain=["could not find"],
        ),
        Case(
            "discovery_anything_happening",
            "Anything happening?",
            expect_intent_in=["discovery", "event_list", "ambiguous", "clarification_needed"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "discovery_show_me",
            "Show me the latest events",
            expect_intent_in=["discovery", "event_list"],
            must_contain=["upcoming events"],
        ),
    ]

    # ---------- Time-based ----------
    cases += [
        Case(
            "time_today",
            "Any events today?",
            expect_intent_in=["time_based", "today_events", "today"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "time_weekend",
            "What's happening this weekend?",
            expect_intent_in=["time_based", "discovery", "event_list"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "time_tonight",
            "Anything going on tonight?",
            expect_intent_in=["time_based", "today_events", "discovery", "event_list"],
        ),
        Case(
            "time_this_week",
            "Programs this week?",
            expect_intent_in=["time_based", "discovery", "event_list"],
        ),
    ]

    # ---------- Event-specific ----------
    cases += [
        Case(
            "event_holi",
            "Tell me about the Holi celebration",
            expect_intent_in=["event_specific", "single_event_detail", "discovery", "event_list", "event_search"],
            must_contain=[holi_name.split()[0]],  # at least the first word "Holi"
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "event_kirtan_retreat",
            "Tell me about the Bhakti Kirtan Retreat",
            expect_intent_in=["event_specific", "single_event_detail", "logistics", "discovery", "event_list", "event_search"],
            # The bot should pull a relevant event via search rather than say "no match"
            must_not_contain=["could not find any matching events for *Bhakti Kirtan Retreat*"],
        ),
        Case(
            "event_ltp",
            "What is the Life Transformation Program?",
            expect_intent_in=["event_specific", "discovery", "event_list", "single_event_detail", "event_search"],
            must_not_contain=["I ran into an issue"],
        ),
    ]

    # ---------- Recurring schedule (LOCAL handler) ----------
    cases += [
        Case(
            "rec_sunday_satsang",
            "When is Sunday Satsang?",
            expect_intent_in=["recurring_schedule"],
            must_contain=["Satsang"],
            must_not_contain=["could not find any matching events"],
        ),
        Case(
            "rec_aarti_time",
            "What time is the Aarti?",
            expect_intent_in=["recurring_schedule"],
            must_contain=["Aarti"],
            must_not_contain=["could not find any matching events"],
        ),
        Case(
            "rec_temple_hours",
            "What are the temple hours?",
            expect_intent_in=["recurring_schedule", "logistics", "discovery", "ambiguous", "clarification_needed"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "rec_darshan_today",
            "Is Darshan happening today?",
            expect_intent_in=["recurring_schedule", "time_based", "logistics"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "rec_daily_bhajans",
            "When are the daily bhajans?",
            expect_intent_in=["recurring_schedule", "discovery", "event_list"],
            must_not_contain=["I ran into an issue"],
        ),
    ]

    # ---------- Logistics ----------
    cases += [
        Case(
            "logistics_holi_where",
            "Where is the Holi celebration held?",
            expect_intent_in=["logistics", "event_specific", "single_event_detail", "discovery", "event_list", "event_search"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "logistics_parking",
            "Is there parking at the temple?",
            expect_intent_in=["logistics", "discovery", "ambiguous", "clarification_needed"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "logistics_kirtan_directions",
            "How do I get to the Bhakti Kirtan Retreat?",
            expect_intent_in=["logistics", "event_specific", "single_event_detail", "event_search"],
            must_not_contain=["I ran into an issue"],
        ),
    ]

    # ---------- Sponsorship / donation ----------
    cases += [
        Case(
            "sponsor_donate_generic",
            "How can I donate?",
            expect_intent_in=["sponsorship"],
            must_contain=["Donations", "jkyog.org/donate"],
            must_not_contain=["could not find any matching events"],
        ),
        Case(
            "sponsor_seva_generic",
            "I want to do seva",
            expect_intent_in=["sponsorship"],
            must_contain=["Seva"],
            must_not_contain=["could not find any matching events"],
        ),
        Case(
            "sponsor_specific_event",
            "Sponsorship tiers for Holi",
            expect_intent_in=["sponsorship", "event_specific", "single_event_detail", "event_search"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "sponsor_annadaan",
            "How do I sponsor annadaan?",
            expect_intent_in=["sponsorship"],
            must_contain=["Annadaan"],
        ),
    ]

    # ---------- Ambiguous / clarification ----------
    cases += [
        Case(
            "amb_info",
            "info",
            expect_intent_in=["ambiguous", "clarification_needed"],
            # The clarification path should NOT proceed to call the events API.
            # ("upcoming events" appears in the clarification HELP TEXT itself
            # as one of the suggested phrasings, so we only forbid the
            # event-list heading and the no-results sentence.)
            must_not_contain=[
                "Here are the events I found",
                "I could not find any matching events",
            ],
        ),
        Case(
            "amb_help",
            "help",
            expect_intent_in=["ambiguous", "clarification_needed", "discovery"],
        ),
        Case(
            "amb_more",
            "tell me more",
            expect_intent_in=["ambiguous", "clarification_needed"],
        ),
    ]

    # ---------- Edge cases ----------
    cases += [
        Case(
            "edge_emoji_only",
            "🙏",
            expect_intent_in=["ambiguous", "clarification_needed", "discovery", "event_list"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "edge_typo_fasival",
            "Any fasival coming up?",
            expect_intent_in=["discovery", "event_list", "event_specific", "ambiguous", "clarification_needed"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "edge_long_query",
            "I am visiting from out of town next month and would like to know what spiritual events are happening at the JKYog Radha Krishna Temple",
            expect_intent_in=["discovery", "event_list", "time_based", "event_specific"],
            must_not_contain=["I ran into an issue"],
        ),
        Case(
            "edge_yes_only",
            "yes",
            expect_intent_in=["ambiguous", "clarification_needed", "discovery", "event_list"],
        ),
        Case(
            "edge_thank_you",
            "thank you",
            expect_intent_in=["ambiguous", "clarification_needed"],
            must_not_contain=["I ran into an issue"],
        ),
    ]

    # ---------- WhatsApp size constraint ----------
    cases += [
        Case(
            "size_limit",
            "List all the events please",
            expect_intent_in=["discovery", "event_list"],
            custom_check=lambda reply, _c: (
                None if len(reply) <= 4096 else f"Reply too long: {len(reply)} chars"
            ),
        ),
    ]

    # ---------- Live data verification ----------
    if upcoming_names:
        first_event_word = upcoming_names[0].split()[0]
        cases.append(
            Case(
                "live_top_event_named",
                "What's coming up?",
                expect_intent_in=["discovery", "event_list"],
                must_contain=[first_event_word],
            )
        )

    return cases


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------
def run_case(case: Case) -> Result:
    failures: List[str] = []
    classification = {}
    reply = ""

    try:
        classification = classify(case.message)
    except Exception as exc:
        failures.append(f"classify() raised: {exc}")
        return Result(case, classification, reply, failures)

    intent = classification.get("intent")
    if case.expect_intent_in and intent not in case.expect_intent_in:
        failures.append(
            f"intent={intent!r} not in expected {case.expect_intent_in}"
        )

    # Don't call build_response for clarification_needed — main.py wouldn't.
    if intent in ("clarification_needed", "ambiguous", "unknown"):
        reply = (
            "I'm not sure I caught that. You can ask me about:\n"
            "- *upcoming events* (e.g. \"what's happening this weekend?\")\n"
            "- a *specific event* (e.g. \"tell me about Holi\")\n"
            "- *recurring temple schedule* (e.g. \"when is Sunday Satsang?\")\n"
            "- *parking / logistics* for an event\n"
            "- *donations / seva*"
        )
    else:
        try:
            reply = build_response(classification, CTX(case.message)) or ""
        except Exception as exc:
            failures.append(f"build_response() raised: {exc}\n{traceback.format_exc()}")

    for needle in case.must_contain:
        if needle.lower() not in reply.lower():
            failures.append(f"missing required substring: {needle!r}")

    for needle in case.must_not_contain:
        if needle.lower() in reply.lower():
            failures.append(f"contains forbidden substring: {needle!r}")

    if case.custom_check:
        err = case.custom_check(reply, classification)
        if err:
            failures.append(err)

    return Result(case, classification, reply, failures)


def main() -> int:
    if not API_BASE:
        log.error("EVENTS_API_BASE_URL not set in .env")
        return 1

    log.info("EVENTS_API_BASE_URL = %s", API_BASE)

    # Allow test runs without burning Gemini free-tier quota by forcing the
    # Jaccard fallback for every classification.
    if os.getenv("FORCE_JACCARD_ONLY", "0") == "1":
        import intent_classifier as _ic
        _ic._classify_with_gemini = lambda _msg: None  # type: ignore
        log.warning("FORCE_JACCARD_ONLY=1 — Gemini path disabled for this run.")
    else:
        log.info("Warming up Gemini ...")
        warm_up()

    cases = build_cases()
    log.info("Running %d cases ...", len(cases))

    results = [run_case(c) for c in cases]

    print("\n" + "=" * 82)
    print(f"  RESULTS — {len(results)} cases")
    print("=" * 82)

    passed = 0
    failed = 0
    for r in results:
        intent = r.classification.get("intent", "-")
        conf = r.classification.get("confidence", "-")
        status = "PASS" if not r.failures else "FAIL"
        if r.failures:
            failed += 1
        else:
            passed += 1
        # ASCII-only output for Windows cp1252 console compatibility.
        reply_preview = (r.reply[:60].replace("\n", " ") + "...") if len(r.reply) > 60 else r.reply.replace("\n", " ")
        # Strip non-ascii from preview (emojis like the recurring schedule's red circle)
        reply_preview = reply_preview.encode("ascii", "ignore").decode("ascii")
        print(f"  [{status}] {r.case.name:<28} | intent={intent:<22} conf={conf} | {reply_preview}")
        for fail in r.failures:
            fail_line = fail.encode("ascii", "ignore").decode("ascii")
            print(f"          -> {fail_line}")

    print("=" * 82)
    print(f"  PASSED {passed}/{len(results)}   FAILED {failed}")
    print("=" * 82)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
