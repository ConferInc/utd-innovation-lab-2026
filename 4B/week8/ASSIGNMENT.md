# Week 8/9 Assignment — Group 4B
## Integration Sprint: Deploy, Align & Support the Demo
**Sprint: April 7 – April 15, 2026**

---

## 🎯 This Sprint's Mission

Team 4B's pipeline is functionally complete — scrapers running, database seeded, five API endpoints live, auth hardened. This sprint is about getting that work into production and making it usable by Team 4A so the demo works on April 15.

Three blockers from Week 7 will fail the demo if not fixed:
1. The Stripe webhook import error crashes the app at startup
2. The events router serves at `/events` but Team 4A's contract says `/api/v2/events`
3. The sponsorship tier schema is mismatched between both teams

Fix those first. Then execute the tasks below.

You are expected to use AI coding tools (Cursor, Copilot, Claude) where they help. Document what you used them for in your summary email.

---

## Context: What Team 4A Is Building

Team 4A will implement:
- An intent classifier that maps WhatsApp messages to one of 8 intents
- A response builder that calls your events API and formats WhatsApp responses
- A bot entry point that wires Twilio → classifier → API call → WhatsApp reply

For their bot to work, they need:
1. Your API live and reachable at a public Render URL
2. The events router at `/api/v2/events` (not `/events`)
3. Agreed-upon field names in the events schema (especially sponsorship tiers)
4. A SQLite fallback so they can test locally without Render credentials

Your Render URL and the schema alignment decisions must be confirmed at the **April 9 cross-team sync**.

---

## Individual Assignments

---

### Rohan Bhargav Kothapalli (Lead) — API Alignment, Deployment & Auth Polish
**Make the API production-ready and get it live for Team 4A.**

Deliverables:

1. **Fix: Events Router Prefix (BLOCKER)**
   - Change the events router mount in `main.py` from `/events` to `/api/v2/events`
   - This is a one-line change in `main.py`
   - Confirm with Team 4A that their `api_client.py` uses the same base path
   - Update `.env.example` to include the correct path format

2. **Fix: `.coverage` and Artifact Cleanup**
   - Add `.coverage`, `*.coverage`, `stress_test_results_*.json`, `stress_test_results_*.txt`, and `data/scraped_events.json` to `.gitignore`
   - These run-output artifacts committed in Week 7 should not be in version control
   - Do NOT delete the files locally — just add them to `.gitignore`

3. **Deploy to Render — Full Stack**
   - Deploy `4B/week8/` (carrying forward all Week 7 infrastructure) to Render
   - Confirm the following are working on the live deployment:
     - `GET /api/v2/events` returns events from the database
     - `GET /api/v2/events/today` returns today's events
     - `GET /api/v2/events/recurring` returns recurring programs
     - `GET /health` returns 200
     - Escalation auth still works (Bearer token)
   - **Share the Render base URL with Team 4A by April 9 at 7:00 PM CST** (before the sync meeting)
   - Share URL in `assignments/week-08-09-sync-notes.md` and in #utd-innovation-lab Slack

4. **Auth Decision for `/events` Endpoints**
   - The events API is currently unauthenticated (public read)
   - Document this as a deliberate design choice in `4B/week8/docs/api-security.md` (1 page max):
     - Why `/events` endpoints are public (read-only, no PII)
     - Which endpoints require auth (escalations, Stripe webhooks)
     - What would need to change if user-specific data is added later
   - Share this doc with Team 4A so they know whether to send auth headers

---

### Chakradhar Reddy Gummakonda — Schema Alignment & Database Hardening
**Resolve the cross-team schema mismatches and strengthen the data layer.**

Deliverables:

1. **Schema Alignment (BLOCKER — due by April 9 sync)**
   - The sponsorship tier schema must match Team 4A's response templates before both teams write integration code
   - Current Team 4B storage: `{ name: str, amount: str, link: str }`
   - Current Team 4A template expects: `{ tier_name: str, price_usd: float, price_inr: float, description: str }`
   - At the April 9 sync, agree on ONE canonical format with Chanakya (4A)
   - After the sync: update `event_storage.py` normalizer if the field names change
   - Update the Pydantic `SponsorshipTier` model in `event_payload.py` to match the agreed schema
   - Document the agreed schema in `4B/week8/docs/schema-decisions.md`

