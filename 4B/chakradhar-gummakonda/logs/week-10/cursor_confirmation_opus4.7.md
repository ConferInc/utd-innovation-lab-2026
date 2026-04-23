# Final tasks for Team 4B
_Exported on 4/22/2026 at 18:32:38 CDT from Cursor (3.1.17)_

---

**User**

Team 4B,

This is your final week. Week 10 is about closing tech debt, tightening edge cases, and making sure the pipeline is production-solid. You set the standard last week ‚Äî now close the gaps.

---
Part 1 ‚Äî Week 8/9 Review
---

All three PRs merged into main: #39 (MOM), #40 (Team 4B), #41 (Team 4A).

Team 4B shipped a production-ready pipeline. Chakradhar's 4-layer recurrence validation (shared module ‚Üí Pydantic Literal ‚Üí ORM @validates ‚Üí DB CHECK constraints) is the strongest engineering artifact of the project. Sysha's unified category module and retry logic close every Week 7 scraper gap. Subodh delivered 8 integration tests with in-memory SQLite, LRU cache, and KB ingestion. Rohan's API security doc and handoff are production-quality. Beyond scope, the team also built a working bot (4B/week8/bot/) using Google Gemini ‚Äî the Render deployment is a fully functional end-to-end bot. Remaining: Stripe import not actually fixed (2-week-old flag ‚Äî Leena), stress test artifacts still tracked in git despite .gitignore update.

Team 4A shipped their first PR with executable Python. Chanakya's response builder and Rujul's classifier are solid, but they have critical hardcoded responses in their bot entry point that must be removed this week. Their integration with your live API is the week's primary goal.

---
Part 2 ‚Äî State of the Project Going into Week 10
---

Week 10 is the final integration and cleanup week. The pipeline is deployed; the demo happened April 15. What remains:

- Team 4A must wire its own components together properly (classifier ‚Üí response builder ‚Üí API ‚Üí recurring handler). Right now they have hardcoded overrides.
- Team 4B must close remaining tech debt (Stripe import, tracked artifacts) and tighten edge cases that will surface in production use.
- Both teams must make the end-to-end flow work against Team 4B's live Render URL ‚Äî not a local mock.

Goal by Wednesday April 22: A user sends a WhatsApp message ‚Üí Team 4A's bot classifies ‚Üí calls Team 4B's live API ‚Üí returns formatted real temple data. No hardcoded answers. No string-matching shortcuts. No fabrication. The pipeline is the product.

---
Part 3 ‚Äî Individual Tasks
---

