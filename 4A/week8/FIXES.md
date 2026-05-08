# Week 12 Fixes — Team 4A Bot Pipeline

**Branch:** `Shrikanth-week12-fixes`
**Author:** Shrikanth
**Date:** May 5, 2026
**Status:** All 5 bugs fixed and verified end-to-end against the live Team 4B API.

---

## TL;DR

Five bugs were preventing the bot from returning correct output, even though the architecture (classifier → session → builder → API / recurring handler) was structurally complete after Week 11. This branch fixes all five and adds a 32-case verification harness that you can run with one command.

| # | Bug | One-line root cause | Files touched |
|---|---|---|---|
| 1 | Recurring handler not wired | `response_builder.py` imported from a non-existent `schedule` module; the silent ImportError disabled the entire recurring intent path | `response_builder.py`, `requirements.txt` |
| 2 | Entity routing mismatch | `_resolve_query()` never looked at `entities.event_name` / `entities.program_name`; `EVENT_NAMES` is a tiny hard-coded list that misses every live scraped event | `response_builder.py`, `main.py` |
| 3 | Sponsorship had no generic path | "How can I donate?" tried to resolve a single event, found nothing, returned "I could not find any matching events" | `response_builder.py` |
| 4 | Confidence threshold gate was broken | Week 11 narrowed clarification to fire only when intent==`ambiguous`; non-ambiguous intents at confidence 0.04 still proceeded | `intent_classifier.py` |
| 5 | Gemini cold-start was 27s | Fresh `genai.Client(...)` was constructed on every WhatsApp message; first call paid TLS + model warmup; Twilio's webhook timeout is 15s | `intent_classifier.py`, `main.py` |

**Verification:** `verify_week12_fixes.py` runs 32 representative WhatsApp messages through `classify()` + `build_response()` against the live Render API and checks expected substrings / forbidden substrings / size limits. Result: **32/32 passing** in Jaccard-only mode (no Gemini quota burnt). Gemini path also confirmed working with a separate spot check (`spot_check_gemini.py`).

---

## How to read this document

Each bug section has the same structure:

1. **Symptom** — what users (or the harness) saw before the fix.
2. **Root cause** — exactly which code path was wrong and why.
3. **The fix** — what changed, in plain language, with file + concept references.
4. **Why this is the right fix** — alternatives we considered and why we didn't take them.
5. **How to verify** — the test cases that exercise this fix.

You should be able to internalise a bug by reading just sections 1–3. The code itself has Week 12 inline comments that mirror this document. If you want to see the actual code, the comments will tell you which lines to look at.

---

## Bug 1 — Recurring Schedule Handler Not Wired

### Symptom

User: *"When is Sunday Satsang?"*
Bot: *"I could not find any matching events for **recurring events** right now."*

This was the headline issue from the Week 11 review: PR #45 claimed the recurring handler was wired, but it wasn't.

### Root cause (multi-layered)

Three independent failures stacked on top of each other:

1. **`response_builder.py` imported from the wrong module.** Line 23 (pre-fix) said:

   ```python
   try:
       from schedule import get_current_schedule
   except Exception:
       get_current_schedule = None
   ```

   There is no `schedule.py` in `4A/week8/`. There *is* a `schedule-2.py` file, but Python cannot import a module whose name contains a hyphen with a normal `import` statement. The `except Exception` block swallowed the `ModuleNotFoundError` and left `get_current_schedule = None`. The recurring branch then always took the fallback path that called Team 4B's `/recurring` endpoint, which returns `{"events": []}` because temple programs are not scraped.

2. **`schedule-2.py` itself is broken.** Its first non-comment line is `from schedule_data import SCHEDULE` — but no `schedule_data.py` exists in the directory either. So even if you fixed the hyphen problem (e.g. by renaming `schedule-2.py` to `schedule_handler.py`), the import would still fail at line 3 of that file.

3. **`zoneinfo` cannot find `America/Chicago` on Windows.** The original `recurring_handler.py` (Week 8) is fully functional and self-contained, but on Windows it raises `ZoneInfoNotFoundError` at import time because Python's `zoneinfo` reads from the system tz database, which Windows does not have. This failure was masked by the `try/except` in `response_builder.py`.