2. **Fix: `recurrence_pattern` Validation**
   - `_matches_recurrence()` in `event_storage.py` supports `daily`, `weekdays`, `weekends`, `weekly:<day>`
   - Add an ORM-level validator or a DB CHECK constraint so only supported values can be inserted
   - Unsupported patterns (e.g., "monthly:15", "biweekly") should raise a `ValueError` at write time, not silently return `False` at query time
   - Update the Pydantic schema in `event_payload.py` to enforce this with a `Literal` type or regex validator

3. **SQLite Local Dev Fallback (4-WEEK OPEN FLAG)**
   - Add a `DATABASE_URL` environment variable check in `database/connection.py` (or equivalent)
   - If `DATABASE_URL` starts with `sqlite:///`, configure SQLAlchemy for SQLite instead of PostgreSQL
   - This allows Team 4A (and any new developer) to run the full stack locally without Render credentials
   - Add a `.env.local.example` file showing the SQLite configuration:
     ```
     DATABASE_URL=sqlite:///./local_dev.db
     ```
   - Add `local_dev.db` to `.gitignore`
   - Test that all 5 event endpoints work with the SQLite fallback

4. **Run the Scraper & Seed Live Data**
   - Trigger `scrape_all.py` against both temple websites from your local machine
   - Seed the Render production database with the scraped events
   - Confirm `GET /api/v2/events` on the live Render deployment returns real data
   - Commit the scraper run logs as `4B/week8/data/scrape-run-april-2026.log` (text summary, not the full JSON)

---

### Sysha Sharma — Scraper Hardening & Category Coverage
**Make the scrapers more robust and close the category gap before the demo.**

Deliverables:

1. **Retry Logic for `RespectfulHttpClient`**
   - Add a retry policy for transient errors in `events/scrapers/http_client.py`
   - On HTTP 5xx or connection timeout: retry up to 3 times with exponential backoff (1s, 2s, 4s)
   - On HTTP 4xx: do not retry — log the error and skip that URL
   - Add a `max_retries` and `backoff_factor` parameter to `RespectfulHttpClient.__init__` (configurable, not hardcoded)

2. **Expand `_guess_category` in Both Scrapers**
   - Current coverage in `radhakrishnatemple.py`: only 4 categories (navratri, jayanti, ram, health)
   - The event schema supports: `festival`, `retreat`, `satsang`, `youth`, `class`, `workshop`, `special_event`, `other`
   - Expand the category mapping to cover the full set:
     ```python
     CATEGORY_KEYWORDS = {
         "festival": ["navratri", "diwali", "holi", "janmashtami", "rama navami", "hanuman"],
         "retreat": ["retreat", "camp", "spiritual camp"],
         "satsang": ["satsang", "kirtan", "bhajans", "aarti", "prayer"],
         "youth": ["yuva", "youth", "students", "UTD", "college"],
         "class": ["class", "workshop", "course", "seminar", "yoga", "meditation"],
         "health": ["health fair", "health camp", "medical"],
         "special_event": ["visit", "talk", "speaker", "swami", "lecture"],
     }
     ```
   - Apply the same expanded mapping to `jkyog.py`
   - Default to `"other"` for events that don't match any keyword

3. **Document JavaScript Rendering Limitation**
   - Add a module-level docstring to both scraper files explaining:
     - Both scrapers use static HTML parsing (httpx + BeautifulSoup)
     - Events rendered via JavaScript will be silently missed
     - What to do if a scraper stops returning results: check if the site changed to a JS-rendered frontend
     - Potential upgrade path: Playwright or Selenium for JS-rendered pages

4. **Move `scraped_events.json` to Fixtures**
   - The `data/scraped_events.json` committed in Week 7 should be treated as a development fixture, not live data
   - Add a `# FIXTURE: snapshot from April 2026 scraper run — not authoritative` comment at the top of the JSON
   - Update the seed script to accept `--fixture` flag for offline dev testing

---

### Subodh Krishna Nikumbh — End-to-End Integration Tests & KB Connection
**Close the integration testing gap and connect events to the knowledge base.**

Deliverables:

1. **Integration Test: Full Pipeline**
   - Add `4B/week8/tests/test_event_pipeline_integration.py`
   - Test the complete flow: mock scraper output → `upsert_events()` → `EventService.get_upcoming_events()` → API endpoint response
   - Minimum test cases:
     - Single event upsert → API returns it in the list
     - Duplicate event upsert (same dedup key) → only one record in DB
     - Search for event by name → correct event returned
     - Today's events query → only events on today's date returned
     - Recurring events query → only `is_recurring=True` events returned
     - Sponsorship tier data → renders correctly in API response
   - Use `pytest` with a `setup_module` fixture that creates a fresh SQLite in-memory database for each test run (no Render required)