Rohan Kothapalli (API/Deploy/Cleanup):
1. git rm --cached on the 6 stress test result files in 4B/week8/stress_test/*.json and *.txt. The .gitignore prevents new files but doesn't retroactively untrack.
2. git rm --cached on final_review_gate.py at repo root (AI tooling artifact).
3. git rm --cached on 4B/week6/.coverage and 4B/week7/.coverage.
4. Run the scraper fresh against both temple sites. Seed Render production. Confirm GET /api/v2/events returns at least 10 upcoming events (current seed returned only 2). Share updated proof in 4B/week8/docs/live-events-api-proof.md.
5. Coordinate with Harshith (Team 4A) ‚Äî confirm their bot webhook is calling the correct Render URL after Harshith removes hardcoded responses.

Chakradhar Gummakonda (Data Quality):
1. Add scraper data quality metrics to the next scrape-run log: total scraped, passed start_datetime parse, passed category inference (not "other"), count by source_site. This is the missing signal for why only 2 events show up in /events when 17 were scraped.
2. Investigate: of the 17 scraped events, how many have start_datetime in the past? How many have missing or future-invalid dates? Fix the upcoming filter or the seed pipeline accordingly.
3. (Optional polish) Add __repr__ to the Event ORM model for debuggable logs.
4. You delivered 10/10 this week ‚Äî keep Chanakya (4A) in the loop if any field-level schema questions arise from his live integration smoke test.

Sysha Sharma (Scrapers):
1. Replace substring matching in category_from_title.py with word-boundary regex (\b). Example: re.search(rf"\b{kw}\b", t) ‚Äî this prevents "class" from matching "classical" and avoids similar false positives. Current tests pass because the specific RKT/JKYog titles don't trigger these edge cases, but real-world data will.
2. Add a scraper observability metric: log the % of events where start_datetime was successfully parsed vs. skipped. This connects to Chakradhar's data quality work.
3. Document scraped_events.json output schema in jkyog.py and radhakrishnatemple.py module docstrings ‚Äî what fields are guaranteed, what can be null, what Pydantic validation will reject.
4. Coordinate with Chakradhar ‚Äî his upcoming-events filter may need your timezone handling fixes.

Subodh Nikumbh (Tests/Cache/KB):
1. Add the explicit LRU eviction boundary test that was asked for in Week 8/9 but missed: insert max_size + 1 entries, verify the oldest is evicted and the newest is retained.
2. Add an integration test covering the full bot-KB flow: seed events ‚Üí ingest_events ‚Üí search_kb("holi") ‚Üí verify the right event surfaces with the right fields.
3. Verify KB ingestion includes recurring programs. Currently ingest_events() pulls from get_upcoming_events() only. Add a recurring-events ingestion path so the intent classifier can find daily/weekly programs via KB search, not just direct API calls.
4. Write one end-to-end test: mock Twilio webhook ‚Üí Team 4B's bot pipeline ‚Üí confirm response formatted correctly. This is optional if Harshith delivers Team 4A's end-to-end test first.

Leena Hussein (Stripe ‚Äî CRITICAL):
1. Actually fix the Stripe import. In 4B/week8/api/stripe_webhooks.py, change line 2 from from integrations.stripe import StripeIntegration to from ..integrations.stripe import StripeIntegration. Commit with message fix(stripe): actually apply the relative import (2-week-old flag). The previous commit message claimed this fix but the file was unchanged.
2. Confirm pytest 4B/week8/tests/test_stripe_webhooks.py still passes after the import change.
3. Verify the Stripe webhook path documented in docs/demo-script.md (/api/stripe/webhook) matches what is actually registered in main.py. Document the exact URL to use when configuring the Stripe dashboard webhook.
4. Add one test for construct_webhook_event() that covers the signature verification path (currently all tests bypass signature verification and test only handle_webhook_event()).

---
Deadline: Wednesday, April 22, 2026 at 11:59 PM CST
Submission: PR into main per team, individual branches required, descriptive commit messages.
Demo expectation: By April 22, both teams' code must work together end-to-end against Team 4B's live Render URL with zero hardcoded responses and zero fabricated data.


Can you go through these tasks. I'm Chakradhar

---

**Cursor**

Chakradhar, here's a clean walkthrough of your four Week 10 tasks and where you stand on each. I'm in Ask mode so I can only inspect and advise — no edits.

## Your tasks (Team 4B, Data Quality)

### Task 1 — Scraper data quality metrics in the scrape-run log
**Status: Done.**

`4B/week8/data/scrape-run-2026-04-22.log` now carries the exact signal that was missing:

```1:15:4B/week8/data/scrape-run-2026-04-22.log
Week 8 scrape + seed run log (text summary) 
Date: 2026-04-22
Run by: Chakradhar Gummakonda
Environment: Windows, cmd, repo 4B/week8, .venv active

Scrape:
  Command: python -m scripts.scrape_events
  Output: data/scraped_events.json
  Summary: 30 events written; 15 skipped (invalid/missing start_datetime).
Scraper errors logged: 2
Scrape quality: total=56 parsed_dt=41 parse_rate=73.2% category_not_other=38 duplicates=11 deduped=30
Raw by source_site: jkyog=50, radhakrishnatemple=6
Validated by source_site: jkyog=39, radhakrishnatemple=2
Deduped by source_site: jkyog=28, radhakrishnatemple=2
```

All four asks are covered: total scraped (56), passed `start_datetime` parse (41), category not `other` (38), and source-site breakdown at raw/validated/deduped stages. The assignment literally lists these as the missing signals for why `/events` looked light — you've closed that loop.

### Task 2 — Investigate past-vs-future dates; fix filter or seed if broken
**Status: Done, with a clear diagnosis (no bug found).**

`4B/week8/data/task2-upcoming-analysis.md` is a solid investigation artifact. Your funnel is well-documented:

- 56 scraped → 41 with parseable `start_datetime` → 30 deduped into JSON → 21 DB rows after upsert collapse.
- DB split: `past=15`, `future=6`, `missing=0`.
- `/events?limit=20` returns 6, which exactly matches the 6 future rows — so the endpoint is truthful.

Your code-level check at `4B/week8/events/storage/event_storage.py` (the upcoming filter includes `is_recurring=True` with null/future end, and `is_recurring=False` with start/end >= now) is correct, and you confirmed the seed `updated=30, failed=0` accounts for all rows.

Your final diagnosis — *low count is historical-heavy source content + zero recurring rows because scrapers hardcode `is_recurring=False`* — is the right call. The instructions said "Fix the upcoming filter **or** the seed pipeline accordingly." Neither is broken, so no code change is warranted, and the doc already spells that out at lines 126–138.

One thing I'd suggest you add so this reads as a *decision*, not a *punt*:

- Explicitly call out the three hardcoded `is_recurring=False` sites (`jkyog.py:220`, `jkyog.py:392`, `radhakrishnatemple.py:396`) as **Sysha's scope / Week 10 follow-up**, since her task list includes timezone/parse-rate work but not recurrence flag inference. A one-line "Recommended next step (owner: Sysha)" paragraph in the conclusion section would make this a self-contained handoff rather than an open thread.

Also worth noting in the doc: the Render API also has `/today=0` and `/recurring=0`. Both are consistent with your DB state (no event starts today, `recurring_count=0`), so these are not bugs — just artifacts of the current scrape snapshot. Calling that out protects you from Rohan or Harshith flagging them during the Week 10 end-to-end test.

### Task 3 — Optional: `__repr__` on the Event ORM model
**Status: Done.**

Already in `4B/week8/database/schema.py`:

```298:309:4B/week8/database/schema.py
    def __repr__(self) -> str:
        start = self.start_datetime.isoformat() if self.start_datetime else None
        end = self.end_datetime.isoformat() if self.end_datetime else None
        source_site = self.source_site.value if hasattr(self.source_site, "value") else self.source_site
        return (
            f"<Event id={self.id} "
            f"name={self.name!r} "
            f"source_site={source_site} "
            f"start={start} "
            f"end={end} "
            f"is_recurring={self.is_recurring}>"
        )
```

This is well-designed — uses `!r` on `name` (quoted output survives logs with special chars), unwraps the enum safely, ISO-formats datetimes, and includes `is_recurring`. Exactly the debuggable-logs shape the brief asked for.

### Task 4 — Keep Chanakya (4A) in the loop on schema questions
**Status: Not a code task — just be reachable.**

Chanakya's Week 10 work is live-integration smoke testing Team 4B's API. The field names/shapes he'll hit are already visible in the `/events?limit=20` response you captured in terminal 9 — point him at `4B/week8/events/schemas/event_payload.py` if he asks. The Pydantic schemas there are the authoritative contract.

A useful proactive move: drop a short comment on Rohan's live-events proof PR (`4B/week8/docs/live-events-api-proof.md`, task 4 on his list) noting the `past=15/future=6` split from your analysis. That prevents anyone from misreading "only 6 events returned" as a bug during 4A's smoke test.

---

## Summary

All three technical tasks are complete, and the optional polish is in. The only two small improvements I'd suggest before your PR:

1. In `task2-upcoming-analysis.md`, explicitly frame the `is_recurring=False` hardcoding as a Sysha-owned Week 10 follow-up (so the doc ends with a clear next action rather than an open observation).
2. Note in the same doc that `/today=0` and `/recurring=0` are consistent with current DB state, not endpoint bugs — so the integration test reviewers don't flag them.

You're in good shape. Let me know if you want me to draft the exact wording for those two additions or look at anything else.