### The fix

- Switched `response_builder.py` to import from `recurring_handler` (the original, working Week 8 module). It exposes `get_current_schedule(now)`, `get_next_occurrence(program, now)`, and a `TIMEZONE = ZoneInfo("America/Chicago")` constant that we reuse so the response is always formatted in temple-local time.
- Replaced the old single-line `_format_active_recurring_schedule()` helper with a richer `_format_recurring_response(program_hint=...)`. It handles:
  - The general "what's running right now" snapshot (live programs + upcoming-within-2-hours + any closure exceptions).
  - A program-specific question ("When is Sunday Satsang?") — uses `get_next_occurrence()` and shows day + clock window.
  - The "no programs running, here are the basics" fallback so the user never gets a blank reply.
- Added a `RECURRING_PROGRAM_ALIASES` dict that maps the user's possible phrasings (`"sunday satsang"`, `"daily bhajans"`, `"prasad"`, `"kirtan"`, etc.) to the canonical program keys (`"satsang"`, `"bhajans"`, `"mahaprasad"`, `"bhajans"`).
- Added `tzdata>=2024.1` to `requirements.txt` so `zoneinfo.ZoneInfo("America/Chicago")` works on Windows. (On Linux/Mac it reads the system tz database; on Windows there is none and `tzdata` provides it.)

### Why this is the right fix

- We did **not** rename `schedule-2.py` because the file itself is broken (its `schedule_data` import) and there is already a working module (`recurring_handler.py`) that does the same job better.
- We did **not** delete the broken files (`schedule-2.py`, `time.py`, `closed.py`) — they are kept as archival artifacts so the team can see the trail of what was attempted. They are no longer imported anywhere.
- Using the original Week 8 `recurring_handler.py` keeps the "single source of truth" invariant — there is one canonical schedule data structure, not three.

### How to verify

Run `verify_week12_fixes.py`. The five recurring-schedule cases all pass:

```
[PASS] rec_sunday_satsang     | intent=recurring_schedule | *Satsang schedule:* Next: Sunday, 10:30 AM 12:30 PM CT
[PASS] rec_aarti_time         | intent=recurring_schedule | *Aarti schedule:* Next: Tuesday, 12:15 PM 12:45 PM CT
[PASS] rec_temple_hours       | intent=recurring_schedule | *Temple recurring schedule* ...
[PASS] rec_darshan_today      | intent=time_based         | (correctly routed elsewhere because "today" hits time_based)
[PASS] rec_daily_bhajans      | intent=recurring_schedule | *Temple recurring schedule* ...
```

---

## Bug 2 — Entity Routing: `program_name` vs `event_name` Slot Collision

### Symptom

User: *"Where is the Bhakti Kirtan Retreat?"*
Bot: *"I could not find any matching events for **your request** right now."*

The live Team 4B API has an event titled "Bhakti Kirtans & Satsang" that perfectly matches that query. Why did the bot say it couldn't find anything?

### Root cause

Two interacting issues:

1. **`entity_extractor.py` has two hard-coded lists**: `EVENT_NAMES` (festivals like Holi, Diwali, etc.) and `PROGRAM_NAMES` (recurring programs: Aarti, Kirtan, Satsang, etc.). It loops through both in order and assigns to whichever matches. `"Kirtan"` is in `PROGRAM_NAMES` but not in `EVENT_NAMES`, so even though the user is asking about a one-off retreat, the extractor stuffs `"Kirtan"` into `entities.program_name` and leaves `entities.event_name` empty. Hard-coded `EVENT_NAMES` will *never* contain the live scraped event titles like "Bhakti Kirtans & Satsang" or "Seattle Life Transformation Program 2026".

2. **`response_builder._resolve_query()` only looked at top-level keys** on the classification dict (`query`, `event_name`, `entity`, `keyword`, `last_query`). It never looked inside `classified_intent["entities"]`. So even when entity extraction *did* populate something (in either `event_name` or `program_name` slot), the response builder saw nothing and routed to the no-results message.

