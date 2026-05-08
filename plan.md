# Week-12 Bot-Fixes Plan
*Source-of-truth for the live test + fix meeting on 2026-05-08.*

> **Update — 2026-05-08 12:35 PM, after Round-2 live test:** Round-1
> (T3+T4+T5+T8) and Round-2 (multi-day display + numbered follow-up)
> shipped, but **two new bugs surfaced from a real WhatsApp test**:
>
> 1. **session.selected_event_id leaks across turns** — once a user
>    replies "2" to a list, every subsequent question that doesn't have
>    an event_id of its own picks up event_id=27 (Bay Area LTP) from
>    session memory. This is the cause of "where is the temple?" →
>    Bay Area LTP logistics, "when is the holi event" → Bay Area LTP,
>    and several other "wrong event" responses in the transcript. THE
>    HEADLINE BUG OF ROUND 3.
>
> 2. **EVENT_NAMES list is incomplete** — "Hanuman Jayanti" gets no
>    entity match, falls into the `event_specific` intent with
>    event_name=None, which then dumps users into the
>    selected_event_id leak above OR returns a confused response
>    based on the stripped raw message.
>
> Plus a few smaller things: the API has mojibake (`â��` instead of
> `–`) in `description` fields because the 4B scraper isn't decoding
> UTF-8 from the source page properly. The bot can defensively
> normalise this. Section 11 below is the Round-3 plan.

> **TL;DR — bot is more broken than it was on May 5.** Chanakya pushed two
> commits May 6 that picked up ~3 of the Week-12 fixes for `response_builder.py`
> but the team also **deleted the LLM intent classifier**, **shrunk the
> keyword sets**, and **added a `bridge_intent_to_builder` hack in `main.py`**
> that overrides the careful classification with brittle string matches.
> Net effect: on a 24-message smoke test against Team-4A-Week8 (Chanakya's
> May-6 head), **23 of 24 messages classify as `clarification_needed`** and
> the bridge then forces them down a path that ignores their actual
> entities. The headline failures from the screenshots — time-based filtering,
> timezone display, generic donation, recurring schedule — are *all* still
> present.
>
> Recommended path: **rebase the meeting work on `Shrikanth-week12-fixes`
> (which already has the working classifier + handlers)** rather than on
> Chanakya's branch, then layer on the timezone-conversion and
> past-event-filter fixes that neither branch has yet. Roll up as one new
> PR before the deadline.

---

## 0. State of the world — as of 2026-05-08

### 0.1 Branches and what's on each

