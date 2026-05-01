# Week 11 tasks and backlog review
_Exported on 4/29/2026 at 00:55:21 CDT from Cursor (3.2.16)_

---

**User**

PART 2 ‚Äî WHAT WENT WRONG AND WHAT TO FIX (Backlog)

‚Ä¢ Rohan ‚Äî Three git rm --cached tasks skipped: Tasks 1, 2, and 3 on Rohan's Week 10 list were literal git rm --cached commands on stress-test result files (13 tracked in 4B/week5/, 4B/week6/, 4B/week7/, 4B/week8/), .coverage files (4B/week6/.coverage and 4B/week7/.coverage), and final_review_gate.py at the repo root. None were run. The .gitignore prevents new files but already-tracked files need explicit removal. final_review_gate.py was removed as a side-effect of Team 4A's root-artifact cleanup, so it is gone from main‚Äîbut not by Rohan's commit. Task 4 (>=10 upcoming events on live API) is also still missed‚Äîcurrent count is 6.

‚Ä¢ Chakradhar ‚Äî Placeholder-timestamp rows identified but not filtered: The Task 2 analysis correctly identified 11 DB rows where EXTRACT(SECOND FROM start_datetime) != 0, a signature of synthetic timestamps from the scraper. The finding is documented but there is no code-level filter or flag yet. For the demo, these 11 rows still exist in production Postgres and may surface in API responses.

‚Ä¢ Subodh ‚Äî Twilio E2E test mocks every component it touches: test_whatsapp_webhook_e2e.py verifies call orchestration (who was called in which order) but not actual message content. A companion test with a real SQLite backend and real classifier would catch more regressions. (Note: Marked optional in the Week 10 task list, so this is not a scoring deduction‚Äîit is a note for Week 11 if time permits).

‚Ä¢ Leena ‚Äî No package-level import regression test: The Stripe import fix was correct and the signature-verification test was added. But the test loads stripe.py via importlib.util.spec_from_file_location‚Äîwhich sidesteps the package import path. If someone flips the import back to absolute, main.py's startup will fail but the test suite will still pass. A def test_stripe_router_imports_cleanly(): import main would catch that.

‚Ä¢ Sysha ‚Äî Category keyword ordering: "yoga" lives under the class bucket, so "International Yoga Day" classifies as class rather than festival. Minor ordering concern with first-matching-bucket-wins. Not broken; stylistic improvement only.

---

PART 3 ‚Äî WEEK 11 TASKS (Polish Only, No New Features)

We are in the final stretch. The pipeline is wired, the deployment is live, the schema is locked. This is no longer a feature-delivery week‚Äîit is polish and prove it. If you find yourself starting a new abstraction, a new file, or a new contract document, pause and ask whether it is actually needed.

Priority 1 (Demo-Critical):

1. Rohan: Run the three git rm --cached commands from the Week 10 list. Verify with git ls-tree -r --name-only main | grep -E "stress_test_results|.coverage$" returning empty. Push.

2. Rohan + Chakradhar (Pair Task): Cross the 10+ upcoming-events threshold on the live API. Either deepen jkyog/temple scraper coverage OR seed a curated set of 4‚Äì5 demo events into Postgres. Refresh live-events-api-proof.md to show the new count and mark the Task 4 requirement as met.

3. Rohan: Canonicalize the Render URL across both teams. Today there are three URLs circulating: [REDACTED_RENDER_URL], [REDACTED_RENDER_URL], and [REDACTED_RENDER_URL]. Pick one, update Team 4A's .env.example and render.yaml, and update Team 4B's docs/demo-script.md and docs/live-events-api-proof.md. One URL everywhere.

Priority 2 (Polish, if Priority 1 is done):

4. Leena: Add test_stripe_router_imports_cleanly‚Äîimports main the way FastAPI does at startup. Catches regressions if the Stripe import flips back to absolute.

5. Chakradhar: Add a scraper-stage filter that rejects or flags rows with EXTRACT(SECOND FROM start_datetime) != 0. Closes the synthetic-timestamp finding from the Task 2 analysis.