### The fix

In `_resolve_query()` (response_builder.py):

- Now walks the nested `entities` dict explicitly, reading `entities.event_name` then `entities.program_name`.
- Order: explicit query → top-level event_name → entity → keyword → entities.event_name → entities.program_name → session.last_query. So a more-specific extracted entity wins over the more general program-name fallback.

For intents that need a target (`event_specific`, `logistics`, `sponsorship`), introduced `_search_term_with_message_fallback()`:

- If `_resolve_query()` returned nothing, fall back to the raw user message (passed through from `main.py` as `context["user_message"]`).
- The fallback strips question words and filler tokens (`what`, `where`, `the`, `tell`, `me`, `about`, etc.) so "Where is the Bhakti Kirtan Retreat?" becomes "bhakti kirtan retreat" and reaches `/api/v2/events/search`.
- This fallback is deliberately **not** used by `discovery` / `time_based` / `recurring_schedule` because those intents don't need a target — using the raw message would corrupt them ("What's happening this weekend?" should not become a search for the literal phrase).

In `main.py`:

- `process_message_background()` now adds `context["user_message"] = body_text` so the response builder has the raw text available.

### Why this is the right fix

- We did **not** try to expand `EVENT_NAMES` to mirror the live scraper. The scraper's catalogue changes every week — keeping a hard-coded list in sync would be a permanent maintenance tax. The right pattern is "send the user's words to the search endpoint and let the database be the source of truth."
- We did **not** drop `EVENT_NAMES` entirely. It still helps when a user types a clear festival name like "Holi" or "Diwali" — the entity extractor catches it cleanly and we don't need to call `/search`.
- The question-word strip is conservative — it only drops common filler tokens, never proper nouns, dates, or unfamiliar words. So "What is Janmashtami?" becomes "janmashtami" and "I want to go to Lohri 2026" stays largely intact.

### How to verify

```
[PASS] event_holi             | intent=event_specific | *Holi Sadhana Shivir* When: Feb 18, 2026 5:30 AM ...
[PASS] event_kirtan_retreat   | intent=event_specific | *Bhakti Kirtans & Satsang* When: Apr 7, 2026 12:00 AM ...
[PASS] event_ltp              | intent=event_specific | (LTP query reaches search and returns Life Transformation Programs)
[PASS] logistics_holi_where   | intent=event_specific | *Holi Sadhana Shivir* ...
[PASS] logistics_kirtan_directions | intent=event_specific | *Bhakti Kirtans & Satsang* ...
```

---

## Bug 3 — Sponsorship Had No Generic Donation Path

### Symptom

User: *"How can I donate?"*
Bot: *"I could not find any matching events for **your request** right now."*

Donating to the temple is generic information; it doesn't require an event to exist. The bot was treating sponsorship as if it always needed an event target.

### Root cause

`response_builder.py` sponsorship branch (pre-fix):

```python
if intent in {"sponsorship", "sponsorship_tiers"}:
    event = _resolve_single_event(client, event_id=event_id, query=query)
    if event is None:
        return _format_no_results(query or "your request")
```

When the user has no specific event in mind, both `event_id` and `query` are `None`. `_resolve_single_event()` short-circuits and returns `None`. The branch falls into `_format_no_results()` — exactly the wrong message.

### The fix

- Added `_format_generic_sponsorship()` which returns real, non-fabricated guidance with the temple's public donation links and a list of seva categories (annadaan, deity bhog, festival sponsorship, LTP sponsorship).
- Updated the sponsorship branch to call the generic helper when:
  - There's no `event_id`, AND
  - There's no search term (after the Bug 2 user-message fallback also returns nothing).

When the user *does* mention a specific event ("Sponsorship tiers for Holi"), the branch still resolves the event and returns the per-event sponsorship tiers, exactly as before.

### Why this is the right fix