2. **`EventQueryCache` — Add Max Size with LRU Eviction**
   - Current cache in `events/services/event_query_cache.py` has no maximum size limit
   - Add `max_size: int = 500` parameter to `EventQueryCache.__init__`
   - When the cache exceeds `max_size`, evict the least recently used entry
   - Use an `OrderedDict` for O(1) LRU eviction (no external libraries required)
   - Update `get_shared_event_query_cache()` to accept `max_size` parameter
   - Add a test for LRU eviction behavior to the cache test suite

3. **Connect Events to Knowledge Base Ingestion**
   - The `knowledge_base/ingestion.py` carries over from prior weeks and does not include events
   - Add an `ingest_events()` function that:
     - Reads all upcoming events from the database via `EventService.get_upcoming_events()`
     - Formats each event as a KB document: `{ "type": "event", "title": name, "content": description + schedule, "source_url": url }`
     - Calls the existing KB ingestion pipeline to index these documents
   - Wire `ingest_events()` to run after each scraper seed (at the end of `seed_from_scraped_json.py`)
   - This ensures the intent classifier and response builder in Team 4A's bot can find events via KB search, not just direct API calls

---

### Leena Hussein — Demo Infrastructure, Import Fix & Final Docs
**Fix the startup blocker, set up the demo environment, and complete the documentation.**

Deliverables:

1. **CRITICAL FIX — Stripe Webhook Import Error (do this first)**
   - File: `4B/week8/api/stripe_webhooks.py`
   - Change:
     ```python
     # WRONG (current)
     from integrations.stripe import StripeIntegration
     
     # CORRECT
     from ..integrations.stripe import StripeIntegration
     ```
   - After fixing, start the app locally: `uvicorn main:app --reload`
   - Confirm it starts without `ImportError`
   - Run `pytest tests/test_stripe_webhooks.py` — all tests must pass

2. **Fix: Stripe Webhook Router Path**
   - The current route is double-prefixed: `/stripe/webhook` prefix + `/stripe/webhook` route = `/stripe/webhook/stripe/webhook`
   - Verify the actual registered path by inspecting `main.py` router mounts and `api/stripe_webhooks.py` route decorators
   - Fix to a clean single path (confirm with the `STRIPE_WEBHOOK_SECRET` URL registered in the Stripe dashboard)
   - Document the correct webhook URL in `docs/render-deployment.md`

3. **Demo Script** — `4B/week8/docs/demo-script.md`
   - Step-by-step instructions to run the April 15 demo:
     1. How to start Team 4B's app locally (for backup demo if Render is down)
     2. How to trigger the scraper and reseed the database
     3. Which Render URL to use for each API call
     4. Sample `curl` commands for each of the 5 events endpoints
     5. What to do if an endpoint returns empty results
     6. What to do if the scraper fails
   - This document is for the instructors and both teams — write it assuming the reader has never seen the codebase

4. **Commit History Cleanup (future PRs)**
   - The Week 7 PR had 4 duplicate "Added Stripe webhook tests" commits
   - Starting this PR: squash duplicate commits before raising a PR
   - Add a brief note in `4B/week8/docs/git-workflow.md` explaining Team 4B's commit conventions:
     - Prefix format: `feat(scope):`, `fix(scope):`, `docs(scope):`, `test(scope):`
     - No duplicate messages in the same PR
     - One commit per logical change (not per file saved)

---

## Deadline

**Wednesday, April 15, 2026 at 11:59 PM CST**

Submit your weekly summary email to `students@mail.confersolutions.ai` AND push all deliverables to the repo under `4B/week8/`.

## Git Requirements
- Branch: `4B-week8-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
- Atomic commits with meaningful messages
- No committed run-output artifacts (`.coverage`, `stress_test_results_*`, `scraped_events.json`)

## Demo Target (April 15)
Be ready to demonstrate live:
1. Show `GET /api/v2/events/today` on the live Render URL returning real temple events
2. Show `GET /api/v2/events/search?q=Hanuman` returning the correct event
3. Show `GET /api/v2/events/recurring` returning all 5 recurring programs
4. Show the Stripe webhook endpoint accepting a test event from the Stripe dashboard
5. Show Team 4A's bot successfully calling your API and formatting a WhatsApp response