Can you check for Chakradhar what are done and what aren't

---

**Cursor**

Here's where Chakradhar stands on the Week 11 task list.

## Chakradhar's Week 11 task status

### Priority 1, Task 2 (paired with Rohan) — Cross 10+ upcoming events on the live API

**Done.**

- `4B/week11/docs/live-events-api-proof.md` was refreshed and now shows **22 upcoming events** on `GET /api/v2/events?limit=100&offset=0`, well above the 10-event requirement.

```24:32:4B/week11/docs/live-events-api-proof.md
- Live endpoint count check:
  - `GET /api/v2/events?limit=100&offset=0` returned `22` rows
  - Computed `upcoming` rows from `start_datetime >= now`: `22`

## Week 10 completion check (Task 4 requirement)

- Requirement: confirm at least `10` upcoming events.
- Current live result: `22` upcoming events.
- Status: **met** (live deployment is above the required threshold).
```

The proof also records the upstream scraper funnel that produced the 22 — `Wrote 49 events`, `parse_rate=87.5%`, `deduped=49`, and `rejected_synthetic_second=3` — which ties directly into Task 5 below.

### Priority 2, Task 5 — Scraper-stage filter for `EXTRACT(SECOND FROM start_datetime) != 0`

**Done.**

The filter was added at the scraper validation stage in `scrape_all.py`, not as a DB-side guard, which is the right layer (rejects synthetic rows before they ever reach Postgres):

```140:160:4B/week11/events/scrapers/scrape_all.py
            # Week 11 data-quality guard: real calendar times are minute-granular
            # (HH:MM:00). Non-zero seconds typically come from dateutil fuzzy
            # parsing inheriting `now_local` seconds when source text lacks an
            # explicit time. See Week 10 Task 2 analysis.
            parsed_start = parse_storage_datetime(event.get("start_datetime"))
            if parsed_start is not None and parsed_start.second != 0:
                rejected_synthetic_second += 1
                errors.append(
                    {
                        "source": event.get("source_site", "unknown"),
                        "stage": "rejected_synthetic_second",
                        "url": event.get("source_url", ""),
                        "name": event.get("name"),
                        "detail": (
                            "start_datetime seconds != 0; treated as synthetic "
                            "timestamp from fuzzy parse fallback"
                        ),
                    }
                )
                continue
            validated.append(event)
```

Surfacing of the metric:

- The counter is added to the returned payload as `rejected_synthetic_second` (`scrape_all.py:187`) and to the metrics dict (`scrape_all.py:69`, `:101`).
- The CLI runner reads and prints it: `4B/week11/scripts/scrape_events.py:54, :68`.
- A regression test pins the contract — `test_compute_metrics_exposes_rejected_synthetic_second` in `4B/week11/validation_tests/test_scrape_all_metrics.py:74-96`, including the assertion that synthetic-second rejections are **not** counted as scraper bugs (`scraper_errors_logged == 0`).

The 4/22 production analysis (`4B/week11/data/task2-upcoming-analysis.md`) had identified 11 such rows; the latest scrape recorded 3 rejections live — the filter is firing in production.

### Net for Chakradhar

Both Week 11 items assigned to him are complete:

| # | Task | Status |
|---|---|---|
| P1.2 | 10+ upcoming events on live API (paired with Rohan) | Done — 22 reported in `live-events-api-proof.md` |
| P2.5 | Scraper-stage filter for `seconds != 0` | Done — implemented in `scrape_all.py`, tested in `test_scrape_all_metrics.py`, firing in production (`rejected_synthetic_second=3`) |

One small follow-up worth flagging (not on his list, but adjacent to his work): the 11 placeholder-second rows that already exist in production Postgres from earlier seeds are still there. The new scraper filter prevents future ones, but it does not retroactively clean the historical 11. If the demo wants those gone too, a one-shot SQL cleanup or a re-seed with the new pipeline is what would close that loop — but per the Week 11 ground rules ("polish only, no new features"), the filter alone satisfies the assigned task.