- The links in the generic response (`jkyog.org/donate`, plus the seva categories) are **real, public, non-fabricated** information about the temple. They belong to the bot's static knowledge — not invented per query.
- We did **not** add a "Stripe checkout link" to the generic response. That belongs to a different sub-intent ("how do I pay?") and would need careful integration with Team 4B's Stripe webhook flow.
- The generic response *invites* the user to mention a specific event for tiered sponsorship — preserving the existing per-event flow as a natural next step.

### How to verify

```
[PASS] sponsor_donate_generic | intent=sponsorship | *Donations & Seva at JKYog Radha Krishna Temple* ...
[PASS] sponsor_seva_generic   | intent=sponsorship | *Donations & Seva at JKYog Radha Krishna Temple* ...
[PASS] sponsor_specific_event | intent=event_specific | *Holi Sadhana Shivir* ... (per-event path still works)
[PASS] sponsor_annadaan       | intent=sponsorship | (mentions Annadaan as seva option)
```

---

## Bug 4 — Confidence Threshold Was Effectively Disabled

### Symptom

User: *"info"*
Bot returned a list of upcoming events instead of asking for clarification.

The Week 11 PR description said: *"Refined confidence fallback to only trigger clarification for ambiguous intents."* This was the wrong fix — it narrowed the safety net to the point that it never fired for misclassifications.

### Root cause

The pre-fix logic at the bottom of `classify()`:

```python
if result["confidence"] < 0.6 and result["intent"] == "ambiguous":
    result["intent"] = "clarification_needed"
```

Two problems:

1. `intent == "ambiguous"` is the wrong predicate. If the classifier already labelled the message ambiguous, the routing was right. The dangerous case is when the classifier labelled it `sponsorship` *with confidence 0.04* — that classification is essentially noise but the rule above doesn't catch it.
2. There was no tokenization fix, so `"How can I donate?"` (with the trailing `?`) had `tokens = {"how", "can", "i", "donate?"}`. The Jaccard intersection with the sponsorship keyword set `{"donate", "donation", ...}` was empty because `donate?` ≠ `donate`. Confidence collapsed to 0 and the bot mis-classified messages that should have been easy.

### The fix

Three changes in `intent_classifier.py`:

1. **Tokenizer strips punctuation.** `tokenize()` now uses a regex to replace non-word characters with spaces before splitting. `"How can I donate?"` → `{"how", "can", "i", "donate"}`. The Jaccard intersection with the sponsorship keywords now correctly returns `{"donate"}`.
2. **Routing rule bypasses the numeric score and uses a `has_signal` flag.** `_classify_with_jaccard()` returns `has_signal=True` when at least one keyword or entity match drove the routing decision; `False` only when nothing matched and the classifier defaulted to `ambiguous`. The downstream gate now redirects to `clarification_needed` only when `has_signal == False` (or when Gemini explicitly returned `ambiguous` with low confidence). Numeric Jaccard scores in the 0.05–0.20 range are no longer treated as "low confidence" because Jaccard ratios over small keyword sets are intrinsically small even on correct classifications.
3. **Routing precedence reshuffled.** Discovery (plurals like "events") now beats event_specific (singular "event") in the keyword chain. Program-name match beats timeframe (so "When is Sunday Satsang?" stays in `recurring_schedule` instead of being stolen by the date regex extracting "sunday" as a timeframe). New `EVENT_OVERRIDE_TOKENS` set means a program-name match flips to `event_specific` when the user says "retreat" / "festival" / "celebration" — handling cases like "Bhakti Kirtan Retreat".
4. **Several keyword sets expanded:** added `coming up`, `show me`, `list` to discovery; `annadaan`, `seva opportunity` to sponsorship; `temple hours`, `what time`, `schedule today` to recurring_schedule; `ltp`, `life transformation`, `shivir`, `yatra` to event_specific.

### Why this is the right fix

- The numeric confidence score from Jaccard is **a similarity ratio, not a probability**. Treating it like a probability ("< 0.30 means low confidence") is the wrong abstraction. The right signal is "did we find a real match?", which is exactly what `has_signal` reports.
- We kept the `ambiguous` rule because it's still useful — when Gemini explicitly says "ambiguous" with low confidence, it knows it doesn't know, and clarification is the right action.
- Tokenization fix is critical and applies to **every** Jaccard classification — punctuation-handling was a hidden tax on every message.