| Branch | Last commit | Has these Week-12 fixes? |
|---|---|---|
| `main` (=PR #45) | 2026-05-01 | ❌ none |
| `Team-4A-Week11` | 2026-05-04 | ❌ none — pre-Week-12 baseline |
| `4A-week11-Chanakyaalluri` | 2026-05-06 | ⚠️ partial (recurring import + generic-donation + entity routing) |
| `Team-4A-Week8` | 2026-05-06 | ⚠️ same as Chanakya's branch above (response_builder identical) — but `intent_classifier.py` and `main.py` regressed badly |
| `Shrikanth-week12-fixes` | 2026-05-05 | ✅ all 5 Week-12 fixes; missing TZ-conversion + past-event filter |

**No PR is open.** Whatever the WhatsApp screenshots in `Logs and Images/` were
hitting must be a separate Render service — `jkyog-whatsapp-bot.onrender.com`
is "service suspended" and `jkyog-whatsapp-bot-4a.onrender.com` 404s.
Confirm during the meeting which Render service is actually wired to the
Twilio sandbox.

### 0.2 Live API state (2026-05-08, Team 4B's Render API) — unchanged from May 5

```
total events:         19
past events listed:   1   (Seattle LTP, May 4 — today is May 8)
today:                0
future:               18
suspect_times:        5   (LTPs at 01:30 / 01:45 — clearly wrong)
missing_timezone:     19/19
missing_address:      19/19
missing_city:         19/19
/api/v2/events/recurring → {"events": []}
/api/v2/events/today    → returns Seattle LTP (because May 4–9 contains today)
?upcoming_only=true     → silently ignored
?start_date=YYYY-MM-DD  → silently ignored
```

So **Team 4B did not improve the data layer this week.** Bug 4–6, 14, 15, 20
from my May-5 review are all still live. The bot has to defend against the
data, not the other way around.

---

## 1. Smoke-test results — Team-4A-Week8 head, 24 messages

Run from `4A/week8/smoke_bug_audit.py` against Chanakya's May-6 code with
the bridge hack from `main.py` applied.

| # | Message | Classifier intent | Bridge intent | Verdict |
|---|---|---|---|---|
| 1 | What events are coming up? | clarification_needed | clarification_needed | ❌ "could not retrieve" — confidence 0.06 |
| 2 | What's happening at the temple this weekend | clarification_needed | event_list (forced) | ❌ "could not retrieve" |
| 3 | Is there anything at 3am tonight | clarification_needed | event_list (forced) | ❌ generic upcoming list, no 3am filter |
| 4 | Any events tomorrow? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 5 | What's on this Friday? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 6 | Anything on May 23rd? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 7 | When is Sunday Satsang? | clarification_needed | recurring_events (forced) | ❌ "could not find for *recurring events*" |
| 8 | What time is the morning aarti? | clarification_needed | time_filtered_events (forced — intent doesn't exist!) | ❌ generic upcoming list |
| 9 | Is there kirtan today? | clarification_needed | event_list (forced) | ❌ generic upcoming list |
| 10 | Where is the Bhakti Kirtan Retreat? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 11 | Tell me about Janmashtami | clarification_needed | time_filtered_events (forced) | ❌ generic upcoming list |
| 12 | When is Holi? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 13 | Where is the temple? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 14 | Is there parking for Holi? | clarification_needed | logistics_parking (forced) | ✅ **Logistics for Holi Sadhana Shivir** with parking field |
| 15 | How do I get to the Dallas retreat? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 16 | How can I donate? | clarification_needed | clarification_needed | ❌ generic upcoming list (generic-donation never reached) |
| 17 | How do I sponsor an event? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 18 | Sponsorship for Holi? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 19 | donate? | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 20 | tell me more | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 21 | info | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 22 | stuff happening | clarification_needed | clarification_needed | ❌ generic upcoming list |
| 23 | Hello | clarification_needed | clarification_needed | ❌ generic upcoming list (no greeting bypass) |
| 24 | "" (empty) | clarification_needed | clarification_needed | ❌ generic upcoming list |

**1 of 24 working** (case 14, only because the bridge hack happened to line up with response_builder's logistics path).

The `1:30 AM` time is on every list result. The `Sunday Satsang` rich-format
(`Next: Sunday, 10:30 AM – 12:30 PM CT`) that the May-7 screenshots showed is
**not produced by this code**. Whatever Render service was on those screenshots
was running a different build.

---

## 2. Root-cause of regressions since May 5

| # | Regression | File | Reason |
|---|---|---|---|
| R1 | LLM classifier deleted | `intent_classifier.py` | Rewrite kept only Jaccard; no Gemini fallback |
| R2 | Keyword sets shrunk | `intent_classifier.py` | "upcoming/seva/fund/support/aarti/retreat/festival" etc. removed |
| R3 | Confidence threshold 0.6 with tiny Jaccard scores | `intent_classifier.py` | Real messages score 0.0–0.17 → all → `clarification_needed` |
| R4 | `tokenize()` still doesn't strip punctuation | `intent_classifier.py` | "donate?" splits to {"donate?"} — never matches {"donate"} |
| R5 | `bridge_intent_to_builder()` hack | `main.py` | String matches "weekend/today/tonight" → forces wrong intent, throws away timeframe |
| R6 | `time_filtered_events` is a fictional intent | `main.py` | Bridge invents a name `response_builder` doesn't recognise |
| R7 | Hardcoded "Sunday Satsang is held in the morning" override | `main.py` | Post-hoc string replace bypasses real schedule |
| R8 | Hardcoded "Hanuman Jayanti..." override | `main.py` | Same — overrides real response with stub |
| R9 | Session memory removed | `main.py` | `ACTIVE_SESSIONS` dict gone — no follow-up tracking |
| R10 | Greeting bypass removed | `main.py` | "Hello" no longer returns the welcome message |
| R11 | No FastAPI `lifespan` | `main.py` | No warm-up; Gemini is gone anyway so moot, but the slot is still unused |
| R12 | Duplicate `*_config.py` files | `4A/week8/` | `intent_classifier.py` + `intent_classifier_config.py`, etc. — at least 5 zombie pairs |
| R13 | `schedule-2.py`, `time.py`, `closed.py` re-added | `4A/week8/` | The orphans I documented for deletion came back |

---

## 3. The complete bug list — what's still broken (status today)

Carrying the May-5 numbering for traceability.

| # | Bug | Status today | Where to fix |
|---|---|---|---|
| **B1** | `time_based` intent has no handler in `response_builder._resolve_intent` | **Open** | `4A/response_builder.py` |
| **B2** | `map_to_api()` is dead code — its endpoint+params dict is never read | **Open** | `4A/response_builder.py` (consume it, or delete and route by intent+entities) |
| **B3** | Datetime rendered in raw stored timezone — no `astimezone()` | **Open** | `4A/response_builder.py:_format_date_time / _format_short_date_time` |
| **B4** | `timezone: null` on every event | **Open — 4B side** | `4B` scraper |
| **B5** | Wrong `start_datetime` values (LTPs at 01:30) | **Open — 4B side** | `4B` scraper |
| **B6** | Past events listed as upcoming | **Open** | `4A/response_builder.py` (filter `start_datetime >= now` client-side) |
| **B7** | Recurring schedule path broken on `Team-4A-Week11` | **Closed** on Chanakya/Week8 (recurring_handler import wired); **needs program_hint passing** |
| **B8** | Sponsorship without an event = "could not find" | **Closed in code, unreachable** because R3 forces clarification_needed |
| **B9** | Logistics without an event = "could not find" | **Closed in code, unreachable** because R3 forces clarification_needed |
| **B10** | `tokenize()` doesn't strip punctuation | **Open** | `4A/intent_classifier.py` |
| **B11** | Gemini cold-start regression (per-request client) | **Open + worse** — Gemini removed entirely | `4A/intent_classifier.py` |
| **B12** | `discovery` and `no_results_check` intents have no explicit handler | **Open** | `4A/response_builder.py` |
| **B13** | "Bhakti Kirtan Retreat" misrouted to `recurring_schedule` | **Closed in code** via entity routing in `_resolve_query`, **unreachable** because R3 |
| **B14** | API duplicate event records (#26 vs #46) | **Open — 4B side** | `4B` dedup |
| **B15** | `EVENT_NAMES` static list is stale | **Open** | `4A/entity_extractor.py` |
| **B16** | Empty message → generic upcoming list | **Open** | `4A/main.py` (early-out before background task) |
| **B17** | `clarification_needed` doesn't get the friendly clarifier text | **Open + worse** — every message is `clarification_needed` | `4A/main.py` |
| **B18** | Multi-day events render confusingly ("May 4 1:30 AM to May 9 3:45 AM") | **Open** | `4A/response_builder.py:_format_date_time` |
| **B19** | "First result wins" search ranking | **Open** | `4A/response_builder.py:_resolve_single_event` |
| **B20** | All event addresses default to `JKYog Radha Krishna Temple` | **Open — 4B side** | `4B` scraper |
| **B21** | (NEW today) `bridge_intent_to_builder()` overrides the classifier | **Open** | `4A/main.py` |
| **B22** | (NEW today) Hard-coded "Sunday Satsang is held in the morning" / "Hanuman Jayanti is..." overrides | **Open** | `4A/main.py` |
| **B23** | (NEW today) Duplicate `*_config.py` files cluttering import surface | **Open** | filesystem cleanup |
| **B24** | (NEW today) `schedule-2.py`, `time.py`, `closed.py` re-added (orphans, not imported) | **Open** | filesystem cleanup |
| **B25** | (NEW today) Session memory deleted from `main.py` | **Open** | `4A/main.py` |
| **B26** | (NEW today) Greeting bypass deleted from `main.py` | **Open** | `4A/main.py` |

---

## 4. Fix tasks — prioritized for today

> Branch strategy: **start from `Shrikanth-week12-fixes`**, not Chanakya's
> regressed work. Cherry-pick the two genuine improvements Chanakya added,
> then layer on the new fixes. Push to a new branch
> `Shrikanth-week12-fixes-v2` and open one PR.

### P0 — demo blockers (must land before live test)

**T1. Restore the working classifier on `Shrikanth-week12-fixes`.**
- Confirm `intent_classifier.py` on the branch already has: Gemini singleton + `warm_up()` + Jaccard fallback + punctuation-stripped `tokenize()` + `time_based` intent + expanded keyword sets. ✅ already there.
- *Do not* port any of Chanakya's intent_classifier changes — they're regressions.
- Acceptance: smoke test gives non-`clarification_needed` for ≥ 20 of 24 messages, with intents matching what the response_builder routes.

**T2. Kill `bridge_intent_to_builder` and the hard-coded overrides in `main.py`.**
- Replace `main.py` with the version on `Shrikanth-week12-fixes` (which has lifespan/warm_up + session memory + greeting bypass + clarification short-circuit + `user_message` in context).
- Acceptance: `main.py` ≤ 140 lines, no `bridge_intent_to_builder`, no string overrides.

**T3. Fix datetime display — convert to Central Time even when API says `timezone: null`.**
- `_format_date_time` and `_format_short_date_time`: if parsed dt has no tzinfo, attach `ZoneInfo("America/Chicago")`. Then format directly. Always append " CT" suffix.
- Don't try to convert from UTC — the data isn't UTC, it's just naive. Treating it as CT is the least-wrong answer until B5 is fixed upstream.
- Acceptance: "When: May 4, 1:30 AM CT" instead of "May 4, 1:30 AM" with a blank suffix. Even better: detect the suspect-time band (`hour < 6`) and append " ⚠ time may be unconfirmed" — *defer to T11*.

**T4. Filter out past events client-side in `_build_event_list_response`.**
- After `_extract_events`, drop any event whose `start_datetime` is before `datetime.now(ZoneInfo("America/Chicago"))`.
- For the Seattle LTP (May 4 → May 9) case where today falls *inside* the range, keep it iff `end_datetime` is in the future.
- Acceptance: "What events are coming up?" no longer leads with the May-4 Seattle LTP on May 8.

**T5. Implement `time_based` intent handler properly.**
- On my branch, `_resolve_intent` already aliases `time_based` → some valid intent. Verify it routes to `_build_event_list_response` with timeframe applied.
- For `timeframe == "today"` → `client.get_today()`.
- For `timeframe == "tomorrow"` / `"this_weekend"` / `"this_week"` / a parsed YYYY-MM-DD → `client.get_events()` then **filter client-side** to the matching date range. The API ignores `start_date`, so don't trust it.
- Acceptance: "Any events tomorrow?" returns events with `start_datetime.date() == today + 1`. "What's on May 23rd?" returns events on that date. "What's happening this weekend?" returns Saturday + Sunday only.

**T6. Generic donation / sponsorship-without-event path.**
- `Shrikanth-week12-fixes` already has `_format_generic_sponsorship`. Confirm it fires when entity_event_name is None and there's no follow-up context. Acceptance: "How can I donate?" returns the seva list, not "could not find."

**T7. Recurring `program_hint` plumbing.**
- Pass the program_name entity (or query) through to `_format_active_recurring_schedule(active_programs, program_hint=...)`.
- Inside, call `get_next_occurrence(program_hint)` from `recurring_handler` and format as `*<Program> schedule:*\nNext: <day>, HH:MM AM/PM CT to HH:MM AM/PM CT`.
- Acceptance: "When is Sunday Satsang?" → `Satsang schedule:\nNext: Sunday, 10:30 AM to 12:30 PM CT`.

### P1 — visible quality

**T8. Greeting and empty-message early-outs in `main.py`.**
- Already in the Week-12 branch — confirm.

**T9. Re-enable session memory.**
- `ACTIVE_SESSIONS` dict + `last_intent` + `selected_event_id` + max-1000 LRU eviction.
- Already in the Week-12 branch — confirm.

**T10. `clarification_needed` short-circuit in `main.py`.**
- Before `build_response`, if `raw_classification["intent"] == "clarification_needed"`, return a friendly clarifier without hitting the API.
- Already in the Week-12 branch — confirm.

### P2 — pipeline correctness (4B side, flag for Subodh / team)

**T11. Confirm the suspect 01:30 / 01:45 LTP times with Subodh.**
- They could be valid (some PST evening time mis-stored). Either way, surface this to the team and add a "⚠ time unconfirmed" banner in the bot for events whose `hour < 6`.
- Owner: Subodh + Rohan (scraper).

**T12. Populate `timezone`, `address`, `city`, `state` from scraper.**
- Currently 19/19 events are missing all four.
- Owner: Rohan (scraper). Block on Subodh's API once scraper is fixed.

**T13. Wire `/api/v2/events/recurring` to actual recurring-event rows.**
- Owner: Subodh.

**T14. Honor `?upcoming_only=true` and `?start_date=YYYY-MM-DD` in the API,**
- or document explicitly that they're not supported so 4A doesn't try to pass them.
- Owner: Subodh.

### P3 — cleanup

**T15. Delete the duplicate `*_config.py` files** (`api_client_config.py`, `entity_extractor_config.py`, `intent_classifier_config.py`, `recurring_handler_config.py`, `response_builder_config.py`).

**T16. Delete `schedule-2.py`, `time.py`, `closed.py`** — orphaned, not imported anywhere.

**T17. Make `EVENT_NAMES` in `entity_extractor.py` derive from API on startup**, or at minimum expand it to include "Holi Sadhana Shivir", "Bhakti Kirtans & Satsang", "Holi Mela", "West Coast Retreat", "Spiritual Retreat & Family Camp", "Pran Pratistha".

---

## 5. Live-test script (run during the meeting)

Tester sends these from a real phone via the Twilio sandbox. Each row notes
what success looks like so the team can flip from "is it sending anything"
to "is it sending the right thing".

| # | Message | Expected output |
|---|---|---|
| L1 | `Hi` | Welcome / namaste blurb |
| L2 | `What events are coming up?` | List of ≥ 3 events, all with `start_datetime ≥ today`, dates rendered as `<Mon DD, H:MM AM/PM CT>` |
| L3 | `Any events tomorrow?` | Events whose start date is May 9, or "no events tomorrow — here are the next few" |
| L4 | `What's happening this weekend?` | Only Saturday/Sunday events, or graceful "no weekend events — here are the next few" |
| L5 | `Anything on May 23rd?` | West Coast Retreat 2026 |
| L6 | `When is Sunday Satsang?` | `Satsang schedule: Next: Sunday, 10:30 AM to 12:30 PM CT` |
| L7 | `What time is the morning aarti?` | Aarti schedule with the 12:15 PM CT and 7:00 PM CT slots from `recurring_handler` |
| L8 | `When is Holi?` | Holi Sadhana Shivir details (or Dallas Holi Mela, whichever the API ranks first) |
| L9 | `Where is the Bhakti Kirtan Retreat?` | Event detail with location field |
| L10 | `Is there parking for Holi?` | Holi Sadhana Shivir logistics block, parking field showing "Not listed on the event page" |
| L11 | `How can I donate?` | Generic seva list with `jkyog.org/donate` |
| L12 | `Sponsorship for Holi?` | Holi sponsorship tiers OR "no sponsorship tiers listed for this event" |
| L13 | `donate?` (with question mark, no caps) | Same generic seva list as L11 — confirms `tokenize()` punctuation fix |
| L14 | `info` | Friendly clarifier: "What can I help with — events, schedule, or donations?" |
| L15 | `Is there anything at 3am tonight` | Either "nothing scheduled at 3 AM tonight" or empty-result with suggestion |

If 12 of 15 pass, ship. If 9–11 pass, ship after fixing the regressors. If
< 9 pass, push the merge to tomorrow morning.

---

## 6. Order of operations during the meeting

1. **0:00–0:05** — Walk through this `plan.md` with the team. Confirm
   everyone agrees `Shrikanth-week12-fixes` is the working baseline.
2. **0:05–0:15** — Live-test the *current* deployed bot with messages L1–L5.
   Record exactly what comes back. This is the "before" snapshot.
3. **0:15–0:45** — Apply T1–T7 (P0) on a new branch
   `Shrikanth-week12-fixes-v2`. Local smoke test (`smoke_bug_audit.py`)
   should hit ≥ 20/24 green.
4. **0:45–0:55** — Push branch, deploy to whichever Render service is
   wired to Twilio. Confirm with `curl /` returns the JSON status block.
5. **0:55–1:25** — Re-run live-test L1–L15. Note pass/fail. Hot-fix any
   regression.
6. **1:25–1:30** — Tag the team for T11–T14 follow-up on the 4B side. Open
   a single PR from `Shrikanth-week12-fixes-v2` → `main`.

---

## 7. Things to *not* do during the meeting

- Do not try to fix the 4B scraper bugs (B4, B5, B14, B20). They're real
  but unrelated to the 4A bot, and they take longer than this meeting has.
- Do not delete the `*_config.py` zombies until after the meeting — they're
  not imported by anything we're changing, and the diff is noisy.
- Do not change the API contract (no new endpoints, no new query params).
  The 4A side has to work against the 4B API as-it-is today.
- Do not merge directly to `main`. PR review still happens, even on a
  deadline.

---

## 8. What actually shipped on `Shrikanth-week12-fixes` (2026-05-08)

> All four edits live in two files: `4A/week8/intent_classifier.py` and
> `4A/week8/response_builder.py`. No changes to `main.py` were needed —
> T1, T2, T6, T7 from §4 were already in place from the original Week-12
> commit (verified by sub-agent before any edits).

### T8 (NEW) — honest confidence scores

The user observed that confidence values were repeatedly `0.5` even on
messages where the math should yield very different numbers. Audit found
two compounding problems:

1. **Hardcoded floor at line 317:** `if has_signal: confidence = max(confidence, 0.5)`.
   Any successfully classified message had its confidence clamped to ≥ 0.5,
   regardless of the underlying Jaccard / entity-coverage math.
2. **Multi-word keyword set entries** like `"any events"`, `"what's happening"`
   inflated the Jaccard *union* but could never enter the *intersection*
   (since `tokenize()` produces single-word tokens). This depressed every
   real Jaccard score into the 0.04–0.25 range, which then triggered the
   floor on every match.

Fix: removed the floor and added a `_flatten_keyword_set` helper that
splits multi-word keyword entries into single tokens specifically for the
Jaccard calculation. Routing still uses the original phrases (substring
scan against `msg`).

Confidence now ranges 0.0 → 0.25 for Jaccard hits — that's real math.
Gemini path still returns its own (LLM-volunteered, uncalibrated) numbers
when the daily quota allows.

### T3 — timezone display: `… CT` always

`_format_date_time` and `_format_short_date_time` now render every event
datetime with an explicit timezone label. When the API returns naive
datetimes (which is currently 19/19 events because the 4B scraper isn't
populating the `timezone` field), the bot defaults the suffix to ` CT` —
the temple's wall-clock zone. If the API ever does populate `timezone`,
that string is honoured as a display label. The underlying datetime
values are not converted, only labelled — see B5 in §3 for why
conversion is unsafe given the current data quality.

Result: "May 4, 1:30 AM" → "May 4, 1:30 AM CT" everywhere.

### T4 — past-event filter

New helpers `_filter_upcoming` and `_now_ct` in `response_builder.py`.
`_build_event_list_response` calls `_filter_upcoming(events)` after
extracting the API payload, dropping any event whose `end_datetime` is
already past (using `start_datetime` as a fallback when end is missing).
Multi-day events that are still in progress are kept — e.g. on 2026-05-08
the Seattle LTP (May 4–9) still appears in the upcoming list because its
end date is tomorrow.

Also widened the default page size from 5 → 20 events so post-filter
trimming doesn't run out of rows.

### T5 — time_based intent: client-side date-range filter

New explicit `time_based` branch in `build_response` plus three helpers:
`_resolve_timeframe`, `_date_range_for_timeframe`, `_filter_by_date_range`,
plus `_format_timeframe_heading` for the user-facing heading.

Mapping:
- `today` / `tonight`     → `client.get_today()` (uses Team 4B's `/today` endpoint)
- `tomorrow`              → today's events filtered to date == tomorrow
- `this_weekend`          → filter to Sat–Sun (or today + Sun if today is Sat/Sun)
- `this_week` / `next_week` → 7-day windows from today / next Monday
- `YYYY-MM-DD` parsed_date → exact-date match via `_filter_by_date_range`

Every filtered list now displays its own friendly heading: "today",
"tomorrow", "this weekend", "May 23", etc. — instead of the generic
"upcoming events".

Verified working from the smoke test:
- "Anything on May 23rd?" → only West Coast Retreat 2026
- "What's happening this weekend?" → only Seattle LTP (still active) + Bay Area LTP (starts Sun)
- "What's on this Friday?" → only Seattle LTP (active today)
- "Any events tomorrow?" → only Seattle LTP (still active tomorrow)

### Bonus polish

- Added `temple`, `jkyog`, `venue`, `place`, `located`, `directions` to
  `_QUESTION_WORDS` so "Where is the temple?" no longer leaks "temple"
  into the search endpoint and returns Mahashivratri.
- Also added a `discovery` branch to `build_response` (was previously
  reaching the right code by accident via the fallback).

### Smoke test results — 2026-05-08, post-fix

`smoke_bug_audit.py` (24 cases, FORCE_JACCARD_ONLY=1):
- 21/24 produce the right output through `build_response` directly.
- The remaining 3 (`Hello`, `info`, `tell me more`, empty string) are
  handled correctly by `main.py` BEFORE `build_response` is ever called
  (greeting bypass + clarification_needed short-circuit). Confirmed via
  `smoke_main_path.py` which exercises the full main.py code path.

`verify_week12_fixes.py` (32 cases, the regression suite):
- **32/32 PASSING.** No regressions.

### Quota note

Gemini free-tier daily quota (20 requests/day on `gemini-2.5-flash-lite`)
is exhausted as of this commit. The bot falls back to Jaccard-only and
still produces correct intents for the standard test set, but
classification quality on unusual phrasings will regress until the quota
resets at midnight Pacific. Three options:
1. Add billing to the existing Gemini key (cheapest path).
2. Provision a Llama / Anthropic / OpenAI key and add a second LLM
   adapter to `intent_classifier.py`.
3. Live with Jaccard-only for the meeting today and re-test tomorrow once
   the quota resets.

User to choose. Code is otherwise ready.

---

## 9. Acceptance criteria for "done"

- `smoke_bug_audit.py` (local) passes ≥ 22/24 cases on
  `Shrikanth-week12-fixes-v2`.
- Live test L1–L15 passes ≥ 12/15 from a real phone via Twilio.
- No event in any list response shows a bare "1:30 AM" — every datetime
  has a `CT` suffix.
- "How can I donate?" returns the seva blurb, not "could not find."
- "When is Sunday Satsang?" returns `Next: Sunday, 10:30 AM to 12:30 PM CT`.
- `/4A/week8/main.py` does not contain the strings `bridge_intent_to_builder`,
  `Hanuman Jayanti is a special celebration`, or `Sunday Satsang is typically
  held in the morning`.
- One PR open from `Shrikanth-week12-fixes-v2` → `main`, with a note
  asking Yatin/Hermes to ping Subodh + Rohan about T11–T14.

---

## 10. Round-2 fixes (committed earlier today)

- Multi-day events now render as `May 4 – May 9 CT` in the list view
  (previously only the start `May 4, 1:30 AM CT`, which made multi-day
  events look like one-shots in the past).
- Numbered follow-up wired: a bare `2` resolves to the second event
  in the previous list and re-enters `build_response` with
  `intent=single_event_detail` and `event_id` set. Stored in
  `session.last_shown_event_ids`.

These shipped in commit `fc717f2`. The live test that followed exposed
the bugs in §11.

---

## 11. Round-3 plan — after the live WhatsApp test

### Evidence

WhatsApp transcript snippets (user `+12408280044` in production):

```
> when is the holi event
< Bay Area Life Transformation Program 2026
  When: May 10, 2026 – May 18 CT  …
```

Expected: Holi Sadhana Shivir details. Got: the Bay Area LTP because
the user had earlier replied `2`, which set
`session.selected_event_id = 27`, and `_resolve_event_id` always picks
that up before it considers the freshly extracted `event_name="Holi"`.

```
> Where is the temple?
< Logistics for Bay Area Life Transformation Program 2026  …
```

Same root cause. Logistics intent + no fresh event_name + leaked
`selected_event_id=27` → returns BA LTP logistics.

```
> tell me about hanuman jayanti
< I'm not sure I caught that …
< *Holi Sadhana Shivir*  …  18th February â 22nd February 2026 …
< -
```

Three messages back, none of them right. The classifier said
`event_specific` but `event_name=None` because Hanuman Jayanti is not
in `EVENT_NAMES`. The mojibake `â��` (an en-dash that wasn't decoded
correctly) is in `description` from the 4B API.

### Bug map → fix map

| # | Bug | Root cause | Fix |
|---|---|---|---|
| **R3-1** | `selected_event_id` leaks across turns | `_resolve_event_id` always uses session id when classification has no `event_id` | Only use session id when current message is a follow-up — i.e. has no entities, no fresh query, AND intent is `logistics`/`sponsorship`/`single_event_detail` paired with explicit pronouns ("for it", "what about parking"). On any new top-level question, ignore session id. Plus: `main.py` clears session id when the current intent has any entity. |
| **R3-2** | `EVENT_NAMES` list is stale + manual | hand-maintained, missing Hanuman Jayanti, Janmashtami in API doesn't match anything currently (also missing) | Replace static list with a startup pull from the live API (`/api/v2/events`), tokenized into a name index. Survives 4B's data churn. |
| **R3-3** | "Where is the temple?" returns wrong event logistics | Cascade of R3-1 + no static venue answer | When the message is a generic "temple" question and no event is targeted, return a static **temple-info** block (address, hours, contact, livestream URL). Bot becomes the "everything about the temple" knowledge surface the user asked for. |
| **R3-4** | Mojibake `â��` in API descriptions | 4B scraper writes mis-decoded UTF-8 | Defensive: in `_value_or_blank`, fix the common pair `â\x80\x93` → `–` and `â\x80\x99` → `’`. Doesn't fix the 4B side but stops the bot from echoing garbage. |
| **R3-5** | Stray "- " message | unclear from logs; possibly a list rendering case where a list item has only a prefix | Audit `_format_event_list` and `_format_recurring_response` for `lines.append("- ")` empty bullet paths; guard against empty strings. |
| **R3-6** | Gemini quota exhausted | hit 20-req/day free tier limit | Add a Z.AI / GLM (`glm-4-flash` or `glm-4-air`) adapter using the user-supplied key as a fallback after Gemini 429. Keep the Jaccard floor as the third tier. |
| **R3-7** | Dead code: `closed.py`, `time.py`, `schedule-2.py` | re-added during student merges; not imported anywhere | Delete. Add a CI test that fails if any of them come back. |

### Order

1. **R3-1** first — it's responsible for most of the wrong responses in the transcript. One-line fix in `_resolve_event_id` plus a one-line clear in `main.py`. Smoke test.
2. **R3-3** next — wire a static "Where is the temple?" / "what are temple hours?" / "phone number" answer. Cheap and high-value for the "temple bot" framing.
3. **R3-4** — defensive mojibake repair. Trivial.
4. **R3-2** — dynamic EVENT_NAMES. Larger change but high ROI.
5. **R3-6** — Z.AI / GLM fallback adapter. Self-contained.
6. **R3-7** — delete dead files.

### Acceptance for Round 3

- After replying to a list with `2`, then asking `where is the temple?` → bot returns the **temple-info block**, not Bay Area LTP logistics.
- After replying with `2`, then `when is the holi event` → bot returns **Holi Sadhana Shivir**, not Bay Area LTP.
- "Tell me about Hanuman Jayanti" → either returns a Hanuman Jayanti event if one exists in the API, or a clean "we don't have that on the calendar yet — here's what's coming up" message. **Not** Holi.
- No `â��` in any bot output.
- `closed.py`, `time.py`, `schedule-2.py` removed from `4A/week8/`.
- With Gemini 429'd, classifier still returns useful intents on the 24-case smoke test (≥ 20/24 right, demonstrating the Z.AI fallback works).