### How to verify

Cases that exercise the threshold:

```
[PASS] sponsor_donate_generic | intent=sponsorship          | (donate? now matches via fixed tokenizer)
[PASS] amb_info               | intent=clarification_needed | (no keyword match → ambiguous → clarification)
[PASS] amb_help               | intent=clarification_needed | (same)
[PASS] amb_more               | intent=clarification_needed | (same)
[PASS] edge_emoji_only        | intent=clarification_needed | (no signal at all)
[PASS] edge_typo_fasival      | intent=discovery            | ("up" is not a discovery match but "coming up" caught via new keywords)
```

The full 32-case suite is also a regression test for this rule — any future change that re-narrows clarification will be caught immediately.

---

## Bug 5 — Gemini Cold-Start was 27 Seconds (> Twilio's 15s timeout)

### Symptom

The first WhatsApp message after deploy or after Render's free-tier idle-timeout took ~27 seconds end-to-end. Twilio's webhook timeout is 15 seconds. So Twilio retried the webhook (sometimes multiple times), and the user saw either nothing, a delayed reply, or a duplicate reply.

### Root cause

`_classify_with_gemini()` (pre-fix) constructed a fresh `genai.Client(...)` on every call:

```python
def _classify_with_gemini(user_message: str) -> Dict | None:
    if not GOOGLE_AVAILABLE or not os.getenv("GOOGLE_API_KEY"):
        return None
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))   # ← fresh per call
        response = client.models.generate_content(...)
```

Two consequences:

- Each call paid the cost of TLS handshake, DNS resolution, and the SDK's internal initialisation. This adds 1–3 seconds even on warm connections.
- The first call from a cold-started container also paid Google's "model warm-up" cost — sometimes ~25 seconds for `gemini-2.5-flash-lite` if the model instance has been idle.

### The fix

In `intent_classifier.py`:

- Module-level `_GEMINI_CLIENT` singleton via `_get_gemini_client()` that lazy-initialises once and returns the same client on subsequent calls.
- New `warm_up()` function that issues a single, tiny throwaway classification at startup (input: `"ping"`, max_output_tokens=4) so the TLS / DNS / model-warmup costs are paid before the first real user message ever arrives.

In `main.py`:

- Added a FastAPI `lifespan` async context manager that calls `warm_up()` once during startup. Controlled by `GEMINI_WARMUP=1` env var (default on); set `GEMINI_WARMUP=0` to skip if you're running offline tests.

### Measured impact

| Phase | Before | After |
|---|---|---|
| Server startup | instant | +13.4s (one-time, before first request is served) |
| First user message | ~27s | ~7.5s |
| Second user message | ~1s | ~2.4s |
| Tenth user message | ~1s | ~1s |

The first user message is now **inside** Twilio's 15s webhook timeout. (Note: even before the fix, the bot's webhook handler returns `{"status": "accepted"}` immediately and processes in a background task — so Twilio's 15s budget was never the actual bottleneck for the user-perceived latency. But Render's worker would still time out and Twilio would still retry. Both pathologies are now gone.)

### Why this is the right fix

- We did **not** switch to a non-Google LLM. Gemini works; the issue was instantiation pattern.
- We did **not** pre-classify every possible message into a cache. That would be over-engineering and would not generalise.
- The singleton + warm-up pattern is exactly what Google's own SDK examples recommend for production deployments.

### How to verify

`spot_check_gemini.py` runs warm_up() then 3 classifications and prints elapsed time per call. You'll see warm_up at ~13s and subsequent calls at single-digit seconds.

---

## Files changed in this branch

| File | Reason |
|---|---|
| `4A/week8/intent_classifier.py` | Bugs 4 + 5: tokenizer fix, routing precedence, expanded keyword sets, Gemini singleton + warm_up. |
| `4A/week8/response_builder.py` | Bugs 1 + 2 + 3: switch to `recurring_handler` import, new `_format_recurring_response`, nested-entity query resolution, raw-message fallback for target intents, generic sponsorship path. |
| `4A/week8/main.py` | Bug 5: FastAPI lifespan calls `warm_up()` at startup. Bug 2: passes `body_text` through to context. Bug 4: clarification reply moved up so we never call build_response on a `clarification_needed` intent. |
| `4A/week8/requirements.txt` | Bug 1: added `tzdata>=2024.1` so `zoneinfo("America/Chicago")` works on Windows. |
| `4A/week8/verify_week12_fixes.py` | New 32-case end-to-end verification harness (live API). |
| `4A/week8/spot_check_gemini.py` | Tiny Gemini cold-start latency spot check. |
| `4A/week8/debug_harness.py` | Pre-existing diagnostic harness from the original investigation. |
| `4A/week8/FIXES.md` | This document. |

**Files deliberately NOT changed**:

- `4A/week8/recurring_handler.py` — already correct, just wasn't being imported. Now is.
- `4A/week8/schedule-2.py`, `4A/week8/time.py`, `4A/week8/closed.py` — orphaned files from the Week 10/11 schedule-data thrash. Not imported by anything in this branch. Kept for historical reference; safe to delete in a future cleanup.
- `4A/week8/entity_extractor.py` — not strictly broken; the slot-collision behaviour is now compensated for in `response_builder.py` and `intent_classifier.py`.

---

## How to run the verification suite yourself

From `4A/week8/`:

```
# One-time setup
python -m venv .venv
.venv/Scripts/pip.exe install -r requirements.txt

# Create a local .env (gitignored) with at minimum:
#   GOOGLE_API_KEY=AIza...
#   EVENTS_API_BASE_URL=https://jkyog-whatsapp-bot-week4-ffuk.onrender.com
#   TWILIO_ACCOUNT_SID=ACdebug00000000000000000000000000     (any stub will do)
#   TWILIO_AUTH_TOKEN=debug_auth_token
#   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
#   ENV=development

# Run the full suite (uses Gemini ~1 quota/case → 32+1 quota; Gemini free tier is 20/day)
.venv/Scripts/python.exe verify_week12_fixes.py

# Run without burning Gemini quota (forces Jaccard fallback path for every case)
FORCE_JACCARD_ONLY=1 .venv/Scripts/python.exe verify_week12_fixes.py

# Just the cold-start spot check (uses ~4 Gemini quota)
.venv/Scripts/python.exe spot_check_gemini.py
```

Both runs should report **PASSED 32/32 FAILED 0**.

If you add a new intent or change behaviour, add a `Case(...)` entry to `build_cases()` with `must_contain` / `must_not_contain` expectations and re-run. The harness is designed to be the regression net for this codebase — keep it green.

---

## What this does NOT fix

These are out of scope for Week 12 but worth knowing:

1. **Session context still not consumed by build_response.** Harshith's `ACTIVE_SESSIONS` dict tracks `last_intent` and `selected_event_id`, but the response builder doesn't yet read them to enable multi-turn follow-ups ("tell me more about that one"). This is the next natural extension of the bot.
2. **Entity extractor's `EVENT_NAMES` list is still hard-coded and stale.** The Bug 2 fix routes around it (raw-message fallback to /search), so this is no longer a *correctness* issue — but it is a maintenance smell. A future PR could replace the static list with a periodic snapshot of upcoming-event names from the API.
3. **Gemini free-tier quota is 20 requests/day on `gemini-2.5-flash-lite`.** The bot will gracefully fall back to Jaccard once quota is exhausted (this is well-tested in `FORCE_JACCARD_ONLY=1` mode), but in production you'd want to upgrade to a paid Gemini tier or switch to Grok via the `LLM_PROVIDER` env var.
4. **`schedule-2.py`, `time.py`, `closed.py` are dead code.** They can be deleted whenever the team is comfortable losing the historical artifacts.

---

*End of Week 12 fixes report.*
