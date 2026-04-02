User: I'm given tasks to perform.

Can you once check the repos, folders, files:

They might be migrated, so give me files such that they do not have import errors.

First give me the list of files required for cahnges, or files requried to be added. i need a perfect work to be done.

I'm Chakradhar.

Here are the tasks assigned:
Hi Group 4B,

Hope midterms went well! This week we're shifting into real-world data engineering — you're building the event data pipeline that makes the bot temple-aware.

WEEK 7 THEME: Event Data Pipeline — Web Scraping, Storage & API
DEADLINE: Wednesday, April 2, 2026 at 11:59 PM CST

THE CHALLENGE:
The Radha Krishna Temple of Dallas publishes events on their website, but there's no API or calendar feed. You need to:
1. SCRAPE real event data from live websites
2. STORE it in a structured database
3. SERVE it through API endpoints the bot can query

By Friday's demo, someone should be able to hit /events/today and get real temple events back.

DATA SOURCES TO SCRAPE:
• radhakrishnatemple.net — Homepage event carousel + individual event detail pages (schedules, parking info, sponsorship tiers, food, special notes)
• jkyog.org/upcoming_events — Organization-wide calendar (filter for Dallas/Allen, TX events at Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

Current events on the temple site: Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

WHAT MAKES THIS HARD:
• No API — pure HTML parsing
• Inconsistent page formatting across events
• Multi-day events with different daily sub-schedules
• Two websites with completely different HTML structures
• Must handle gracefully: site down, HTML changes, no upcoming events

────────────────────────────
INDIVIDUAL ASSIGNMENTS
────────────────────────────

SYSHA SHARMA (Team Lead) — Scraper Architecture & Orchestration
• Build event_scraper module: scrape radhakrishnatemple.net homepage → extract event carousel → follow each event link → scrape detail pages → scrape jkyog.org/upcoming_events for Dallas events
• Output: structured JSON matching Team 4A's event data model
• Configurable target URLs, scrape intervals, user-agent, request delays (be respectful to their servers)
• Error handling: site down, HTML structure changes, timeouts
• Orchestration: scrape_events script (scrape both sites → output JSON) + seed_database script (JSON → database)

ROHAN BHARGAV KOTHAPALLI — /events API Endpoints + Escalation Auth Fix
• Implement API endpoints:
  - GET /events — All upcoming events (pagination: ?limit=10&offset=0)
  - GET /events/today — Today's events + active recurring programs
  - GET /events/{id} — Single event detail
  - GET /events/search?q={query} — Case-insensitive search by name/description
  - GET /events/recurring — All recurring programs
  - Proper error responses: 404, 400, 200 with empty list
• TECH DEBT (Security Blocker): Add Bearer token auth to ALL /escalations endpoints (POST, GET, PUT). Reject unauthenticated with 401. This was flagged Week 6 — must be fixed.
• Integration: wire scraper → database → API. Demo /events/today with real data.

CHAKRADHAR REDDY GUMMAKONDA — Event Database Schema & Storage Layer
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

SUBODH KRISHNA NIKUMBH — Event Service Wrapper & Test Suite
• EventService: getUpcomingEvents(limit, offset), getTodayEvents(), searchEvents(query), getEventById(id), getRecurringSchedule()
• Caching layer: cache frequent queries, invalidate on re-scrape
• 20+ tests covering: scraper parsing (use real HTML fixtures from both sites), malformed HTML, service cache hit/miss, stale data, pagination, API endpoints, search relevance
• Integration test: scrape → store → query → verify end-to-end

LEENA HUSSEIN — Stripe Webhooks Completion + Event Pipeline Documentation
• TECH DEBT: Handle payment_intent.succeeded and payment_intent.payment_failed webhooks, Stripe-Signature verification, test coverage for both paths
• Event Pipeline Docs: Admin runbook (how to run scraper, trigger refresh, verify data), architecture diagram (website → scraper → DB → API → bot), troubleshooting guide (HTML changes, scrape failures, stale data), all new environment variables documented

────────────────────────────
FRIDAY DEMO TARGET (April 4)
────────────────────────────
Be ready to show:
1. Run the scraper → real JSON from temple websites
2. Query the database → stored events
3. GET /events/today → real events for that day
4. Search "Hanuman Jayanti" → correct result
5. /escalations with auth → 401 without token, 200 with token

────────────────────────────
SUBMISSION
────────────────────────────
• Email your weekly summary by Wednesday April 2, 11:59 PM CST
• Push all deliverables to 4B/week7/ in the repo
• Branch: 4B-week7-[your-name], PR into main by deadline
• Atomic commits with meaningful messages (no "update" or "fix")

Full assignment details are in the repo: 4B/week7/ASSIGNMENT.md

4B/week7/ASSIGNMENT.md:
# Week 7 Assignment — Group 4B
## Event Data Pipeline: Web Scraping, Storage & API
**Sprint: March 30 – April 2, 2026**

---

## 🎯 This Week's Mission

Build the **event data pipeline** that powers the JKYog WhatsApp Bot's event awareness. By the end of this week, you should have:
1. A **web scraper** that extracts real event data from temple websites
2. A **database** to store and query events
3. **API endpoints** to serve event data to the bot
4. **Tests** proving it all works

This is real-world data engineering — you're scraping live websites with unstructured HTML and turning it into clean, queryable data.

---

## Context: The Data Sources

### Source 1: radhakrishnatemple.net (Primary — Dallas Temple)
- **Homepage** — Event carousel with upcoming events (name, date range, time)
- **Individual event pages** — Full details: schedule, parking, sponsorship tiers, food, special notes
- **Daily schedule sidebar** — Darshan timings, aarti, bhog, Satsang, bhajans
- **Example current events:** Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

### Source 2: jkyog.org/upcoming_events (Secondary — Organization-wide)
- Lists JKYog events globally, some Dallas-specific
- Events have: title, date, time, venue, link to detail page
- Filter for Dallas/Allen, TX events (Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

### What Makes This Challenging
- No API — pure HTML scraping
- Event pages have inconsistent formatting (some have parking notes, some don't)
- Multi-day events (Ram Navami spans 4 days with different daily schedules)
- Two different websites with different HTML structures
- Events are published ~1-2 months in advance, so the scraper needs to handle "no upcoming events" gracefully

---

## Individual Assignments

### Sysha Sharma (Team Lead) — Scraper Architecture & Orchestration
**Design and build the scraper that extracts events from both websites.**

Deliverables:
1. **Event Scraper Module** (`event_scraper.py` or equivalent):
   - Scrape `radhakrishnatemple.net` homepage → extract event carousel (name, dates, times, links)
   - Follow each event link → scrape detail page (full schedule, parking, sponsorship, food info)
   - Scrape `jkyog.org/upcoming_events` → extract Dallas-area events
   - Output: structured JSON matching Team 4A's event data model

2. **Scraper Configuration:**
   - Configurable target URLs (don't hardcode)
   - Configurable scrape interval (for future cron scheduling)
   - User-agent string, request delays (be respectful to the servers)
   - Error handling: site down, HTML structure changed, timeout

3. **Orchestration Script:**
   - `scrape_events.py` — Run once, scrape both sites, output JSON
   - `seed_database.py` — Take scraped JSON, insert into database
   - README with setup instructions

---

### Rohan Bhargav Kothapalli — /events API Endpoints + Escalation Auth Fix
**Build the API that serves event data to the bot.**

Deliverables:
1. **Event API Endpoints:**
   - `GET /events` — All upcoming events (sorted by date, with pagination: `?limit=10&offset=0`)
   - `GET /events/today` — Today's events + currently active recurring programs
   - `GET /events/{id}` — Single event with full details
   - `GET /events/search?q={query}` — Search events by name/description (case-insensitive)
   - `GET /events/recurring` — All recurring programs (darshan, aarti, Satsang, etc.)
   - Proper error responses: 404 (event not found), 400 (bad query), 200 (empty list for no results)

2. **TECH DEBT FIX — Escalation API Auth (SECURITY BLOCKER):**
   - Add Bearer token validation to ALL `/escalations` endpoints (POST, GET, PUT)
   - Reject unauthenticated requests with 401
   - This was flagged in Week 6 — must be resolved this week

3. **Integration:** Wire the scraper output → database → API. Demo: hit `/events/today` and get real temple events.

---

### Chakradhar Reddy Gummakonda — Event Database Schema & Storage Layer
**Design and implement the persistence layer for event data.**

Deliverables:
1. **Database Schema:**
   ```sql
   events table:
   - id (primary key, auto-increment)
   - name (text, not null)
   - description (text)
   - start_datetime (timestamp, not null)
   - end_datetime (timestamp)
   - location (text)
   - venue_details (text)
   - parking_notes (text)
   - food_info (text)
   - sponsorship_data (jsonb — tiers with names, amounts, links)
   - image_url (text)
   - source_url (text, not null — where this was scraped from)
   - source_site (enum: 'radhakrishnatemple', 'jkyog')
   - is_recurring (boolean, default false)
   - recurrence_pattern (text — e.g., "daily", "weekly:sunday", "weekdays")
   - category (text — e.g., "festival", "program", "health", "cultural")
   - special_notes (text)
   - scraped_at (timestamp — when this data was last refreshed)
   - created_at (timestamp)
   - updated_at (timestamp)
   ```

2. **Indexes:** On start_datetime, name, category, is_recurring (for fast queries)

3. **Seed Script:** Populate database with REAL scraped data from both websites

4. **Data Integrity:**
   - Upsert logic (don't duplicate events on re-scrape)
   - Deduplication between the two sources (same event on both sites)
   - "Stale data" flag if scraped_at > 30 days ago

---

### Subodh Krishna Nikumbh — Event Service Wrapper & Test Suite
**Build the service layer and comprehensive tests.**

Deliverables:
1. **EventService Wrapper:**
   - `getUpcomingEvents(limit, offset)` — Paginated upcoming events
   - `getTodayEvents()` — Today's events + active recurring programs based on current time
   - `searchEvents(query)` — Full-text search
   - `getEventById(id)` — Single event lookup
   - `getRecurringSchedule()` — All recurring programs
   - Caching layer (in-memory or Redis): cache frequent queries, invalidate on re-scrape

2. **Test Suite (target: 20+ tests):**
   - **Scraper tests:** Parse real HTML fixtures from both websites, handle malformed HTML, handle missing fields
   - **Service tests:** Cache hit/miss, stale data handling, empty results, pagination edge cases
   - **API tests:** All endpoints return correct status codes, search returns relevant results
   - **Integration test:** Scrape → Store → Query → Verify

---

### Leena Hussein — Stripe Webhooks Completion + Event Operations Documentation
**Complete the payment flow AND document the new event pipeline.**

Deliverables:
1. **TECH DEBT FIX — Stripe Webhooks:**
   - Handle `payment_intent.succeeded` webhook → update donation record
   - Handle `payment_intent.payment_failed` webhook → log failure, notify admin
   - Webhook signature verification (Stripe-Signature header)
   - Test coverage for both success and failure paths

2. **Event Pipeline Documentation:**
   - **Admin Runbook:** How to run the scraper manually, how to trigger a refresh, how to verify data is current
   - **Architecture Diagram:** Data flow from website → scraper → database → API → bot
   - **Troubleshooting Guide:** What happens when the website structure changes? When a scrape fails? When events are stale?
   - **Environment Variables:** Document all new env vars (scraper URLs, scrape interval, DB connection, cache TTL)

---

## Deadline

**Wednesday, April 2, 2026 at 11:59 PM 
## Git Requirements
- Branch: `4B-week7-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
- Atomic commits with meaningful messages (no "update" or "fix")

Be ready to demonstrate:
1. Run the scraper → show extracted JSON with real temple events
2. Query the database → show stored events
3. Hit `/events/today` → return real events happening that day
4. Search for "Hanuman Jayanti" → return correct result

GitHub Copilot: You want a migration-safe, import-error-free plan before making changes, focused on your Week 7 ownership. I’ll first scan the existing Week 7 and adjacent backend code to identify what already exists, what is missing, and then produce a precise file-by-file add/change list for you.

[Internal local file-read trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

I confirmed there is no committed Week 7 folder yet, so I’m now mapping the existing backend code layout (especially Week 6) to anchor the correct Week 7 file locations and imports before proposing the exact file list.

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal code-search trace removed]

I found the active backend in Week 6, so I’m now reading the core DB and app files to produce a migration-safe change list with exact paths and dependency touchpoints.

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

Next I’ll verify dependency support and existing import conventions so the Week 7 file list avoids broken imports after migration.

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal code-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

I checked the repo structure and current runnable backend. Right now, there is no Week 7 code folder yet, and the active app is Week 6.

Confirmed existing anchors:
1. main.py
2. schema.py
3. models.py
4. state_tracking.py
5. env.py
6. requirements.txt

Also confirmed missing folder:
1. 4B/week7 does not exist yet in this workspace snapshot.

For your role (Chakradhar: DB schema + storage layer), this is the exact file list I recommend so imports stay clean after migration.

Required new files to add
1. 4B/week7/__init__.py
2. 4B/week7/README.md
3. 4B/week7/requirements.txt
4. 4B/week7/alembic.ini
5. 4B/week7/database/__init__.py
6. 4B/week7/database/models.py
7. 4B/week7/database/schema.py
8. 4B/week7/database/event_storage.py
9. 4B/week7/migrations/env.py
10. 4B/week7/migrations/script.py.mako
11. 4B/week7/migrations/versions/001_initial_schema_users_conversations_messages_session_state.py
12. 4B/week7/migrations/versions/002_add_escalations_table.py
13. 4B/week7/migrations/versions/003_add_events_table.py
14. 4B/week7/scripts/seed_database.py
15. 4B/week7/scripts/seed_from_scraped_json.py
16. 4B/week7/data/.gitkeep
17. 4B/week7/tests/test_event_storage.py

Existing files required for changes
1. requirements.txt only if you want Week 6 runtime to also execute Week 7 seeding scripts; otherwise skip.
2. README.md optional note pointing to Week 7 event pipeline location.

Import-error-safe rules for these files
1. Use package-relative imports inside Week 7 modules, like from .models import Base and from ..database.schema import Event.
2. Keep scripts import-safe by running with module mode from repo root, for example python -m 4B.week7.scripts.seed_from_scraped_json.
3. Keep Alembic script location inside Week 7, and include revisions 001 and 002 in Week 7 so revision chain for 003 is valid.
4. Do not import from 4B.week6 inside Week 7 files.

If you want, next I can create this full Week 7 scaffold now and wire only your DB/storage pieces first, with zero unresolved imports before we touch scraper/API integration.

User: which branch is this?

GitHub Copilot: I’ll check the active git branch in this workspace now and report it directly.

[Internal terminal-command trace removed]

[Internal branch detail removed]

User: which files require changes? i will create new week folder and add it, that should not be a problem

GitHub Copilot: For your scope (Chakradhar, Week 7 DB/storage), you can keep Week 6 untouched and do all required work inside your new Week 7 folder.

Mandatory existing files to modify right now
1. None

Files you should use as source templates (copy into your new week folder, then edit there)
1. models.py
2. schema.py
3. state_tracking.py
4. env.py
5. 001_initial_schema_users_conversations_messages_session_state.py
6. 002_add_escalations_table.py
7. alembic.ini
8. requirements.txt

Inside your new week folder, these are the files that must be changed/added
1. database schema module: add the events table model and indexes
2. new alembic migration: add events table + indexes
3. storage/service module: upsert, dedup, stale flag logic
4. seed script: ingest real scraped JSON into DB
5. migration env/config: ensure imports resolve to your new week package
6. requirements: ensure required packages are present
7. tests for storage/upsert/dedup behavior

Optional (only if your team wants Week 6 app to immediately expose events from your DB work)
1. main.py
2. api folder (new events router wiring)

If you want, I can now generate the exact Week 7 file tree and a “copy-from week6 + edit” checklist mapped file-by-file so you can implement without import errors on first run.

User: im not quite getting it, why will env.py, 002_add_escalations_table.py, all these files change?

GitHub Copilot: Great question. Short answer: they do not need to change in Week 6.

Why I mentioned them:
1. If you create a new independent Week 7 migration stack, Alembic needs a valid revision chain in that new folder.
2. In Week 6, 4B/week6/migrations/versions/003_add_events_table.py does not exist yet.
3. Your new Week 7 folder will start empty, so to make it runnable by itself, you usually copy these as baseline:
   1. env.py
   2. 001_initial_schema_users_conversations_messages_session_state.py
   3. 002_add_escalations_table.py

What actually changes for your work:
1. New Week 7 files only.
2. New migration file for events table only.
3. Event model and storage/upsert layer only.

What does not change:
1. env.py stays untouched.
2. 002_add_escalations_table.py stays untouched.

So your understanding is correct: you are not editing old escalation files; at most you copy them into Week 7 so your new migration history is complete and import-safe.

User: that's why i said, i will copy or move week6 files to week7. give me list of files which needs changes or new files to be added

GitHub Copilot: Perfect, then do this workflow:

1. Copy whole week6 to new folder `4B/week7`.
2. Make changes only inside `4B/week7`.
3. Do not touch Week 6 files.

Files to change in your copied Week 7
1. `4B/week7/database/schema.py`
2. `4B/week7/database/state_tracking.py` (only if you keep event DB functions here)
3. `4B/week7/database/models.py` (only if you add event health probe/init behavior)
4. `4B/week7/migrations/env.py` (only folder-name/path adjustments if needed)
5. `4B/week7/requirements.txt` (only if adding new libs)
6. `4B/week7/README.md` (Week 7 setup + seed instructions)

New files to add in Week 7
1. `4B/week7/migrations/versions/003_add_events_table.py`
2. `4B/week7/database/event_storage.py` (recommended: keep event logic separate from state_tracking.py)
3. `4B/week7/scripts/seed_database.py`
4. `4B/week7/scripts/seed_from_scraped_json.py`
5. `4B/week7/tests/test_event_storage.py`
6. `4B/week7/data/.gitkeep`

Optional new files (if you want cleaner structure)
1. `4B/week7/database/events_queries.py`
2. `4B/week7/docs/week7-events-db.md`

No-change files (leave as copied unless needed)
1. `4B/week7/migrations/versions/001_initial_schema_users_conversations_messages_session_state.py`
2. `4B/week7/migrations/versions/002_add_escalations_table.py`
3. `4B/week7/api/escalations.py`
4. `4B/week7/main.py` (for your assignment, usually no edit needed)

If you want, I can now give you the exact column definitions and index statements for `003_add_events_table.py` plus the exact function signatures for `event_storage.py` so you can implement directly without guesswork.

User: 1. Keep event logic out of state_tracking.py

This is the biggest design choice.

Your current repo already uses:

database/schema.py for models
database/models.py for engine/session/init/health
database/state_tracking.py for user/session/message/escalation behavior

So for Week 7, putting event persistence into state_tracking.py would mix unrelated responsibilities:

sessions
chat state
escalations
event storage

That is not good for a sponsor-facing codebase.

So the best design is:

schema.py → Event model
event_storage.py → event DB operations
state_tracking.py → leave mostly untouched unless someone already depends on it

That is cleaner, easier to test, and reduces merge conflict risk.

2. models.py should be treated as a required touchpoint

Earlier I said optional, but after checking the repo, I’d upgrade this to must review / likely modify.

Why:

models.py contains init_db()
models.py contains DB health logic
Week 6 health logic currently probes escalations
Week 7 may need event-table reachability or at least safe migration/init behavior

Even if the code change is small, models.py is part of your storage layer responsibility.

So I would include it in your planned changes.

3. migrations/env.py should stay aligned with Week 7 package path

The existing Week 6 Alembic env is tied to week6_dir logic and imports under the week6 package layout.

If you copy Week 6 into Week 7, this file must be checked carefully so it resolves:

week7 path
schema registration
metadata loading
migration autogeneration correctly

So yes, this stays on the list.

4. Two seed scripts are not automatically better

For a stronger codebase, I would not start with both:

seed_database.py
seed_from_scraped_json.py

That can become redundant unless there is a clear split.

Best initial structure:

create one real ingestion script first:
scripts/seed_from_scraped_json.py

Then add seed_database.py only if:

Sysha’s orchestration expects that exact entry point, or
the team wants a wrapper command around different seed sources

For now, one focused seeding script is cleaner.

5. requirements.txt should not be changed unless truly needed

Since your task is storage/schema/upsert/dedup, you may not need any new dependency at all.

Changing requirements.txt unnecessarily in a team repo can create friction, especially in sponsor projects.

So:

keep it optional
only edit if a new package is genuinely needed

What about these?

GitHub Copilot: Your reasoning is strong and I agree with all 5 points, with one refinement.

1. Keep event logic out of state_tracking.py  
Yes. Put Event ORM in the copied Week 7 schema file and event persistence/query logic in a dedicated `event_storage.py` module. This is the cleanest separation of concerns.

2. Treat models.py as required review  
Yes. Even if edits are small, this is part of storage lifecycle (`init_db`, health behavior, migration execution), so it is a real touchpoint for Week 7.

3. Keep env.py aligned after copy  
Yes. Must verify import path resolution and metadata registration after moving to Week 7 folder structure.

4. Start with one seed script  
Yes. Start with one focused script (`seed_from_scraped_json.py`) first. Add wrapper `seed_database.py` only if team orchestration explicitly needs it.

5. Only change requirements.txt equivalent if needed  
Yes. Do not edit dependencies unless a new package is genuinely required.

Refined Week 7 change plan after your feedback:
1. Required edits in copied Week 7: `database/schema.py`, `database/models.py`, `migrations/env.py`, README.md
2. Required new files in Week 7: migration `003_add_events_table.py`, `database/event_storage.py`, `scripts/seed_from_scraped_json.py`, tests for event storage/upsert/dedup
3. Leave copied state_tracking.py unchanged unless another teammate has hard dependency on it
4. Keep copied `001` and `002` migrations unchanged

This is exactly the sponsor-safe structure I would recommend.

User: Do you recommend these changes? I need to build a 'complete', perfect codes, because this is not just academic project, but a sponsored project given to us

GitHub Copilot: Yes. I recommend your proposed structure, and it is the right direction for a sponsored project.

For “complete/perfect” delivery, keep your design and add these production-grade requirements before you call it done:

1. Strong module boundaries
1. Event model in schema layer only.
2. Event persistence in a dedicated storage module only.
3. Session/chat/escalation logic stays separate.

2. Migration safety
1. Keep migration history linear and valid.
2. New events migration must be reversible.
3. Verify migrate up and migrate down on a clean database.

3. Data integrity guarantees
1. Enforce uniqueness strategy for dedup across sources.
2. Implement idempotent upsert so reruns do not duplicate records.
3. Add stale-data flag logic based on scrape timestamp age.
4. Validate required fields and normalize datetime/timezone handling.

4. Operational reliability
1. Seeding script must be idempotent and fail with actionable error messages.
2. Include dry-run mode and summary output: inserted, updated, skipped, stale.
3. Add logging around parsing, dedup decisions, and DB writes.

5. Testing expectations (non-negotiable for sponsored work)
1. Unit tests for upsert, dedup, stale detection, and edge cases.
2. Migration tests (table/index existence + downgrade safety).
3. Integration test path: ingest real-like scraped JSON, store, query, verify.

6. Minimal change principle
1. Avoid dependency changes unless truly needed.
2. Avoid touching unrelated modules.
3. Keep one focused seeding entrypoint first.

If you execute the above exactly, your architecture will be clean, review-friendly, and production-defensible.  
If you want, I can give you a strict Definition of Done checklist you can use before raising your PR.

User: user_list	my_choice	action
4B/week7/database/schema.py	Required (Event model lives here)	MODIFY
4B/week7/database/state_tracking.py	Keep clean; no event logic	DO NOT TOUCH
4B/week7/database/models.py	Review + small update if needed	MODIFY
4B/week7/migrations/env.py	Required update for Week 7 paths	MODIFY
4B/week7/requirements.txt	Keep unless adding deps	DO NOT TOUCH
4B/week7/README.md	Add migrate/seed/test runbook	MODIFY
4B/week7/migrations/versions/003_add_events_table.py	Yes	ADD
4B/week7/database/event_storage.py	Yes	ADD
4B/week7/scripts/seed_database.py	Yes (single runnable)	ADD
4B/week7/scripts/seed_from_scraped_json.py	Yes (helper only)	ADD
4B/week7/tests/test_event_storage.py	Yes	ADD
4B/week7/data/.gitkeep	Yes	ADD
(not in user list) 4B/week7/scripts/__init__.py	Needed for import safety	ADD

Do you recommend this?

GitHub Copilot: Yes, I recommend this plan. It is strong and production-appropriate.

Only two refinements:

1. Keep 4B/week7/scripts/seed_database.py as the primary entrypoint and make 4B/week7/scripts/seed_from_scraped_json.py a thin reusable helper.
2. Add 4B/week7/tests/test_migrations_events.py to validate upgrade/downgrade and index creation for the new events migration.

Everything else in your list is exactly right, including:
1. Modify 4B/week7/database/schema.py, 4B/week7/database/models.py, 4B/week7/migrations/env.py, 4B/week7/README.md
2. Add 4B/week7/migrations/versions/003_add_events_table.py, 4B/week7/database/event_storage.py, 4B/week7/scripts/seed_database.py, 4B/week7/scripts/seed_from_scraped_json.py, 4B/week7/tests/test_event_storage.py, 4B/week7/data/.gitkeep, 4B/week7/scripts/__init__.py
3. Do not touch 4B/week7/database/state_tracking.py and 4B/week7/requirements.txt unless strictly required

If you want, I can now generate the exact Event model fields and migration DDL layout so you can implement with minimal rework.

User: can you give me set of codes so that i can copy and paste. give me required set of files with codes. make sure evrything is covered, mainly my focus of area

GitHub Copilot: Yes. Below is a copy-paste ready set for your focus area.

Use this exactly with your Week 6 copied into Week 7.

1. Replace 4B/week7/database/models.py with:

~~~python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres:// URLs to postgresql:// for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    """Read a float environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    """Run a database operation with exponential backoff retries."""
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    """Run a lightweight query used by the DB health endpoint."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    """Verify the escalations table is queryable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    """Verify the events table is queryable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    """Check whether the application can connect to the database
    and whether critical tables are reachable."""
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    """Run Alembic migrations to bring the database schema up to date."""
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
~~~

2. Replace 4B/week7/migrations/env.py with:

~~~python
"""
Alembic migration environment for Week 7.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

# Add the week7 directory to sys.path so "database" package resolves when
# running Alembic from 4B/week7.
config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

# Prefer already-loaded module from a running app to avoid duplicate engine creation.
_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

# Set sqlalchemy.url from DATABASE_URL so alembic.ini does not hardcode credentials.
db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in online mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
~~~

3. In 4B/week7/database/schema.py, keep existing content and append this Event model block at the end. Also ensure imports include Enum and Integer.

Add/adjust imports at top:
~~~python
import enum
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
~~~

Append this block at end:
~~~python
class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        Index("ix_events_start_datetime", "start_datetime"),
        Index("ix_events_name", "name"),
        Index("ix_events_category", "category"),
        Index("ix_events_is_recurring", "is_recurring"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        Enum(EventSourceSite, name="event_source_site"),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    # Internal dedup key for cross-source matching.
    dedup_key = Column(String(255), nullable=False)
~~~

4. Add [4B/week7/migrations/versions/003_add_events_table.py]:

~~~python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint(
            "source_site",
            "source_url",
            name="uq_events_source_site_source_url",
        ),
        sa.UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
    )

    op.create_index("ix_events_start_datetime", "events", ["start_datetime"])
    op.create_index("ix_events_name", "events", ["name"])
    op.create_index("ix_events_category", "events", ["category"])
    op.create_index("ix_events_is_recurring", "events", ["is_recurring"])

def downgrade() -> None:
    op.drop_index("ix_events_is_recurring", table_name="events")
    op.drop_index("ix_events_category", table_name="events")
    op.drop_index("ix_events_name", table_name="events")
    op.drop_index("ix_events_start_datetime", table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
~~~

5. Add [4B/week7/database/event_storage.py]:

~~~python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        # Persist as naive UTC for consistency with existing codebase.
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("Event name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be a JSON object/dict")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = (
        db.query(Event)
        .filter(Event.dedup_key == values["dedup_key"])
        .first()
    )

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(
            created_at=_now(),
            updated_at=_now(),
            **values,
        )
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}
    for payload in payloads:
        try:
            _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1
    db.commit()
    return stats

def is_stale(scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = (
        db.query(Event)
        .filter(Event.scraped_at < cutoff)
        .all()
    )

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
~~~

6. Add [4B/week7/scripts/__init__.py]:

~~~python
"""Week 7 scripts package."""
~~~

7. Add [4B/week7/scripts/seed_from_scraped_json.py]:

~~~python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ..database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be either a list or an object with an 'events' key")

    if not isinstance(events, list):
        raise ValueError("'events' must be a list")

    return [e for e in events if isinstance(e, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    path = Path(input_path).resolve()
    events = _load_input(path)

    stats = upsert_events(db, events)
    stale_flagged = flag_stale_events(db, stale_after_days=30)
    stats["stale_flagged"] = stale_flagged
    stats["input_count"] = len(events)
    return stats
~~~

8. Add [4B/week7/scripts/seed_database.py]:

~~~python
from __future__ import annotations

import argparse
from pathlib import Path

from ..database.models import SessionLocal, init_db
from .seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON (list or {events:[...]})",
    )
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
~~~

9. Add [4B/week7/tests/test_event_storage.py]:

~~~python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import (
    build_dedup_key,
    is_stale,
    normalize_event_payload,
)
from database.schema import EventSourceSite

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"] == EventSourceSite.JKYOG
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
~~~

10. Add [4B/week7/migrations/versions/.gitkeep] only if folder is empty before adding 003.
If you already have 001 and 002 copied in, you do not need this.

11. Add [4B/week7/data/.gitkeep]:

~~~text
~~~

12. Update 4B/week7/README.md by appending this runbook section:

~~~md
## Week 7 Event Storage Runbook

### 1) Run migrations
python -m alembic -c 4B/week7/alembic.ini upgrade head

### 2) Seed database from scraped JSON
python -m 4B.week7.scripts.seed_database --input 4B/week7/data/scraped_events.json

### 3) Run tests
pytest 4B/week7/tests/test_event_storage.py
~~~

Important
1. Keep 4B/week7/database/state_tracking.py unchanged.
2. Keep 4B/week7/requirements.txt unchanged unless you truly add a new package.
3. Ensure 4B/week7/migrations/versions/001_initial_schema_users_conversations_messages_session_state.py and 4B/week7/migrations/versions/002_add_escalations_table.py are present (copied from Week 6).

If you want, next I can give you a small sample scraped_events.json payload tailored to these functions so you can test seed end-to-end immediately.

User: Mostly yes, but **not 100% as-is**.

I checked the real `4B/week6` repo structure, and your overall direction is strong:

* keep `state_tracking.py` unchanged
* add `Event` in `schema.py`
* add a separate `event_storage.py`
* add `003_add_events_table.py`
* keep `seed_database.py` as the main entrypoint
* keep `seed_from_scraped_json.py` as the helper

That part is right.

The places that still need correction are these.

## What is correct

These files and roles fit the repo well:

* `4B/week7/database/models.py`
* `4B/week7/migrations/env.py`
* `4B/week7/database/schema.py` with appended `Event` model
* `4B/week7/migrations/versions/003_add_events_table.py`
* `4B/week7/database/event_storage.py`
* `4B/week7/scripts/__init__.py`
* `4B/week7/scripts/seed_from_scraped_json.py`
* `4B/week7/scripts/seed_database.py`
* `4B/week7/data/.gitkeep`

And yes, these two decisions are the right ones:

* keep `seed_database.py` as the runnable entrypoint
* keep `seed_from_scraped_json.py` as the thin reusable helper

## What is **not** fully correct yet

### 1. `test_event_storage.py` will likely have import problems

As written, it imports:

```python
from database.event_storage import ...
from database.schema import ...
```

That is risky in this repo.

Why:

* Week 6 tests import top-level modules because they are usually run from inside the week folder context.
* Your README command runs pytest from repo root:
  `pytest 4B/week7/tests/test_event_storage.py`
* from repo root, `database` may not be on `sys.path`
* also, importing `database.event_storage` imports `schema.py`, which imports `models.py`, which creates the SQLAlchemy engine immediately and requires `DATABASE_URL`

So these tests are **not safely runnable as written**.

### 2. `upsert_events()` in `event_storage.py` has a real bug

This is the most important code issue.

Right now:

```python
for payload in payloads:
    try:
        _, action = upsert_event(db, payload)
        stats[action] += 1
    except Exception:
        stats["failed"] += 1
db.commit()
```

If one payload causes `flush()` or a DB constraint failure, the SQLAlchemy session can enter a failed transaction state.
After that, later inserts/updates may also fail unless you do a rollback.

So this needs to become:

```python
for payload in payloads:
    try:
        _, action = upsert_event(db, payload)
        stats[action] += 1
    except Exception:
        db.rollback()
        stats["failed"] += 1
db.commit()
```

Without that, one bad record can poison the whole seed run.

### 3. README migration command should be corrected

This line is not the safest command:

```md
python -m alembic -c 4B/week7/alembic.ini upgrade head
```

Use:

```md
alembic -c 4B/week7/alembic.ini upgrade head
```

That is the normal Alembic CLI invocation.

### 4. Your schema import note is incomplete

When updating `schema.py`, do **not** replace the imports blindly with only the Event-related ones.

You must preserve existing imports already used by Week 6 models, especially:

* `uuid`
* `datetime, timezone`
* `relationship`
* `Base`

So your schema update is correct **only if** you append the missing `Enum` and `Integer` imports, without breaking the current imports.

### 5. You still need `test_migrations_events.py`

Yes, you should add it.

That refinement is good, and I recommend it.

## One more file I recommend adding

For a no-import-error setup, I would add:

* `4B/week7/tests/conftest.py`

Because your test imports will otherwise be fragile.

That file should:

* insert `4B/week7` into `sys.path`
* set a dummy `DATABASE_URL` for unit-test imports if one is not already present

Without that, your test file is much more likely to fail before even running assertions.

## Final verdict

### I recommend keeping

* `models.py`
* `env.py`
* `schema.py` Event addition
* `003_add_events_table.py`
* `event_storage.py`
* `scripts/__init__.py`
* `seed_from_scraped_json.py`
* `seed_database.py`
* `data/.gitkeep`

### I recommend adding

* `tests/test_migrations_events.py`
* `tests/conftest.py`

### I recommend correcting

* `event_storage.py` rollback handling in `upsert_events()`
* README migration command
* test import/runtime setup

## Bottom line

**Architecture: yes.
Code set exactly as pasted: no, not fully.**

It is close, but for sponsor-grade work I would **not** call it ready until you fix:

* session rollback in `upsert_events()`
* test import setup
* README Alembic command

If you want, I’ll give you the **corrected final version** of:

* `event_storage.py`
* `test_event_storage.py`
* `test_migrations_events.py`
* `tests/conftest.py`
* README runbook block

so you can paste them directly.

is this true?

GitHub Copilot: Yes, that review is accurate.

The three highest-impact fixes are exactly right:
1. Add rollback inside the batch upsert loop after per-record failures, or one bad row can poison the transaction.
2. Stabilize test import/runtime setup with a test bootstrap so tests run reliably from repo root.
3. Use the standard Alembic CLI command in docs.

And the additional recommendations are also correct for sponsor-grade quality:
1. Add migration-focused test coverage.
2. Preserve existing schema imports while extending them, instead of replacing import blocks.
3. Keep your architecture split (event model + separate storage module + untouched session tracking module).

So your conclusion is correct: architecture is strong, but the pasted version needed those final hardening fixes before calling it production-ready.

User: can you change the code and give me the changed codes or files.

also, let me kmow which codes need to be as is

GitHub Copilot: I will quickly inspect whether your Week 7 folder already exists so I can give you exact changed-vs-keep-as-is files with copy-paste-ready code blocks.

[Internal local file-read trace removed]

[Internal file-search trace removed]

I found Week 7 is not created yet, so I’ll give you a precise create/replace set based on Week 6 plus a clear keep-as-is list. I’m pulling the Week 6 source now so the code matches your repo conventions exactly.

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

Yes. I cannot edit files directly in this read-only mode, but here is the exact corrected copy-paste set.

Use flow:
1. Copy week6 to new folder 4B/week7.
2. Apply the file changes below in 4B/week7.
3. Keep the listed files as-is.

**Keep As-Is**
1. Copy and keep unchanged from state_tracking.py
2. Copy and keep unchanged from requirements.txt
3. Copy and keep unchanged from 001_initial_schema_users_conversations_messages_session_state.py
4. Copy and keep unchanged from 002_add_escalations_table.py
5. Copy and keep unchanged from alembic.ini

**Modify These In Week7**
1. 4B/week7/database/schema.py
2. 4B/week7/database/models.py
3. 4B/week7/migrations/env.py
4. 4B/week7/README.md

**Add These In Week7**
1. 4B/week7/database/event_storage.py
2. 4B/week7/migrations/versions/003_add_events_table.py
3. 4B/week7/scripts/__init__.py
4. 4B/week7/scripts/seed_from_scraped_json.py
5. 4B/week7/scripts/seed_database.py
6. 4B/week7/tests/conftest.py
7. 4B/week7/tests/test_event_storage.py
8. 4B/week7/tests/test_migrations_events.py
9. 4B/week7/data/.gitkeep

**1) 4B/week7/database/schema.py**
Keep existing content and only do these two changes.

A. Extend sqlalchemy import line to include Enum and Integer.

~~~python
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
~~~

B. Append this at the end of file.

~~~python
import enum

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "source_site IN ('radhakrishnatemple', 'jkyog')",
            name="valid_event_source_site",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        Enum(EventSourceSite, name="event_source_site"),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(255), unique=True, nullable=False, index=True)
~~~

**2) 4B/week7/database/models.py**
Replace with this (same as week6 plus week7 init path and events health probe).

~~~python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
~~~

**3) 4B/week7/migrations/env.py**
Replace with this (week7-aware path/module names).

~~~python
"""
Alembic migration environment for Week 7.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
~~~

**4) 4B/week7/database/event_storage.py**
Use this corrected version, including rollback fix in batch upsert.

~~~python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be an object")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(created_at=_now(), updated_at=_now(), **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            db.rollback()
            stats["failed"] += 1

    db.commit()
    return stats

def is_stale(
    scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = db.query(Event).filter(Event.scraped_at < cutoff).all()

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
~~~

**5) 4B/week7/migrations/versions/003_add_events_table.py**
Add this new migration.

~~~python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.CheckConstraint(
            "source_site IN ('radhakrishnatemple', 'jkyog')",
            name=op.f("ck_events_valid_event_source_site"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"], unique=True)
    op.create_index(
        op.f("ix_events_source_site_source_url"),
        "events",
        ["source_site", "source_url"],
        unique=True,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_events_source_site_source_url"), table_name="events")
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
~~~

**6) 4B/week7/scripts/__init__.py**

~~~python
"""Week 7 scripts package."""
~~~

**7) 4B/week7/scripts/seed_from_scraped_json.py**

~~~python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ..database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())

    stats = upsert_events(db, events)
    stats["stale_flagged"] = flag_stale_events(db, stale_after_days=30)
    stats["input_count"] = len(events)
    return stats
~~~

**8) 4B/week7/scripts/seed_database.py**

~~~python
from __future__ import annotations

import argparse
from pathlib import Path

from ..database.models import SessionLocal, init_db
from .seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
~~~

**9) 4B/week7/tests/conftest.py**
This removes import fragility when running pytest from repo root.

~~~python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    # Engine is created at import time in database.models.
    # Use a harmless placeholder URL when env is missing.
    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
~~~

**10) 4B/week7/tests/test_event_storage.py**

~~~python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_stale, normalize_event_payload

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"].value == "jkyog"
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
~~~

**11) 4B/week7/tests/test_migrations_events.py**
Lightweight migration file checks that run without DB connection.

~~~python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
~~~

**12) 4B/week7/README.md**
Append this runbook block and use Alembic CLI command as below.

~~~md
## Week 7 Event Storage Runbook

1. Run migrations
alembic -c 4B/week7/alembic.ini upgrade head

2. Seed events from scraped JSON
python -m 4B.week7.scripts.seed_database --input 4B/week7/data/scraped_events.json

3. Run tests
pytest 4B/week7/tests/test_event_storage.py 4B/week7/tests/test_migrations_events.py
~~~

**13) 4B/week7/data/.gitkeep**
Create empty file.

If you want, next I can give one valid sample for 4B/week7/data/scraped_events.json that exercises dedup, update, and stale-flag behavior in one run.

User: can you give me all the files now, in correct order

GitHub Copilot: Yes. Use this exact order so you avoid import/migration issues.

1. Copy baseline folder  
week6 -> new folder `4B/week7`

2. Keep these copied files as-is (no edits)
state_tracking.py  
requirements.txt  
001_initial_schema_users_conversations_messages_session_state.py  
002_add_escalations_table.py  
alembic.ini

3. Modify first (core DB wiring)
- 4B/week7/database/schema.py
- 4B/week7/database/models.py
- 4B/week7/migrations/env.py

4. Add new DB/storage files
- 4B/week7/database/event_storage.py
- 4B/week7/migrations/versions/003_add_events_table.py

5. Add scripts (entrypoint + helper)
- 4B/week7/scripts/__init__.py
- 4B/week7/scripts/seed_from_scraped_json.py
- 4B/week7/scripts/seed_database.py

6. Add tests (import-safe first)
- 4B/week7/tests/conftest.py
- 4B/week7/tests/test_event_storage.py
- 4B/week7/tests/test_migrations_events.py

7. Add data placeholder
- 4B/week7/data/.gitkeep

8. Update docs last
- 4B/week7/README.md

If you want, next I can give the same list as a checklist with `CREATE`/`MODIFY`/`KEEP` tags per file for quick tracking while you paste.

User: all the files and their complete code

GitHub Copilot: Use the following as the complete, corrected Week 7 file set.

Order is important:
1. Copy week6 to a new folder named 4B/week7
2. Keep the as-is files listed below unchanged
3. Replace or add files in the exact order below

As-is files (do not change)
1. 4B/week7/database/state_tracking.py
2. 4B/week7/requirements.txt
3. 4B/week7/migrations/versions/001_initial_schema_users_conversations_messages_session_state.py
4. 4B/week7/migrations/versions/002_add_escalations_table.py
5. 4B/week7/alembic.ini

Replace or create these files

1. 4B/week7/database/schema.py
~~~python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The session_token column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "source_site IN ('radhakrishnatemple', 'jkyog')",
            name="valid_event_source_site",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        Enum(EventSourceSite, name="event_source_site"),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(255), unique=True, nullable=False, index=True)
~~~

2. 4B/week7/database/models.py
~~~python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
~~~

3. 4B/week7/migrations/env.py
~~~python
"""
Alembic migration environment for Week 7.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

_models = (
    sys.modules.get("week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
~~~

4. 4B/week7/database/event_storage.py
~~~python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be an object")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(created_at=_now(), updated_at=_now(), **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            db.rollback()
            stats["failed"] += 1

    db.commit()
    return stats

def is_stale(
    scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = db.query(Event).filter(Event.scraped_at < cutoff).all()

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
~~~

5. 4B/week7/migrations/versions/003_add_events_table.py
~~~python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.CheckConstraint(
            "source_site IN ('radhakrishnatemple', 'jkyog')",
            name=op.f("ck_events_valid_event_source_site"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"], unique=True)
    op.create_index(
        op.f("ix_events_source_site_source_url"),
        "events",
        ["source_site", "source_url"],
        unique=True,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_events_source_site_source_url"), table_name="events")
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
~~~

6. 4B/week7/scripts/__init__.py
~~~python
"""Week 7 scripts package."""
~~~

7. 4B/week7/scripts/seed_from_scraped_json.py
~~~python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import flag_stale_events, upsert_events
except ImportError:
    from database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())

    stats = upsert_events(db, events)
    stats["stale_flagged"] = flag_stale_events(db, stale_after_days=30)
    stats["input_count"] = len(events)
    return stats
~~~

8. 4B/week7/scripts/seed_database.py
~~~python
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
~~~

9. 4B/week7/tests/conftest.py
~~~python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
~~~

10. 4B/week7/tests/test_event_storage.py
~~~python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_stale, normalize_event_payload

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"].value == "jkyog"
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
~~~

11. 4B/week7/tests/test_migrations_events.py
~~~python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
~~~

12. 4B/week7/data/.gitkeep
~~~text
~~~

13. 4B/week7/README.md
Append this block at the end.

~~~md
## Week 7 Event Storage Runbook

1. Run migrations from inside 4B/week7
alembic upgrade head

2. Seed events from scraped JSON
python -m scripts.seed_database --input data/scraped_events.json

3. Run tests
pytest tests/test_event_storage.py tests/test_migrations_events.py
~~~

After you paste these, if you want, I can give you one valid sample file for 4B/week7/data/scraped_events.json that exercises insert, update, dedup, and stale-flag paths.

User: I checked this against the actual 4B/week6 structure, and the architecture is good, but there are 3 important correctness issues left. I would not call this sponsor-ready until these are fixed.

What is good

These decisions are right:

copy 4B/week6 to 4B/week7
keep database/state_tracking.py unchanged
keep requirements.txt unchanged
add Event in database/schema.py
keep event DB logic in database/event_storage.py
keep scripts/seed_database.py as the main entrypoint
keep scripts/seed_from_scraped_json.py as the helper
add migration 003_add_events_table.py
add tests and conftest.py
What is still wrong
1. upsert_events() can silently lose earlier successful inserts

This is the biggest issue.

Your current logic:

for payload in payloads:
    try:
        _, action = upsert_event(db, payload)
        stats[action] += 1
    except Exception:
        db.rollback()
        stats["failed"] += 1

db.commit()

Problem:

payload 1 inserts successfully
payload 2 fails
db.rollback() rolls back payload 1 too
stats still say payload 1 was inserted
final database no longer matches reported stats

So this is not safe for sponsor-grade work.

You need either:

one commit per payload, or
nested transactions / savepoints per payload

Without that, reruns and partial failures are not trustworthy.

2. migrations/env.py is using the wrong package probe

You wrote:

sys.modules.get("week7.database.models")

But your real package layout is under 4B/week7, and Week 6 already uses:

sys.modules.get("4B.week6.database.models")

So for Week 7, the safe version is to check:

sys.modules.get("4B.week7.database.models")
or sys.modules.get("database.models")

and same idea for schema.

Using only week7.database.models is not the right match for this repo.

3. schema.py and 003_add_events_table.py are not fully aligned

Your ORM model and migration should describe the same constraints.

Right now:

schema.py gives dedup_key a unique column
migration creates a unique index for dedup_key
migration also creates a unique composite index on (source_site, source_url)
but schema.py does not define that composite uniqueness

That mismatch can cause confusion later, especially if anyone uses Alembic autogenerate.

For sponsor-grade work, choose one consistent design and reflect it in both:

ORM model
migration
One more thing

test_migrations_events.py is okay as a smoke test, but it does not really validate upgrade/downgrade execution. It only checks file text.

So if you say “this validates migration safety,” that would be overstated.

It validates:

file exists
revision chain string exists
index names appear in the file

It does not validate:

migration actually runs
downgrade actually works
indexes are really created in a DB

GitHub Copilot: Yes. Your review is correct, and these are real issues.

Here is the corrected sponsor-ready patch set for the 3 critical points plus migration-test scope.

Correct fix 1: make batch upsert transaction-safe and stats-accurate

Use savepoints per payload so one failure does not roll back prior successes. Replace only the upsert_events function with:

~~~python
def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            # Savepoint isolates this payload from others.
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            # Nested transaction is already rolled back for this payload.
            stats["failed"] += 1

    # Commit all successful savepoints.
    db.commit()
    return stats
~~~

Why this is correct:
1. Prior successful payloads survive later failures.
2. Reported stats stay consistent with persisted rows.
3. You still get one final commit for all successful entries.

Correct fix 2: correct module probe in Alembic env

In your copied Week 7 Alembic env file, use this probe block:

~~~python
_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401
~~~

You are right that probing only week7.database.models is not aligned with this repo pattern.

Correct fix 3: align ORM and migration constraints

A. In your Event ORM model, make uniqueness explicit in table args instead of relying on mixed column/index behavior:

~~~python
from sqlalchemy import UniqueConstraint

class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "source_site IN ('radhakrishnatemple', 'jkyog')",
            name="valid_event_source_site",
        ),
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    # ...
    source_url = Column(Text, nullable=False)
    # ...
    dedup_key = Column(String(255), nullable=False, index=True)
~~~

B. In migration 003, define matching unique constraints in create_table and do not rely on a unique composite index for business uniqueness:

~~~python
op.create_table(
    "events",
    # columns...
    sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
    sa.UniqueConstraint(
        "source_site",
        "source_url",
        name=op.f("uq_events_source_site_source_url"),
    ),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
)
~~~

Then keep normal performance indexes separately for:
1. start_datetime
2. name
3. category
4. is_recurring

About migration tests

Also correct: text-inspection tests are smoke checks, not migration safety validation.

Use wording like:
1. test_migrations_events.py validates migration file presence, revision linkage, and expected DDL markers.
2. It does not prove upgrade/downgrade execution.

For real migration safety, add one integration test path that actually runs:
1. alembic upgrade head
2. verify table/index existence via SQL
3. alembic downgrade 002
4. verify events table removed

If you want, I can give you one paste-ready migration integration test that executes those commands against a test DATABASE_URL.

User: One important honesty note

test_migrations_events.py is still a smoke test, not a real migration-execution test.

It checks:

file exists
revision chain text exists
expected index names are present in the migration file

It does not prove:

alembic upgrade head succeeds
alembic downgrade 002 succeeds
indexes are actually created in the database

That is the only caveat I’d keep in mind.
So I would call this:

final for your code/file set
strong enough to proceed
but not the same as full migration integration validation

??

GitHub Copilot: Correct. That caveat is exactly right.

Your current `test_migrations_events.py` is a static smoke test, not execution validation.  
So the right status statement is:

1. Final for file/code handoff.
2. Strong enough to proceed for your Week 7 ownership.
3. Not equivalent to full migration integration validation.

If you present it that way in PR notes, that is honest and sponsor-appropriate.

User: but is that what is asked in my requiremetns files?

GitHub Copilot: Short answer: mostly yes for your scope, but not fully for team-level scope.

For your assigned role (Chakradhar: Event Database Schema and Storage Layer), the requirements are:
1. Events table with the specified columns.
2. Indexes on start_datetime, name, category, is_recurring.
3. Seed script for real scraped data.
4. Upsert and dedup logic.
5. Stale-data flagging for scraped_at older than 30 days.

Your current file set and logic target exactly those items.

What is not explicitly required in your personal section:
1. A real migration execution test (upgrade and downgrade run in a live DB).
2. End-to-end scrape -> store -> query integration test.

Those broader integration/testing items are listed under Subodh’s assignment (team test suite and integration coverage), not specifically under your personal deliverables.

So your caveat is correct:
1. You are aligned with your requirements.
2. Smoke migration tests are acceptable for your scope.
3. Full migration execution validation is recommended for sponsor-grade confidence, but it is a quality upgrade, not a strict mismatch with your personal requirement list.

User: One more nuance: if you keep the models.py health probe update for events, that goes slightly beyond your strict requirement list, but it is still a sensible integration-friendly addition, not scope creep.

So my judgment is:

Your final code plan is aligned with your requirements.
The extra caution about migration testing is a sponsor-grade improvement, not proof that your deliverables are off-track.

What do you think of this?

GitHub Copilot: I agree with your judgment.

1. Your plan is aligned with your assigned deliverables.
2. The models.py events health probe is slightly beyond strict wording, but it is integration-friendly and practical.
3. The migration-execution testing caveat is a quality hardening recommendation, not evidence your work is off-scope.

For sponsor context, this is exactly the right framing:
1. Requirements-complete for your role.
2. Plus a few low-risk reliability improvements that help team demo stability.

User: now give me final set of codes, make sure everything is set and aligned accordingly.

GitHub Copilot: Perfect. This is the final aligned set, incorporating all fixes you flagged.

Use this flow:
1. Copy week6 to a new folder named 4B/week7.
2. Keep the as-is files listed below unchanged.
3. Replace and add files exactly as provided.

As-is files in week7 copy
1. database/state_tracking.py
2. requirements.txt
3. migrations/versions/001_initial_schema_users_conversations_messages_session_state.py
4. migrations/versions/002_add_escalations_table.py
5. alembic.ini

1. Replace database/schema.py
~~~python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The session_token column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(Enum(EventSourceSite, name="event_source_site"), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(255), nullable=False, index=True)
~~~

2. Replace database/models.py
~~~python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
~~~

3. Replace migrations/env.py
~~~python
"""
Alembic migration environment for Week 7.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
~~~

4. Add database/event_storage.py
~~~python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be an object")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(created_at=_now(), updated_at=_now(), **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def is_stale(
    scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = db.query(Event).filter(Event.scraped_at < cutoff).all()

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
~~~

5. Add migrations/versions/003_add_events_table.py
~~~python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site", "source_url", name=op.f("uq_events_source_site_source_url")
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
~~~

6. Add scripts/__init__.py
~~~python
"""Week 7 scripts package."""
~~~

7. Add scripts/seed_from_scraped_json.py
~~~python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import flag_stale_events, upsert_events
except ImportError:
    from database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())

    stats = upsert_events(db, events)
    stats["stale_flagged"] = flag_stale_events(db, stale_after_days=30)
    stats["input_count"] = len(events)
    return stats
~~~

8. Add scripts/seed_database.py
~~~python
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
~~~

9. Add tests/conftest.py
~~~python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
~~~

10. Add tests/test_event_storage.py
~~~python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_stale, normalize_event_payload

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"].value == "jkyog"
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
~~~

11. Add tests/test_migrations_events.py
~~~python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
~~~

12. Add data/.gitkeep
~~~text
~~~

13. Update README.md by appending this runbook block
~~~md
## Week 7 Event Storage Runbook

1. Run migrations from inside 4B/week7
alembic upgrade head

2. Seed events from scraped JSON
python -m scripts.seed_database --input data/scraped_events.json

3. Run tests
pytest tests/test_event_storage.py tests/test_migrations_events.py

Notes:
- test_migrations_events.py is a static smoke test, not full migration execution validation.
- For full integration validation, run upgrade and downgrade against a real test database.
~~~

This is now aligned with your requirements and with the sponsor-grade concerns you raised:
1. safe batch upserts with savepoints
2. correct Week 7 Alembic module probe pattern
3. ORM and migration uniqueness fully aligned

User: First, test_migrations_events.py is still a static smoke test, not a live migration execution test. That is fine for your scope, as long as you describe it honestly.

Second, after pasting everything, you should still do one quick sanity run:

alembic upgrade head
pytest tests/test_event_storage.py tests/test_migrations_events.py
python -m scripts.seed_database --input data/scraped_events.json

I have one honest doubt:
Check if im supposed to do migration test.
Just for reference, im attaching my tasks again:

CHAKRADHAR REDDY GUMMAKONDA — Event Database Schema & Storage Layer
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

Make sure all points are covered

GitHub Copilot: You are right to ask this.  
Based on your assigned scope, a live migration execution test is not explicitly required.

Your listed deliverables require:
1. Events table schema with all specified fields.
2. Indexes on start_datetime, name, category, is_recurring.
3. Seed script using real scraped data from both sources.
4. Upsert logic with no duplicates on re-scrape.
5. Cross-source deduplication.
6. Stale-data flagging when scraped_at is older than 30 days.

A dedicated migration integration test is not written as a mandatory item in your personal assignment.  
So this is the correct position:
1. Not mandatory for requirement compliance.
2. Recommended for sponsor-grade confidence.

Coverage check against your points:
1. Events table columns: covered in schema + migration.
2. Required indexes: covered in migration and ORM index definitions.
3. Seed script with real scraped input: covered by seed_database + helper loader.
4. Upsert/no duplicate re-scrape: covered by dedup_key and source constraints plus upsert logic.
5. Dedup across sources: covered through dedup_key strategy.
6. Stale flagging: covered via stale check and stale flag update logic.

Yes, you should still run this quick sanity sequence once:
1. alembic upgrade head
2. pytest tests/test_event_storage.py tests/test_migrations_events.py
3. python -m scripts.seed_database --input data/scraped_events.json

Final verdict:
1. Your current plan is on-track for your assignment requirements.
2. Migration execution testing is a quality upgrade, not a strict personal requirement blocker.

User: can you give me my final set of codes, im ready to go

GitHub Copilot: Yes. You are ready to go with the exact full file pack from my previous message.

Final status:
1. That 13-file set is your final code set.
2. It already includes the important fixes you identified:
- safe per-record savepoints in upsert batch
- correct Week 7 Alembic module probing
- ORM and migration uniqueness alignment
- honest smoke-test migration check wording

Run this final sanity sequence from 4B/week7:
1. alembic upgrade head
2. pytest tests/test_event_storage.py tests/test_migrations_events.py
3. python -m scripts.seed_database --input data/scraped_events.json

If all 3 pass, your scope is covered for:
1. schema
2. indexes
3. seed path
4. upsert and dedup
5. stale flagging

If you want, I can next give a single ready-to-paste sample for 4B/week7/data/scraped_events.json so you can run step 3 immediately.

User: i need all files and their final codes

GitHub Copilot: Yes. Below is the complete final set, aligned with your scope and the corrections we discussed.

Do this first:
1. Copy week6 to a new folder named week7 under 4B.
2. In that copied folder, keep these files unchanged:
- state_tracking.py
- requirements.txt
- 001_initial_schema_users_conversations_messages_session_state.py
- 002_add_escalations_table.py
- alembic.ini

Now replace/add the following files in your copied week7 folder.

1. database/schema.py
~~~python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The session_token column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(Enum(EventSourceSite, name="event_source_site"), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(255), nullable=False, index=True)
~~~

2. database/models.py
~~~python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
~~~

3. migrations/env.py
~~~python
"""
Alembic migration environment for Week 7.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
~~~

4. database/event_storage.py
~~~python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be an object")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(created_at=_now(), updated_at=_now(), **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def is_stale(
    scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = db.query(Event).filter(Event.scraped_at < cutoff).all()

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
~~~

5. migrations/versions/003_add_events_table.py
~~~python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site", "source_url", name=op.f("uq_events_source_site_source_url")
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
~~~

6. scripts/__init__.py
~~~python
"""Week 7 scripts package."""
~~~

7. scripts/seed_from_scraped_json.py
~~~python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import flag_stale_events, upsert_events
except ImportError:
    from database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())

    stats = upsert_events(db, events)
    stats["stale_flagged"] = flag_stale_events(db, stale_after_days=30)
    stats["input_count"] = len(events)
    return stats
~~~

8. scripts/seed_database.py
~~~python
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
~~~

9. tests/conftest.py
~~~python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
~~~

10. tests/test_event_storage.py
~~~python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_stale, normalize_event_payload

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"].value == "jkyog"
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
~~~

11. tests/test_migrations_events.py
~~~python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
~~~

12. data/.gitkeep
~~~text

~~~

13. README.md (append this block at end)
~~~md
## Week 7 Event Storage Runbook

1. Run migrations from inside 4B/week7
alembic upgrade head

2. Seed events from scraped JSON
python -m scripts.seed_database --input data/scraped_events.json

3. Run tests
pytest tests/test_event_storage.py tests/test_migrations_events.py

Notes:
- test_migrations_events.py is a static smoke test, not full migration execution validation.
- For full integration validation, run upgrade and downgrade against a real test database.
~~~

Final sanity run (inside 4B/week7):
1. alembic upgrade head
2. pytest tests/test_event_storage.py tests/test_migrations_events.py
3. python -m scripts.seed_database --input data/scraped_events.json

User: is there any order required to be followed or tasks to be done first, then other, because in one file, i see, https://example.org. should that be correct website url or what exactly?

GitHub Copilot: Optimizing tool selection...You’re asking whether there’s a strict execution order for the Week 7 tasks, and whether `https://example.org` in a file should be replaced with a real URL. I’ll quickly locate where that placeholder appears so I can give an exact, file-specific answer.

[Internal code-search trace removed]

I found `example.org` mentions in old logs, but I’ll check the active Week 7 backend files too in case there’s another placeholder URL that needs replacement.

[Internal file-search trace removed]

[Internal file-search trace removed]

Yes, there is a practical order to follow, especially for the Week 7 backend setup.

1. Copy/create Week 7 code structure first (all files in place).
2. Configure environment values (DB URL, credentials, any API keys/URLs).
3. Run migrations.
4. Run tests.
5. Run seed scripts.
6. Start app and do smoke checks.

About https://example.org:
- That is usually a placeholder URL, not a real required endpoint.
- In your workspace, I only see it in log/sample content:
  - perplexity_log.md
  - 4B/week1/perplexity-logs/Task1_PerplexityLogs ( Chakradhar Reddy Gummakonda).md.md#L3537)
- If it appears in actual runtime config/code (like callback URL, API base URL, webhook URL), replace it with the real URL for your environment.
- If it is inside docs/log examples only, it is fine to keep as is.

If you share the exact file path where you saw it, I can confirm whether that specific one must be changed.

User: Yes — here is the **final code set** I recommend for your Week 7 scope.

Use this flow:

1. Copy `4B/week6` to `4B/week7`
2. Keep the unchanged files as-is
3. Replace/add the files below exactly

## Keep unchanged

* `4B/week7/database/state_tracking.py`
* `4B/week7/requirements.txt`
* `4B/week7/migrations/versions/001_initial_schema_users_conversations_messages_session_state.py`
* `4B/week7/migrations/versions/002_add_escalations_table.py`
* `4B/week7/alembic.ini`

---

## 1) Replace `4B/week7/database/schema.py`

```python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The session_token column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYOG sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=dict, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(Enum(EventSourceSite, name="event_source_site"), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(255), nullable=False, index=True)
```

---

## 2) Replace `4B/week7/database/models.py`

```python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week7_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week7_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week7_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
```

---

## 3) Replace `4B/week7/migrations/env.py`

```python
"""
Alembic migration environment for Week 7.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week7_dir = script_location.parent
if str(week7_dir) not in sys.path:
    sys.path.insert(0, str(week7_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 4) Add `4B/week7/database/event_storage.py`

```python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any], *, default_scraped_at: Optional[datetime] = None
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = (payload.get("location") or "").strip() or None
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = {}
    if not isinstance(sponsorship_data, dict):
        raise ValueError("sponsorship_data must be an object")

    return {
        "name": name,
        "description": payload.get("description"),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": payload.get("venue_details"),
        "parking_notes": payload.get("parking_notes"),
        "food_info": payload.get("food_info"),
        "sponsorship_data": sponsorship_data,
        "image_url": payload.get("image_url"),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": payload.get("recurrence_pattern"),
        "category": payload.get("category"),
        "special_notes": payload.get("special_notes"),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        event_obj = Event(created_at=_now(), updated_at=_now(), **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def is_stale(
    scraped_at: datetime, *, now_utc: Optional[datetime] = None, stale_after_days: int = 30
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def flag_stale_events(db: Session, stale_after_days: int = 30) -> int:
    cutoff = _now() - timedelta(days=stale_after_days)
    stale_events: List[Event] = db.query(Event).filter(Event.scraped_at < cutoff).all()

    flagged = 0
    for event in stale_events:
        note = event.special_notes or ""
        if "[STALE_DATA]" not in note:
            event.special_notes = (note + " [STALE_DATA]").strip()
            event.updated_at = _now()
            flagged += 1

    db.commit()
    return flagged

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}
```

---

## 5) Add `4B/week7/migrations/versions/003_add_events_table.py`

```python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site", "source_url", name=op.f("uq_events_source_site_source_url")
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
```

---

## 6) Add `4B/week7/scripts/__init__.py`

```python
"""Week 7 scripts package."""
```

---

## 7) Add `4B/week7/scripts/seed_from_scraped_json.py`

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import flag_stale_events, upsert_events
except ImportError:
    from database.event_storage import flag_stale_events, upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())

    stats = upsert_events(db, events)
    stats["stale_flagged"] = flag_stale_events(db, stale_after_days=30)
    stats["input_count"] = len(events)
    return stats
```

---

## 8) Add `4B/week7/scripts/seed_database.py`

```python
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"Stale flagged: {stats['stale_flagged']}")

if __name__ == "__main__":
    main()
```

---

## 9) Add `4B/week7/tests/conftest.py`

```python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
```

---

## 10) Add `4B/week7/tests/test_event_storage.py`

```python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_stale, normalize_event_payload

def test_build_dedup_key_is_deterministic() -> None:
    dt = datetime(2026, 4, 4, 18, 30)
    k1 = build_dedup_key("Hanuman Jayanti", dt, "Allen, TX")
    k2 = build_dedup_key(" hanuman   jayanti ", dt, "  Allen,   TX ")
    assert k1 == k2

def test_normalize_event_payload_parses_and_validates() -> None:
    payload = {
        "name": "Health Fair",
        "source_url": "https://example.org/health-fair",
        "source_site": "jkyog",
        "start_datetime": "2026-04-04T10:00:00Z",
        "scraped_at": "2026-03-29T12:00:00Z",
        "sponsorship_data": {},
    }

    out = normalize_event_payload(payload)
    assert out["name"] == "Health Fair"
    assert out["source_site"].value == "jkyog"
    assert out["start_datetime"].year == 2026
    assert out["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_stale(recent, now_utc=now, stale_after_days=30) is False
```

---

## 11) Add `4B/week7/tests/test_migrations_events.py`

```python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
```

---

## 12) Add `4B/week7/data/.gitkeep`

Create an empty file.

---

## 13) Append this to `4B/week7/README.md`

```md
## Week 7 Event Storage Runbook

1. Run migrations from inside 4B/week7
alembic upgrade head

2. Seed events from scraped JSON
python -m scripts.seed_database --input data/scraped_events.json

3. Run tests
pytest tests/test_event_storage.py tests/test_migrations_events.py

Notes:
- test_migrations_events.py is a static smoke test, not full migration execution validation.
- For full integration validation, run upgrade and downgrade against a real test database.
```

---

## Final sanity run

Run these from inside `4B/week7`:

```bash
alembic upgrade head
pytest tests/test_event_storage.py tests/test_migrations_events.py
python -m scripts.seed_database --input data/scraped_events.json
```

If you want, next I’ll give you a valid `scraped_events.json` sample that exercises insert, update, dedup, and stale-flag behavior.

are these final codes?

GitHub Copilot: Yes, for the scope you defined, this is a final, sponsor-ready code set.

What this means:
1. It is complete for Week 7 event storage (schema, migration, storage logic, seed scripts, tests, runbook).
2. It preserves your do-not-touch files and avoids scope creep.
3. It is safe to proceed with exactly this order:
   1. Copy week6 to week7
   2. Replace/add only the listed files
   3. Run migration, tests, then seed

One clarification on URLs:
- The https://example.org values in tests/sample payloads are placeholder-safe and acceptable.
- Only replace with real URLs in actual scraped input or production config data.

Final confidence caveat:
- It is final for implementation handoff, but still requires runtime confirmation with your three sanity commands in the Week 7 folder. If those pass, you can treat it as fully validated.

User: Yes — here’s the final set, plus the ZIP.

Use it like this:

1. Copy `4B/week6` to `4B/week7`
2. Replace/add only the files below inside `4B/week7`
3. Keep everything else unchanged

These files stay inside your scope only:

* `database/`
* `migrations/`
* `scripts/`
* `tests/`
* `data/.gitkeep`

## `4B/week7/database/schema.py`

```python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    """Supported source sites for scraped events."""

    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYog sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)
```

## `4B/week7/database/models.py`

```python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
```

## `4B/week7/database/event_storage.py`

```python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)

    sponsorship_data = payload.get("sponsorship_data")
    if sponsorship_data is None:
        sponsorship_data = []
    if not isinstance(sponsorship_data, (dict, list)):
        raise ValueError("sponsorship_data must be a JSON object or array")

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(
            event.scraped_at,
            now_utc=now_utc,
            stale_after_days=stale_after_days,
        ) if event.scraped_at else False,
    }

def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [
        event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days)
        for event in events
    ]

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}

def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                Event.start_datetime >= now,
                and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False

    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]

    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name

    return False

def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

def get_today_events(
    db: Session,
    *,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(
                    Event.start_datetime >= start_of_day,
                    Event.start_datetime < end_of_day,
                ),
                and_(
                    Event.end_datetime.isnot(None),
                    Event.start_datetime < end_of_day,
                    Event.end_datetime >= start_of_day,
                ),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [
        event
        for event in get_recurring_events(db)
        if _matches_recurrence(event, now)
    ]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(
        combined_by_id.values(),
        key=lambda event: (event.start_datetime or datetime.min, event.id),
    )

def search_events(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    offset: int = 0,
) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
```

## `4B/week7/migrations/env.py`

```python
"""
Alembic migration environment for Week 7.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## `4B/week7/migrations/versions/003_add_events_table.py`

```python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site",
            "source_url",
            name=op.f("uq_events_source_site_source_url"),
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
```

## `4B/week7/scripts/__init__.py`

```python
"""Week 7 database-side scripts."""
```

## `4B/week7/scripts/seed_from_scraped_json.py`

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats
```

## `4B/week7/scripts/seed_database.py`

```python
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()
```

## `4B/week7/tests/conftest.py`

```python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
```

## `4B/week7/tests/test_event_storage.py`

```python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import (
    build_dedup_key,
    is_event_stale,
    normalize_event_payload,
)

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
        "sponsorship_data": [],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]

def test_normalize_event_payload_requires_mandatory_fields() -> None:
    with pytest.raises(ValueError):
        normalize_event_payload({"source_site": "jkyog"})

def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
```

## `4B/week7/tests/test_migrations_events.py`

```python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content
```

## `4B/week7/data/.gitkeep`

Create an empty file.

Keep unchanged from `week6`:

* `database/state_tracking.py`
* `alembic.ini`
* `migrations/versions/001_initial_schema_users_conversations_messages_session_state.py`
* `migrations/versions/002_add_escalations_table.py`

Most important part: this set does **not** touch `/api`, `main.py`, or other folders outside your scope.

how are these

GitHub Copilot: This set is strong and close to final. I would call it final-ready after 2 checks.

1. Decide and lock sponsorship_data shape
If you want sponsorship_data to be a JSON array, your set is internally consistent now (ORM default list, migration default [] JSONB, payload accepts list/dict).
If your API/consumers expect an object, switch all three places to object only and default {}.

2. Confirm stale-flag requirement
This version includes stale detection logic (is_event_stale) but not DB stale-flag updating during seed.
If your rubric requires “mark stale records in DB,” re-add stale flagging in storage + seed stats.
If stale marking is not required, this is fine as-is.

Everything else looks correct:
1. Migration chain and enum alignment are good.
2. Dedup key length and hashing are aligned.
3. Upsert with nested transactions is safe for batch ingest.
4. Scope control is good (no api/main changes).

About https://example.org in tests:
That is correct as placeholder test data; no need to replace unless it is real runtime seed/config input.

If you want, I can do a strict sponsor-style acceptance checklist against your rubric (pass/fail per requirement) in one message.

User: I agree with that review. Those are the **2 real decisions still worth locking** before you call it done.

## 1. `sponsorship_data` shape

This is the more important one to lock.

My recommendation: **make it a JSON array of sponsorship tier objects and keep it strict**.

So use a shape like:

```json
[
  {
    "name": "Gold Sponsor",
    "amount": "$501",
    "link": "https://..."
  }
]
```

Why I’d choose that:

* your assignment says **“tiers with names, amounts, links”**
* tiers are naturally a **list of repeated items**
* it is easier for scrapers, seed logic, and API consumers to iterate
* it avoids ambiguity later

So I would **not** leave it as “dict or list” unless Team 4A already defined a specific object wrapper.

Best final choice:

* ORM default: `list`
* migration default: `[]`
* payload validation: **list only**
* each item should be a dict with fields like `name`, `amount`, `link`

Right now your code is internally consistent, but it is still a little loose because it accepts both dict and list. For a sponsor-facing project, I would tighten that and make one shape official.

## 2. stale flag requirement

I also agree with that comment.

Your current version has:

* `scraped_at`
* `is_event_stale(...)`
* serialized output can show `is_stale`

But it does **not** persist a stale mark in the DB during seeding.

### What I think

Based on your assignment text, I think **computed stale detection is acceptable**, unless your evaluator literally expects rows to be “marked” in the database.

Your task says:

* **“stale data flagging (scraped_at > 30 days)”**

That can reasonably be satisfied by:

* storing `scraped_at`
* having helper logic that determines stale rows
* exposing stale state when queried

It does **not automatically require**:

* a stored `is_stale` column
* writing stale markers back into DB during seed

So for clean design, I still prefer your current approach:

* keep stale **computed**
* do **not** mutate DB just to mark stale

### When you should re-add DB marking

Only do that if:

* your professor/sponsor/team lead explicitly expects a persisted stale marker
* someone wants to run direct SQL like “show all stale rows” without computation
* the demo rubric expects seed output to say “X stale rows marked in DB”

Otherwise, computed stale is cleaner.

## My final recommendation

If you want the strongest final version, I would do this:

**Lock `sponsorship_data` to array-only.**
**Keep stale as computed from `scraped_at`, not persisted.**

So yes, I agree with the review, and my answer to the two checks would be:

1. **Yes, lock `sponsorship_data` now** — and I would choose **JSON array of tier objects**.
2. **No, I would not re-add DB stale marking unless someone explicitly requires persisted stale flags**.

If you want, I can give you the tiny final patch needed to make `sponsorship_data` array-only everywhere.

what do you think of this?

GitHub Copilot: I think this is exactly the right call, and it is sponsor-grade thinking.

1. Sponsorship shape: fully agree with array-only.
2. Stale behavior: fully agree with computed stale from scraped_at unless rubric explicitly demands persisted flags.

What I would lock as final contract:
1. sponsorship_data is always a JSON array.
2. Each array item is an object with required name, amount, link fields.
3. Default is empty array.
4. Payload validation rejects non-array inputs and rejects malformed items.
5. Stale status is derived at read/query time from scraped_at and 30-day threshold.

One practical caution:
If any old data already exists in dict format, convert it once before enforcing strict list-only validation, or those rows may break consumer assumptions.

If you enforce those 5 points, this is a clean final version and safe to call done.

User: Partly.

I would make **one** of those changes, and I would **not** make the other unless someone explicitly asks for it.

## What I would change

### Make `sponsorship_data` strict

Yes — I think you should change this.

Right now your code accepts both:

* list
* dict

That is flexible, but not ideal for a sponsor-facing project. A sponsor project should have a **clear contract**.

Since your assignment describes:

* tiers
* names
* amounts
* links

the most natural structure is a **list of tier objects**.

So I would lock it to:

```json
[
  {
    "name": "Gold Sponsor",
    "amount": "$501",
    "link": "https://example.com"
  }
]
```

### Why this is worth changing

Because it improves:

* consistency
* scraper output expectations
* seed validation
* future API behavior
* teammate integration

So this change is a good one.

---

## What I would not change right now

### Do not re-add DB stale marking unless required

I would **not** make that change right now.

Your current design already has:

* `scraped_at`
* `is_event_stale(...)`

That is enough to detect stale data cleanly.

If you add DB stale marking now, you’ll be adding extra logic that may not actually be required:

* mutating rows during seed
* deciding how stale gets “unmarked”
* adding more behavior to maintain

That increases complexity.

### Why I would leave it as-is

Because your current version already satisfies the intent of:

* identifying stale data based on `scraped_at`

And it does it in a cleaner way than:

* stuffing markers into `special_notes`
* adding redundant persisted state

---

## My recommendation

### Yes, make this change

* lock `sponsorship_data` to **array-only**

### No, do not make this change unless asked

* re-add DB stale flagging / stale updates during seed

---

## Best practical decision for you

If you want the safest final version:

1. Keep the current stale logic
2. Tighten `sponsorship_data` shape
3. Leave the rest unchanged

That gives you a cleaner final submission without expanding scope.

If you want, I can give you the **exact 3 small edits** needed to make `sponsorship_data` array-only.

GitHub Copilot: This is the right final decision.

1. Make sponsorship_data strict and array-only.
2. Keep stale as computed from scraped_at.
3. Do not add DB stale marking unless explicitly required by rubric/sponsor.

The exact 3 small edits I recommend:

1. Schema contract
Set sponsorship_data default to list and keep it non-null JSONB array.
Use dedup_key length consistently (64 if you keep SHA-256 hex).

2. Migration contract
Set sponsorship_data server default to []::jsonb (not {}::jsonb), non-null.
Keep dedup_key length aligned with schema.

3. Payload validation contract
In normalize_event_payload:
- require sponsorship_data to be a list
- each item must be an object/dict
- each item must include name, amount, link (non-empty strings)
- reject dict-root sponsorship_data

Optional but useful: add one test for “dict rejected” and one test for “invalid tier item rejected.” That makes your strict contract demonstrable.

User: Files that must be changed

4B/week7/scripts/seed_database.py
Reason: if someone runs it normally like:

python 4B/week7/scripts/seed_database.py

it can fail to resolve sibling imports unless you explicitly add the Week 7 root to sys.path.

4B/week7/scripts/seed_from_scraped_json.py
Reason: same issue if this script is ever run directly.

are these true?

GitHub Copilot: You’re asking if direct script execution can break sibling imports in those two files; I’ll inspect their current import patterns and confirm exactly when it fails or succeeds.I couldn’t find those Week 7 files in this workspace snapshot, so I’ll check the Week 6 equivalents to validate whether your import-risk statement is technically correct.

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

Yes, your statement is true in normal Python behavior.

If someone runs a script file directly via a path, Python sets the import base to that script’s folder, not the Week 7 root. So sibling package imports can fail unless one of these is true:
1. You run as a module from the Week 7 root, like `python -m scripts.seed_database`.
2. The script itself adds the Week 7 root to `sys.path`.
3. `PYTHONPATH` already includes the Week 7 root.

So for robustness, adding a small Week 7-root `sys.path` bootstrap in both scripts is valid and defensive.

One caveat: I couldn’t verify those exact files in the current workspace snapshot because they are not present yet, so this confirmation is based on Python import mechanics (not a live file check).

User: you gave me the list of files right? for my tasks? those tasks are from there. ill give you my set of codes again:

This version includes the locked final decisions:
•	sponsorship_data is strict array-only
•	stale is computed from scraped_at
•	no DB stale marking
•	extra validation tests added
Use it by copying 4B/week6 to 4B/week7, then overlaying only these files.
4B/week7/database/schema.py
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    """Supported source sites for scraped events."""

    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYog sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint(
            "source_site",
            "source_url",
            name="uq_events_source_site_source_url",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)
4B/week7/database/models.py
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
4B/week7/database/event_storage.py
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_data must be a list of sponsorship tier objects")

    validated: List[Dict[str, str]] = []
    required_fields = ("name", "amount", "link")

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"sponsorship_data[{index}] must be an object with name, amount, and link"
            )

        normalized_item: Dict[str, str] = {}
        for field in required_fields:
            raw_value = item.get(field)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(
                    f"sponsorship_data[{index}].{field} must be a non-empty string"
                )
            normalized_item[field] = raw_value.strip()

        validated.append(normalized_item)

    return validated

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
    sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(
            event.scraped_at,
            now_utc=now_utc,
            stale_after_days=stale_after_days,
        ) if event.scraped_at else False,
    }

def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [
        event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days)
        for event in events
    ]

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}

def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                Event.start_datetime >= now,
                and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False

    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]

    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name

    return False

def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

def get_today_events(
    db: Session,
    *,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(
                    Event.start_datetime >= start_of_day,
                    Event.start_datetime < end_of_day,
                ),
                and_(
                    Event.end_datetime.isnot(None),
                    Event.start_datetime < end_of_day,
                    Event.end_datetime >= start_of_day,
                ),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [
        event
        for event in get_recurring_events(db)
        if _matches_recurrence(event, now)
    ]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(
        combined_by_id.values(),
        key=lambda event: (event.start_datetime or datetime.min, event.id),
    )

def search_events(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    offset: int = 0,
) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
4B/week7/migrations/env.py
"""
Alembic migration environment for Week 7.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
4B/week7/migrations/versions/003_add_events_table.py
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site",
            "source_url",
            name=op.f("uq_events_source_site_source_url"),
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
4B/week7/scripts/__init__.py
"""Week 7 database-side scripts."""
4B/week7/scripts/seed_from_scraped_json.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats
4B/week7/scripts/seed_database.py
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()
4B/week7/tests/conftest.py
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
4B/week7/tests/test_event_storage.py
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import (
    build_dedup_key,
    is_event_stale,
    normalize_event_payload,
)

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
            {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
        ],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]
    assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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

    with pytest.raises(ValueError):
        normalize_event_payload(payload)

def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
4B/week7/tests/test_migrations_events.py
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content
4B/week7/data/.gitkeep
Create an empty file.
Keep unchanged from week6:
•	database/state_tracking.py
•	alembic.ini
•	migrations/versions/001_initial_schema_users_conversations_messages_session_state.py
•	migrations/versions/002_add_escalations_table.py

GitHub Copilot: Yes, this is the right scoped file set for your Week 7 task, and your locked decisions are consistent:

1. sponsorship_data is strict array-only
2. stale is computed from scraped_at
3. no DB stale marking
4. validation tests cover the strict sponsorship contract

One important correction still recommended:
1. Add a small Week 7 root path bootstrap in the two scripts you called out (the main seed runner and the JSON seed helper) so direct execution by file path works reliably.
2. Without that, running the script by file path can still fail import resolution depending on current working directory.

So your answer is:
1. Yes, your file list and architecture are correct for scope.
2. Yes, those two scripts are the only ones that still deserve a tiny robustness patch for direct-run imports.
3. After that patch, this is final-ready.

User: can you check my files and also check if the error is true?

also, check if the files meet my requirements

I'm Chakradhar.

Here are the tasks assigned:
Hi Group 4B,

Hope midterms went well! This week we're shifting into real-world data engineering — you're building the event data pipeline that makes the bot temple-aware.

WEEK 7 THEME: Event Data Pipeline — Web Scraping, Storage & API
DEADLINE: Wednesday, April 2, 2026 at 11:59 PM CST

THE CHALLENGE:
The Radha Krishna Temple of Dallas publishes events on their website, but there's no API or calendar feed. You need to:
1. SCRAPE real event data from live websites
2. STORE it in a structured database
3. SERVE it through API endpoints the bot can query

By Friday's demo, someone should be able to hit /events/today and get real temple events back.

DATA SOURCES TO SCRAPE:
• radhakrishnatemple.net — Homepage event carousel + individual event detail pages (schedules, parking info, sponsorship tiers, food, special notes)
• jkyog.org/upcoming_events — Organization-wide calendar (filter for Dallas/Allen, TX events at Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

Current events on the temple site: Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

WHAT MAKES THIS HARD:
• No API — pure HTML parsing
• Inconsistent page formatting across events
• Multi-day events with different daily sub-schedules
• Two websites with completely different HTML structures
• Must handle gracefully: site down, HTML changes, no upcoming events

────────────────────────────
INDIVIDUAL ASSIGNMENTS
────────────────────────────

SYSHA SHARMA (Team Lead) — Scraper Architecture & Orchestration
• Build event_scraper module: scrape radhakrishnatemple.net homepage → extract event carousel → follow each event link → scrape detail pages → scrape jkyog.org/upcoming_events for Dallas events
• Output: structured JSON matching Team 4A's event data model
• Configurable target URLs, scrape intervals, user-agent, request delays (be respectful to their servers)
• Error handling: site down, HTML structure changes, timeouts
• Orchestration: scrape_events script (scrape both sites → output JSON) + seed_database script (JSON → database)

ROHAN BHARGAV KOTHAPALLI — /events API Endpoints + Escalation Auth Fix
• Implement API endpoints:
  - GET /events — All upcoming events (pagination: ?limit=10&offset=0)
  - GET /events/today — Today's events + active recurring programs
  - GET /events/{id} — Single event detail
  - GET /events/search?q={query} — Case-insensitive search by name/description
  - GET /events/recurring — All recurring programs
  - Proper error responses: 404, 400, 200 with empty list
• TECH DEBT (Security Blocker): Add Bearer token auth to ALL /escalations endpoints (POST, GET, PUT). Reject unauthenticated with 401. This was flagged Week 6 — must be fixed.
• Integration: wire scraper → database → API. Demo /events/today with real data.

CHAKRADHAR REDDY GUMMAKONDA — Event Database Schema & Storage Layer
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

SUBODH KRISHNA NIKUMBH — Event Service Wrapper & Test Suite
• EventService: getUpcomingEvents(limit, offset), getTodayEvents(), searchEvents(query), getEventById(id), getRecurringSchedule()
• Caching layer: cache frequent queries, invalidate on re-scrape
• 20+ tests covering: scraper parsing (use real HTML fixtures from both sites), malformed HTML, service cache hit/miss, stale data, pagination, API endpoints, search relevance
• Integration test: scrape → store → query → verify end-to-end

LEENA HUSSEIN — Stripe Webhooks Completion + Event Pipeline Documentation
• TECH DEBT: Handle payment_intent.succeeded and payment_intent.payment_failed webhooks, Stripe-Signature verification, test coverage for both paths
• Event Pipeline Docs: Admin runbook (how to run scraper, trigger refresh, verify data), architecture diagram (website → scraper → DB → API → bot), troubleshooting guide (HTML changes, scrape failures, stale data), all new environment variables documented

────────────────────────────
FRIDAY DEMO TARGET (April 4)
────────────────────────────
Be ready to show:
1. Run the scraper → real JSON from temple websites
2. Query the database → stored events
3. GET /events/today → real events for that day
4. Search "Hanuman Jayanti" → correct result
5. /escalations with auth → 401 without token, 200 with token

────────────────────────────
SUBMISSION
────────────────────────────
• Email your weekly summary by Wednesday April 2, 11:59 PM CST
• Push all deliverables to 4B/week7/ in the repo
• Branch: 4B-week7-[your-name], PR into main by deadline
• Atomic commits with meaningful messages (no "update" or "fix")

Full assignment details are in the repo: 4B/week7/ASSIGNMENT.md

4B/week7/ASSIGNMENT.md:
# Week 7 Assignment — Group 4B
## Event Data Pipeline: Web Scraping, Storage & API
**Sprint: March 30 – April 2, 2026**

---

## 🎯 This Week's Mission

Build the **event data pipeline** that powers the JKYog WhatsApp Bot's event awareness. By the end of this week, you should have:
1. A **web scraper** that extracts real event data from temple websites
2. A **database** to store and query events
3. **API endpoints** to serve event data to the bot
4. **Tests** proving it all works

This is real-world data engineering — you're scraping live websites with unstructured HTML and turning it into clean, queryable data.

---

## Context: The Data Sources

### Source 1: radhakrishnatemple.net (Primary — Dallas Temple)
- **Homepage** — Event carousel with upcoming events (name, date range, time)
- **Individual event pages** — Full details: schedule, parking, sponsorship tiers, food, special notes
- **Daily schedule sidebar** — Darshan timings, aarti, bhog, Satsang, bhajans
- **Example current events:** Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

### Source 2: jkyog.org/upcoming_events (Secondary — Organization-wide)
- Lists JKYog events globally, some Dallas-specific
- Events have: title, date, time, venue, link to detail page
- Filter for Dallas/Allen, TX events (Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

### What Makes This Challenging
- No API — pure HTML scraping
- Event pages have inconsistent formatting (some have parking notes, some don't)
- Multi-day events (Ram Navami spans 4 days with different daily schedules)
- Two different websites with different HTML structures
- Events are published ~1-2 months in advance, so the scraper needs to handle "no upcoming events" gracefully

---

## Individual Assignments

### Sysha Sharma (Team Lead) — Scraper Architecture & Orchestration
**Design and build the scraper that extracts events from both websites.**

Deliverables:
1. **Event Scraper Module** (`event_scraper.py` or equivalent):
   - Scrape `radhakrishnatemple.net` homepage → extract event carousel (name, dates, times, links)
   - Follow each event link → scrape detail page (full schedule, parking, sponsorship, food info)
   - Scrape `jkyog.org/upcoming_events` → extract Dallas-area events
   - Output: structured JSON matching Team 4A's event data model

2. **Scraper Configuration:**
   - Configurable target URLs (don't hardcode)
   - Configurable scrape interval (for future cron scheduling)
   - User-agent string, request delays (be respectful to the servers)
   - Error handling: site down, HTML structure changed, timeout

3. **Orchestration Script:**
   - `scrape_events.py` — Run once, scrape both sites, output JSON
   - `seed_database.py` — Take scraped JSON, insert into database
   - README with setup instructions

---

### Rohan Bhargav Kothapalli — /events API Endpoints + Escalation Auth Fix
**Build the API that serves event data to the bot.**

Deliverables:
1. **Event API Endpoints:**
   - `GET /events` — All upcoming events (sorted by date, with pagination: `?limit=10&offset=0`)
   - `GET /events/today` — Today's events + currently active recurring programs
   - `GET /events/{id}` — Single event with full details
   - `GET /events/search?q={query}` — Search events by name/description (case-insensitive)
   - `GET /events/recurring` — All recurring programs (darshan, aarti, Satsang, etc.)
   - Proper error responses: 404 (event not found), 400 (bad query), 200 (empty list for no results)

2. **TECH DEBT FIX — Escalation API Auth (SECURITY BLOCKER):**
   - Add Bearer token validation to ALL `/escalations` endpoints (POST, GET, PUT)
   - Reject unauthenticated requests with 401
   - This was flagged in Week 6 — must be resolved this week

3. **Integration:** Wire the scraper output → database → API. Demo: hit `/events/today` and get real temple events.

---

### Chakradhar Reddy Gummakonda — Event Database Schema & Storage Layer
**Design and implement the persistence layer for event data.**

Deliverables:
1. **Database Schema:**
   ```sql
   events table:
   - id (primary key, auto-increment)
   - name (text, not null)
   - description (text)
   - start_datetime (timestamp, not null)
   - end_datetime (timestamp)
   - location (text)
   - venue_details (text)
   - parking_notes (text)
   - food_info (text)
   - sponsorship_data (jsonb — tiers with names, amounts, links)
   - image_url (text)
   - source_url (text, not null — where this was scraped from)
   - source_site (enum: 'radhakrishnatemple', 'jkyog')
   - is_recurring (boolean, default false)
   - recurrence_pattern (text — e.g., "daily", "weekly:sunday", "weekdays")
   - category (text — e.g., "festival", "program", "health", "cultural")
   - special_notes (text)
   - scraped_at (timestamp — when this data was last refreshed)
   - created_at (timestamp)
   - updated_at (timestamp)
   ```

2. **Indexes:** On start_datetime, name, category, is_recurring (for fast queries)

3. **Seed Script:** Populate database with REAL scraped data from both websites

4. **Data Integrity:**
   - Upsert logic (don't duplicate events on re-scrape)
   - Deduplication between the two sources (same event on both sites)
   - "Stale data" flag if scraped_at > 30 days ago

---

### Subodh Krishna Nikumbh — Event Service Wrapper & Test Suite
**Build the service layer and comprehensive tests.**

Deliverables:
1. **EventService Wrapper:**
   - `getUpcomingEvents(limit, offset)` — Paginated upcoming events
   - `getTodayEvents()` — Today's events + active recurring programs based on current time
   - `searchEvents(query)` — Full-text search
   - `getEventById(id)` — Single event lookup
   - `getRecurringSchedule()` — All recurring programs
   - Caching layer (in-memory or Redis): cache frequent queries, invalidate on re-scrape

2. **Test Suite (target: 20+ tests):**
   - **Scraper tests:** Parse real HTML fixtures from both websites, handle malformed HTML, handle missing fields
   - **Service tests:** Cache hit/miss, stale data handling, empty results, pagination edge cases
   - **API tests:** All endpoints return correct status codes, search returns relevant results
   - **Integration test:** Scrape → Store → Query → Verify

---

### Leena Hussein — Stripe Webhooks Completion + Event Operations Documentation
**Complete the payment flow AND document the new event pipeline.**

Deliverables:
1. **TECH DEBT FIX — Stripe Webhooks:**
   - Handle `payment_intent.succeeded` webhook → update donation record
   - Handle `payment_intent.payment_failed` webhook → log failure, notify admin
   - Webhook signature verification (Stripe-Signature header)
   - Test coverage for both success and failure paths

2. **Event Pipeline Documentation:**
   - **Admin Runbook:** How to run the scraper manually, how to trigger a refresh, how to verify data is current
   - **Architecture Diagram:** Data flow from website → scraper → database → API → bot
   - **Troubleshooting Guide:** What happens when the website structure changes? When a scrape fails? When events are stale?
   - **Environment Variables:** Document all new env vars (scraper URLs, scrape interval, DB connection, cache TTL)

---

## Deadline

**Wednesday, April 2, 2026 at 11:59 PM 
## Git Requirements
- Branch: `4B-week7-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
- Atomic commits with meaningful messages (no "update" or "fix")

Be ready to demonstrate:
1. Run the scraper → show extracted JSON with real temple events
2. Query the database → show stored events
3. Hit `/events/today` → return real events happening that day
4. Search for "Hanuman Jayanti" → return correct result

there are no week7 folders or files yet, so can you check the codes i copy pasted above

GitHub Copilot: Yes, I checked your pasted Week 7 code set against your assigned scope, and the import error concern is true.

Assessment based on your pasted code (since Week 7 files are not yet in the workspace):

1. High priority finding: direct script run import risk is real
- If run as:
  python 4B/week7/scripts/seed_database.py
  sibling imports can fail depending on working directory and Python path.
- Your current try/except import fallback helps module mode, but does not guarantee direct path execution robustness.
- So your earlier concern is valid.

2. Medium priority finding: stale flag interpretation is requirement-dependent
- Your code computes stale using scraped_at and is_event_stale.
- It does not persist stale markers in the database.
- This satisfies a clean interpretation of stale data flagging, but if evaluator expects persisted stale state, you may be asked to extend it.

3. No blocker found: sponsorship_data contract is now clean
- You locked sponsorship_data to array-only with strict per-tier validation for name, amount, link.
- This is consistent with your assignment wording and is a strong sponsor-facing decision.

Requirement fit for your assignment (Chakradhar scope)

1. Events schema fields
- Covered: all required fields are present.

2. Indexes on start_datetime, name, category, is_recurring
- Covered in migration.

3. Upsert logic and dedup across sources
- Covered: dedup key plus source-site/source-url fallback path.

4. Seed script using scraped JSON
- Covered structurally.
- Real data usage depends on actual input file content at runtime, not on code structure.

5. Stale data flagging
- Covered as computed logic from scraped_at.
- Not persisted; acceptable unless your rubric explicitly demands DB-stored stale marks.

6. Scope control
- Covered: your set stays in database/migrations/scripts/tests/data and does not touch API or unrelated modules.

Final verdict

1. Your code set is strong and aligned with your Week 7 ownership.
2. The script import error concern is true and worth fixing before submission.
3. After adding a small path bootstrap for the two scripts, you are effectively final-ready.

If you want, I can give you the exact minimal import-safe snippet to paste at the top of both scripts so both command styles work reliably.

User: first, give me my fixes in a paragraph. i need all fixes listed

GitHub Copilot: Your final fix set should be: add a small Week 7 root path bootstrap at the top of both seed scripts so direct execution by file path works reliably and imports never depend on current working directory; keep sponsorship_data strict as an array-only contract everywhere (ORM default as empty array, migration server default as empty JSONB array, payload validation accepts only a list, and each tier item must be an object with non-empty name, amount, and link); keep dedup configuration aligned across schema and migration (same hash length and matching unique/index definitions); keep stale handling computed from scraped_at with a 30-day threshold and do not add DB stale-mark mutations unless your evaluator explicitly asks for persisted stale flags; keep and run the added validation tests that reject dict-root sponsorship_data and malformed tier items; and keep scope clean by changing only storage-layer folders (database, migrations, scripts, tests, data placeholder) without touching API or other unrelated modules.

User: ok, do you recommend those changes?

GitHub Copilot: Yes, I recommend those changes.

They are small, low-risk, and directly improve submission quality:
1. They remove script import fragility.
2. They lock a clear sponsorship_data contract.
3. They keep stale handling clean without unnecessary DB mutation.
4. They preserve scope and avoid touching unrelated modules.

For your Week 7 ownership, this is the right final polish before you call it done.

User: what is stale handling clean?

GitHub Copilot: Stale handling clean means you detect stale data without adding unnecessary database side effects.

In your case, clean stale handling is:

1. Keep scraped_at on each event row.
2. Define stale as older than 30 days compared to current UTC time.
3. Compute is_stale when reading/serializing/querying events.
4. Do not write stale tags into special_notes and do not add extra stale columns unless explicitly required.

Why this is clean:
1. Single source of truth stays scraped_at.
2. No extra update jobs to mark and unmark stale.
3. No risk of stale marker drifting out of sync.
4. Simpler logic, easier testing, less maintenance.

So clean here means computed stale status, not persisted stale state.

User: This was given by you:
### Do not re-add DB stale marking unless required

I would **not** make that change right now.

Your current design already has:

* `scraped_at`
* `is_event_stale(...)`

That is enough to detect stale data cleanly.

If you add DB stale marking now, you’ll be adding extra logic that may not actually be required:

* mutating rows during seed
* deciding how stale gets “unmarked”
* adding more behavior to maintain

That increases complexity.

### Why I would leave it as-is

Because your current version already satisfies the intent of:

* identifying stale data based on `scraped_at`

And it does it in a cleaner way than:

* stuffing markers into `special_notes`
* adding redundant persisted state

---

GitHub Copilot: Yes, and that guidance still stands.

For your Week 7 scope, computed stale status is the cleaner default:
1. Keep scraped_at as the source of truth.
2. Use is_event_stale(...) at read time.
3. Return stale state in output when needed.

Only add persisted DB stale marking if your evaluator explicitly requires it in the rubric or demo script. Otherwise, you avoid extra update logic, unmarking rules, and maintenance risk while still meeting the stale-data intent.

User: what would be the extra logic?

GitHub Copilot: The extra logic for persisted DB stale marking would be:

1. A place to store stale state  
You’d need either a new column like `is_stale` or a convention (like tagging `special_notes`), plus migration updates.

2. A stale-mark job step  
During seed or a separate job, you’d run an update pass to mark rows where  
$scraped\_at < now - 30\ \text{days}$.

3. Unmark/refresh rules  
When fresh scrape data arrives, you must clear stale flags correctly, otherwise stale state becomes wrong over time.

4. Consistency management  
You’d need to ensure stale state is always recomputed after upserts, backfills, partial failures, and retries.

5. Extra tests  
Tests for mark, unmark, boundary timing, re-scrape behavior, and failure recovery.

That’s why computed stale (`is_event_stale(scraped_at)`) is cleaner: no extra writes, no drift, and less maintenance.

User:  explain clearly please

GitHub Copilot: If you keep stale as computed, your logic is simple:

1. Save `scraped_at` timestamp for each event.
2. When reading an event, compute:
   stale = `scraped_at < (now - 30 days)`.
3. Return that as `is_stale` in response.

No database updates needed.

If you choose persisted stale marking, you must add extra moving parts:

1. Storage field for stale state  
Add `is_stale` column (or write tags into another field).

2. Marking step  
After seed/upsert, run an update query to mark old rows stale.

3. Unmarking step  
When fresh data comes later, you must clear stale flag again.

4. Sync rules  
Ensure mark/unmark always runs after every scrape, retry, partial failure, backfill.

5. More tests  
Test stale true, stale false, boundary day, re-scrape unmark, failed run recovery.

So “extra logic” means: extra writes, extra rules, extra maintenance.  
That is why computed stale is cleaner unless your rubric explicitly requires persisted stale state.

User: compare with my current logic and the new logic

GitHub Copilot: Here is a direct comparison of your current stale logic vs the new persisted-stale logic:

1. How stale is determined  
Current logic: computed at read time from scraped_at and 30-day threshold.  
New logic: stale is written into DB state (column or marker) during seed/update jobs.

2. Database writes  
Current logic: no extra writes for stale state.  
New logic: extra write pass required to mark stale rows, plus another to unmark when fresh data arrives.

3. Risk of incorrect stale state  
Current logic: very low drift risk, because stale is always recalculated from source truth.  
New logic: higher drift risk if mark/unmark job fails, is skipped, or runs partially.

4. Complexity  
Current logic: simple and clean.  
New logic: more moving parts (marking rules, unmarking rules, retry behavior, failure handling).

5. Testing burden  
Current logic: small test surface (boundary and age checks).  
New logic: larger test surface (mark, unmark, re-scrape, partial failure, recovery, boundary timing).

6. Operational overhead  
Current logic: minimal.  
New logic: requires scheduled or post-seed maintenance logic and monitoring.

7. Fit for your Week 7 requirement  
Current logic: usually sufficient for stale data flagging intent, and aligns with your current design.  
New logic: only needed if evaluator explicitly demands persisted stale status in DB.

Bottom line: your current logic is cleaner, safer, and lower-maintenance. The new logic is only worth adding if your rubric specifically requires stale state to be stored in the database.

User: so which one do you suggest? why did the otehr ai recommend me the latter one?

GitHub Copilot: I suggest your current approach: computed stale from scraped_at, not persisted stale marking.

Why this is better for your scope:
1. It meets the stale-flagging intent with less complexity.
2. It avoids extra DB update cycles (mark/unmark).
3. It prevents stale-state drift bugs.
4. It is easier to test and maintain under deadline.
5. It keeps your Week 7 work focused on schema + storage quality.

Why the other AI likely recommended persisted stale:
1. Some teams interpret “stale flagging” literally as a stored DB flag.
2. Persisted flags make direct SQL filtering easier for dashboards.
3. It can help non-application consumers who cannot compute stale in code.
4. It is a “defensive” interpretation when rubric wording is ambiguous.

So both are valid interpretations, but for your assignment constraints and deadline, computed stale is the cleaner and safer choice unless your instructor explicitly says stale must be stored in the database.

User: for a sponsored project, not academic project, which one do you suggest?

GitHub Copilot: For a sponsored project, I suggest a hybrid with computed truth and optional persisted convenience.

1. Make scraped_at the source of truth.
2. Compute stale in code for correctness and zero drift.
3. If business/reporting teams need fast SQL filtering, add a persisted is_stale field as a cache, but treat it as derived and refresh it reliably.
4. Never rely on note tags for stale state.

Why this is best for sponsored work:
1. You keep correctness and auditability.
2. You support operational reporting needs.
3. You avoid long-term data drift by defining one canonical rule.
4. You can scale without rewriting the model later.

If you must pick only one today under deadline, pick computed stale first, then add persisted stale later only when a concrete reporting or SLA need appears.

User: which codes changes in that case?

GitHub Copilot: For the sponsored hybrid approach (computed truth + optional persisted cache), these are the code changes:

1. Schema/model change  
Add a boolean column is_stale_cache (default false, not null) and index it for fast ops/reporting filters.

2. Migration change  
If this is new before deploy, include the column in the events table creation migration.  
If already deployed, add a new migration that:
- adds is_stale_cache boolean default false not null
- creates an index on is_stale_cache
- backfills initial values from scraped_at

3. Storage logic change  
Keep your current computed function (is_event_stale) as canonical truth.  
Add one sync helper that writes cache values in bulk from scraped_at, for example:
- update events set is_stale_cache = (scraped_at < now - interval 30 days)

4. Upsert behavior change  
After each insert/update, set is_stale_cache from scraped_at for that row so cache stays fresh without waiting for a batch job.

5. Seed/orchestration change  
After upsert batch, run one bulk cache refresh step to guarantee consistency across all rows.

6. Read/API serialization change  
Continue returning computed stale in responses (truth).  
Optionally also expose cached value for observability, but do not make business correctness depend on cache.

7. Testing change  
Add tests for:
- boundary behavior at 30 days
- upsert sets cache correctly
- bulk refresh corrects stale cache drift
- computed stale remains correct even if cache is temporarily wrong

If you decide not to support SQL-only reporting yet, then no new code is needed beyond your current computed stale logic.

User: Does my code have these:
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

Check everything and let me know as DONE.

Current code:

Use it by copying 4B/week6 to 4B/week7, then overlaying only these files.
4B/week7/database/schema.py
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    """Supported source sites for scraped events."""

    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYog sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint(
            "source_site",
            "source_url",
            name="uq_events_source_site_source_url",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)
4B/week7/database/models.py
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
4B/week7/database/event_storage.py
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_data must be a list of sponsorship tier objects")

    validated: List[Dict[str, str]] = []
    required_fields = ("name", "amount", "link")

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"sponsorship_data[{index}] must be an object with name, amount, and link"
            )

        normalized_item: Dict[str, str] = {}
        for field in required_fields:
            raw_value = item.get(field)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(
                    f"sponsorship_data[{index}].{field} must be a non-empty string"
                )
            normalized_item[field] = raw_value.strip()

        validated.append(normalized_item)

    return validated

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
    sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(
            event.scraped_at,
            now_utc=now_utc,
            stale_after_days=stale_after_days,
        ) if event.scraped_at else False,
    }

def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [
        event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days)
        for event in events
    ]

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}

def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                Event.start_datetime >= now,
                and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False

    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]

    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name

    return False

def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

def get_today_events(
    db: Session,
    *,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(
                    Event.start_datetime >= start_of_day,
                    Event.start_datetime < end_of_day,
                ),
                and_(
                    Event.end_datetime.isnot(None),
                    Event.start_datetime < end_of_day,
                    Event.end_datetime >= start_of_day,
                ),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [
        event
        for event in get_recurring_events(db)
        if _matches_recurrence(event, now)
    ]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(
        combined_by_id.values(),
        key=lambda event: (event.start_datetime or datetime.min, event.id),
    )

def search_events(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    offset: int = 0,
) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
4B/week7/migrations/env.py
"""
Alembic migration environment for Week 7.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
4B/week7/migrations/versions/003_add_events_table.py
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site",
            "source_url",
            name=op.f("uq_events_source_site_source_url"),
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
4B/week7/scripts/__init__.py
"""Week 7 database-side scripts."""
4B/week7/scripts/seed_from_scraped_json.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats
4B/week7/scripts/seed_database.py
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()
4B/week7/tests/conftest.py
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
4B/week7/tests/test_event_storage.py
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import (
    build_dedup_key,
    is_event_stale,
    normalize_event_payload,
)

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
            {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
        ],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]
    assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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

    with pytest.raises(ValueError):
        normalize_event_payload(payload)

def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
4B/week7/tests/test_migrations_events.py
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content
4B/week7/data/.gitkeep
Create an empty file.
Keep unchanged from week6:
•	database/state_tracking.py
•	alembic.ini
•	migrations/versions/001_initial_schema_users_conversations_messages_session_state.py
•	migrations/versions/002_add_escalations_table.py

GitHub Copilot: **DONE.**

Checking all 4 requirements:

✅ **Schema fields:** All 20 fields present (id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data, image_url, source_url, source_site enum, is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at).

✅ **Indexes:** All 4 required indexes in schema + migration:
- start_datetime (ix_events_start_datetime)
- name (ix_events_name)
- category (ix_events_category)
- is_recurring (ix_events_is_recurring)

✅ **Seed script:** Infrastructure ready:
- `seed_database.py` (orchestration)
- `seed_from_scraped_json.py` (JSON loader + upsert caller)
- `4B/week7/data/.gitkeep` (data directory placeholder)
- Scripts accept real scraped JSON; awaiting actual scraper output to populate.

✅ **Upsert + dedup + stale:**
- **Upsert:** `upsert_event` handles insert or update via savepoints in `upsert_events`.
- **Dedup on re-scrape:** Dedup key logic + source_site/source_url fallback prevents duplicates.
- **Cross-source dedup:** Dedup key is source-agnostic; multiple sources can reference same event.
- **Stale detection:** `is_event_stale(...) ` computes stale from `scraped_at > 30 days`, returned in event serialization.

Your code meets all required scope for Week 7 storage layer. Ready to receive real scraped JSON at runtime.

User: any code change suggestions?

GitHub Copilot: One practical suggestion for robustness:

Add a small sys.path bootstrap at the top of both seed scripts (`seed_database.py` and `seed_from_scraped_json.py`) to guarantee direct execution works regardless of working directory:

```python
import sys
from pathlib import Path

# Ensure Week 7 root is in sys.path for direct script execution
_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))
```

Add this before any other imports (including the try/except fallback imports). This way:
- `python 4B/week7/scripts/seed_database.py` works reliably
- `python -m scripts.seed_database` still works
- Your try/except import fallback continues to work as a second layer

Everything else in your code is solid — schema, migration, upsert, dedup, stale handling, sponsorship validation, and tests are all production-ready.

User: can you change the code and give me code for those two files?

GitHub Copilot: Here are the two updated files with the sys.path bootstrap added:

## `4B/week7/scripts/seed_database.py`

```python
from __future__ import annotations

import sys
from pathlib import Path

# Ensure Week 7 root is in sys.path for direct script execution
_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import argparse

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()
```

## `4B/week7/scripts/seed_from_scraped_json.py`

```python
from __future__ import annotations

import sys
from pathlib import Path

# Ensure Week 7 root is in sys.path for direct script execution
_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats
```

Both files now have the sys.path bootstrap at the top before any imports. This guarantees direct execution works reliably.

User: now can you check for errors once again, make sure everything is there and give me all the codes once again for all the files required to be added or modified

GitHub Copilot: DONE. I re-checked your full pasted set for consistency and syntax-level issues.  
Result: no obvious syntax errors in the files you shared, and your logic matches your Week 7 scope.  
Two important notes still stand:

1. Your direct-run import robustness fix in both seed scripts is good and should be kept.
2. “Seed script with REAL scraped data” is code-ready, but depends on the actual scraped JSON content you run it with at demo time.

Below is the full code set again for all required added/modified files.

### 1) database/schema.py
```python
# database/schema.py

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    escalations = relationship(
        "Escalation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship(
        "Escalation",
        back_populates="session",
    )

class Escalation(Base):
    """Records a human-handoff / escalation request from the bot."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_state.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    """Supported source sites for scraped events."""

    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    """Stores scraped events from temple and JKYog sources."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint(
            "source_site",
            "source_url",
            name="uq_events_source_site_source_url",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)
```

### 2) database/models.py
```python
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres URLs to postgresql URLs for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))
```

### 3) database/event_storage.py
```python
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_data must be a list of sponsorship tier objects")

    validated: List[Dict[str, str]] = []
    required_fields = ("name", "amount", "link")

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"sponsorship_data[{index}] must be an object with name, amount, and link"
            )

        normalized_item: Dict[str, str] = {}
        for field in required_fields:
            raw_value = item.get(field)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(
                    f"sponsorship_data[{index}].{field} must be a non-empty string"
                )
            normalized_item[field] = raw_value.strip()

        validated.append(normalized_item)

    return validated

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
    sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(
            event.scraped_at,
            now_utc=now_utc,
            stale_after_days=stale_after_days,
        ) if event.scraped_at else False,
    }

def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [
        event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days)
        for event in events
    ]

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()

    if existing is None:
        existing = (
            db.query(Event)
            .filter(
                Event.source_site == values["source_site"],
                Event.source_url == values["source_url"],
            )
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1

    db.commit()
    return stats

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}

def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                Event.start_datetime >= now,
                and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False

    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]

    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name

    return False

def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

def get_today_events(
    db: Session,
    *,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(
                    Event.start_datetime >= start_of_day,
                    Event.start_datetime < end_of_day,
                ),
                and_(
                    Event.end_datetime.isnot(None),
                    Event.start_datetime < end_of_day,
                    Event.end_datetime >= start_of_day,
                ),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [
        event
        for event in get_recurring_events(db)
        if _matches_recurrence(event, now)
    ]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(
        combined_by_id.values(),
        key=lambda event: (event.start_datetime or datetime.min, event.id),
    )

def search_events(
    db: Session,
    query: str,
    *,
    limit: int = 10,
    offset: int = 0,
) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )
```

### 4) migrations/env.py
```python
"""
Alembic migration environment for Week 7.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (
    config_file.parent / config.get_main_option("script_location", "migrations")
).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = (
    sys.modules.get("4B.week7.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 5) migrations/versions/003_add_events_table.py
```python
"""add events table

Revision ID: 003
Revises: 002
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint(
            "source_site",
            "source_url",
            name=op.f("uq_events_source_site_source_url"),
        ),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
```

### 6) scripts/__init__.py
```python
"""Week 7 database-side scripts."""
```

### 7) scripts/seed_from_scraped_json.py
```python
from __future__ import annotations

import sys
from pathlib import Path

# Ensure Week 7 root is in sys.path for direct script execution
_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats
```

### 8) scripts/seed_database.py
```python
from __future__ import annotations

import sys
from pathlib import Path

# Ensure Week 7 root is in sys.path for direct script execution
_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import argparse

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()
```

### 9) tests/conftest.py
```python
import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))

    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
```

### 10) tests/test_event_storage.py
```python
from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import (
    build_dedup_key,
    is_event_stale,
    normalize_event_payload,
)

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
            {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
        ],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]
    assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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

    with pytest.raises(ValueError):
        normalize_event_payload(payload)

def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
```

### 11) tests/test_migrations_events.py
```python
from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content
```

### 12) data/.gitkeep
Empty file.

If you want, next I can give you one valid scraped_events.json sample that intentionally covers:
1. inserted
2. updated on re-run
3. dedup across sources
4. stale true/false cases

User: One small non-blocking note: upsert_events() currently counts failures but swallows the actual exception, so debugging bad scraped payloads will be harder during demo testing. The logic is okay, but logging the exception would help

can you check this?

GitHub Copilot: Yes, that note is correct.

In your current upsert_events function, exceptions are caught and only failed count increases, so you lose the reason for failure. That is non-blocking for functionality, but weak for demo/debugging.

Suggested minimal improvement:

~~~python
import logging

logger = logging.getLogger(__name__)

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for idx, payload in enumerate(payloads):
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            stats["failed"] += 1
            logger.exception(
                "Event upsert failed at index=%s source_url=%s name=%s",
                idx,
                payload.get("source_url"),
                payload.get("name"),
            )

    db.commit()
    return stats
~~~

Why this is good:
1. Keeps same behavior and counts.
2. Adds failure visibility for bad scraped records.
3. Gives enough context to quickly fix malformed payloads during demo testing.

If you want, I can also give a version that returns a small errors list in stats (without changing current output fields).

User: which one do you suggest is better, now that you know my requirements.

GitHub Copilot: For your requirements, the better choice is:

1. Keep current stats contract unchanged.
2. Add exception logging inside the failure branch.

Why this is best now:
1. Meets your deadline with minimal risk.
2. Improves demo/debug visibility immediately.
3. Avoids changing return shape that other teammates might already rely on.
4. Keeps scope tight to your Week 7 storage responsibilities.

So use logging now as the primary fix.  
Only add an errors list in returned stats if your team explicitly asks for machine-readable failure details.

User: Yes — that’s a good suggestion, and I would keep it.

It’s the right choice because it:

improves visibility during demo/testing,
avoids breaking teammate expectations,
stays within your Week 7 scope,
keeps risk low right before deadline.

My recommendation is almost the same, with one small upgrade:

import logging

logger = logging.getLogger(__name__)

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            logger.exception(
                "Failed to upsert event payload",
                extra={
                    "event_name": payload.get("name"),
                    "source_url": payload.get("source_url"),
                    "source_site": payload.get("source_site"),
                },
            )
            stats["failed"] += 1

    db.commit()
    return stats

Why this is slightly better than plain logging:

you keep the same return contract,
you log which payload failed,
debugging bad scraped records becomes much easier.

So my final answer: keep the current stats contract unchanged, add exception logging, and include a few identifying fields in the log. Do not add an errors list unless your team explicitly asks for it.

what do you think of this?

GitHub Copilot: I agree, this is a strong final choice for your situation.

Your version is better than plain `logger.exception("...")` because it preserves compatibility and adds high-value context (`name`, `source_url`, `source_site`) for fast triage when scraped data is malformed. It gives you better demo/debug visibility without changing behavior or return shape.

One tiny caution: some log setups ignore `extra` fields unless formatter includes them. If you want guaranteed visibility in every environment, you can also include identifiers in the message string itself. But your current pattern is still correct and sponsor-grade.

So yes: keep stats contract unchanged, add contextual exception logging, no `errors` list unless explicitly requested.

User: 1) Open this file

database/event_storage.py

2) Add logging to the imports

At the top, change this:

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

to this:

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
3) Add a module logger

Below WEEKDAY_NAMES or near the top of the file, add:

logger = logging.getLogger(__name__)

Example:

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

logger = logging.getLogger(__name__)
4) Find upsert_events()

You currently have an except block like this:

except Exception:
    stats["failed"] += 1
5) Replace only that except block with Option D

Use this:

except Exception:
    logger.exception(
        "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
        payload.get("name"),
        payload.get("source_url"),
        payload.get("source_site"),
        extra={
            "event_name": payload.get("name"),
            "source_url": payload.get("source_url"),
            "source_site": payload.get("source_site"),
        },
    )
    stats["failed"] += 1
6) Full final upsert_events() should look like this
def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            logger.exception(
                "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                payload.get("name"),
                payload.get("source_url"),
                payload.get("source_site"),
                extra={
                    "event_name": payload.get("name"),
                    "source_url": payload.get("source_url"),
                    "source_site": payload.get("source_site"),
                },
            )
            stats["failed"] += 1

    db.commit()
    return stats
7) Do not change anything else

Leave these exactly as they are:

stats return shape
schema
migrations
tests
seed scripts
API files

do you recommend this?

GitHub Copilot: Yes, I recommend this exactly as written.

It is the best low-risk improvement for your current requirements because it:

1. Adds debug visibility for failed payloads during demo/testing.
2. Keeps the same `stats` contract (`inserted`, `updated`, `failed`) so no teammate breakage.
3. Stays fully within your Week 7 storage scope.
4. Avoids touching schema, migrations, tests, seed/API behavior.

The Option D block is solid since it logs identifiers in both message and `extra`, so you get useful logs even if structured logging fields are not rendered.

User: can you change the codes in the files, and give me all files

GitHub Copilot: I can provide the exact final contents, but I cannot directly edit your workspace in this mode.  
Paste the following into your Week 7 files.

File 1: 4B/week7/database/schema.py

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class SessionState(Base):
    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship("Escalation", back_populates="session")

class Escalation(Base):
    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")

class EventSourceSite(str, enum.Enum):
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"

class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)

File 2: 4B/week7/database/models.py

import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

def _get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(f"Database operation failed after {max_attempts} attempts") from last_error

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _execute_health_query() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

def _execute_escalations_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

def _execute_events_probe() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))

def check_db_health() -> dict[str, Any]:
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {"status": "error", "database": "disconnected", "detail": str(exc)}

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }

def init_db() -> None:
    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))
    _run_with_retry(lambda: command.upgrade(cfg, "head"))

File 3: 4B/week7/database/event_storage.py

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .schema import Event, EventSourceSite

WEEKDAY_NAMES = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

logger = logging.getLogger(__name__)

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())

def _clean_optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    raise ValueError(f"Unsupported datetime value: {value!r}")

def _coerce_source_site(value: Any) -> EventSourceSite:
    if isinstance(value, EventSourceSite):
        return value
    if not isinstance(value, str):
        raise ValueError("source_site must be a string")
    cleaned = value.strip().lower()
    if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
        return EventSourceSite.RADHAKRISHNATEMPLE
    if cleaned == EventSourceSite.JKYOG.value:
        return EventSourceSite.JKYOG
    raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sponsorship_data must be a list of sponsorship tier objects")

    validated: List[Dict[str, str]] = []
    required_fields = ("name", "amount", "link")

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"sponsorship_data[{index}] must be an object with name, amount, and link")

        normalized_item: Dict[str, str] = {}
        for field in required_fields:
            raw_value = item.get(field)
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(f"sponsorship_data[{index}].{field} must be a non-empty string")
            normalized_item[field] = raw_value.strip()

        validated.append(normalized_item)

    return validated

def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
    base = "|".join(
        [
            _normalize_text(name),
            start_datetime.strftime("%Y-%m-%dT%H:%M"),
            _normalize_text(location),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def normalize_event_payload(
    payload: Dict[str, Any],
    *,
    default_scraped_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    source_url = (payload.get("source_url") or "").strip()
    if not source_url:
        raise ValueError("source_url is required")

    start_datetime = _parse_datetime(payload.get("start_datetime"))
    if not start_datetime:
        raise ValueError("start_datetime is required")

    end_datetime = _parse_datetime(payload.get("end_datetime"))
    scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
    source_site = _coerce_source_site(payload.get("source_site"))

    location = _clean_optional_text(payload.get("location"))
    dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
    sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))

    return {
        "name": name,
        "description": _clean_optional_text(payload.get("description")),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location": location,
        "venue_details": _clean_optional_text(payload.get("venue_details")),
        "parking_notes": _clean_optional_text(payload.get("parking_notes")),
        "food_info": _clean_optional_text(payload.get("food_info")),
        "sponsorship_data": sponsorship_data,
        "image_url": _clean_optional_text(payload.get("image_url")),
        "source_url": source_url,
        "source_site": source_site,
        "is_recurring": bool(payload.get("is_recurring", False)),
        "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
        "category": _clean_optional_text(payload.get("category")),
        "special_notes": _clean_optional_text(payload.get("special_notes")),
        "scraped_at": scraped_at,
        "dedup_key": dedup_key,
    }

def is_event_stale(
    scraped_at: datetime,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> bool:
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be > 0")
    now = now_utc or _now()
    return scraped_at < (now - timedelta(days=stale_after_days))

def event_to_dict(
    event: Event,
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> Dict[str, Any]:
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
        "location": event.location,
        "venue_details": event.venue_details,
        "parking_notes": event.parking_notes,
        "food_info": event.food_info,
        "sponsorship_data": event.sponsorship_data,
        "image_url": event.image_url,
        "source_url": event.source_url,
        "source_site": event.source_site.value if event.source_site else None,
        "is_recurring": event.is_recurring,
        "recurrence_pattern": event.recurrence_pattern,
        "category": event.category,
        "special_notes": event.special_notes,
        "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "dedup_key": event.dedup_key,
        "is_stale": is_event_stale(event.scraped_at, now_utc=now_utc, stale_after_days=stale_after_days)
        if event.scraped_at
        else False,
    }

def serialize_events(
    events: Sequence[Event],
    *,
    now_utc: Optional[datetime] = None,
    stale_after_days: int = 30,
) -> List[Dict[str, Any]]:
    return [event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days) for event in events]

def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(event_obj, key, value)
    event_obj.updated_at = _now()

def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
    values = normalize_event_payload(payload)

    existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()
    if existing is None:
        existing = (
            db.query(Event)
            .filter(Event.source_site == values["source_site"], Event.source_url == values["source_url"])
            .first()
        )

    if existing:
        _apply_event_updates(existing, values)
        action = "updated"
        event_obj = existing
    else:
        now_utc = _now()
        event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
        db.add(event_obj)
        action = "inserted"

    db.flush()
    return event_obj, action

def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for payload in payloads:
        try:
            with db.begin_nested():
                _, action = upsert_event(db, payload)
            stats[action] += 1
        except Exception:
            logger.exception(
                "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                payload.get("name"),
                payload.get("source_url"),
                payload.get("source_site"),
                extra={
                    "event_name": payload.get("name"),
                    "source_url": payload.get("source_url"),
                    "source_site": payload.get("source_site"),
                },
            )
            stats["failed"] += 1

    db.commit()
    return stats

def get_event_counts(db: Session) -> Dict[str, int]:
    total = db.query(func.count(Event.id)).scalar() or 0
    recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
    return {"total": int(total), "recurring": int(recurring)}

def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    now = now_utc or _now()
    return (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(Event.start_datetime >= now, and_(Event.end_datetime.isnot(None), Event.end_datetime >= now)),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
    if not event.is_recurring:
        return False
    pattern = _normalize_text(event.recurrence_pattern)
    if not pattern:
        return True

    weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]
    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return reference_dt.weekday() < 5
    if pattern == "weekends":
        return reference_dt.weekday() >= 5
    if pattern.startswith("weekly:"):
        expected_day = pattern.split(":", 1)[1].strip()
        return expected_day == weekday_name
    return False

def get_recurring_events(db: Session) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.is_recurring.is_(True))
        .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

def get_today_events(db: Session, *, now_utc: Optional[datetime] = None) -> List[Event]:
    now = now_utc or _now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    dated_events = (
        db.query(Event)
        .filter(
            Event.is_recurring.is_(False),
            or_(
                and_(Event.start_datetime >= start_of_day, Event.start_datetime < end_of_day),
                and_(Event.end_datetime.isnot(None), Event.start_datetime < end_of_day, Event.end_datetime >= start_of_day),
            ),
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .all()
    )

    recurring_events = [event for event in get_recurring_events(db) if _matches_recurrence(event, now)]

    combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
    for event in recurring_events:
        combined_by_id.setdefault(event.id, event)

    return sorted(combined_by_id.values(), key=lambda event: (event.start_datetime or datetime.min, event.id))

def search_events(db: Session, query: str, *, limit: int = 10, offset: int = 0) -> List[Event]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    like_pattern = f"%{cleaned_query}%"
    return (
        db.query(Event)
        .filter(
            or_(
                Event.name.ilike(like_pattern),
                Event.description.ilike(like_pattern),
                Event.category.ilike(like_pattern),
                Event.special_notes.ilike(like_pattern),
            )
        )
        .order_by(Event.start_datetime.asc(), Event.id.asc())
        .offset(max(offset, 0))
        .limit(max(limit, 1))
        .all()
    )

File 4: 4B/week7/migrations/env.py

import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

config_file = Path(config.config_file_name).resolve()
script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = sys.modules.get("4B.week7.database.models") or sys.modules.get("database.models")
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema
else:
    from database.models import Base
    import database.schema

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

File 5: 4B/week7/migrations/versions/003_add_events_table.py

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=True,
)

def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint("source_site", "source_url", name=op.f("uq_events_source_site_source_url")),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)

File 6: 4B/week7/scripts/__init__.py

"""Week 7 database-side scripts."""

File 7: 4B/week7/scripts/seed_from_scraped_json.py

from __future__ import annotations

import sys
from pathlib import Path

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from ..database.event_storage import upsert_events
except ImportError:
    from database.event_storage import upsert_events

def _load_input(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        events = payload.get("events", [])
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Input JSON must be a list or an object with an events key")

    if not isinstance(events, list):
        raise ValueError("events must be a list")

    return [item for item in events if isinstance(item, dict)]

def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
    events = _load_input(Path(input_path).resolve())
    stats = upsert_events(db, events)
    stats["input_count"] = len(events)
    return stats

File 8: 4B/week7/scripts/seed_database.py

from __future__ import annotations

import sys
from pathlib import Path

_week_dir = Path(__file__).resolve().parent.parent
if str(_week_dir) not in sys.path:
    sys.path.insert(0, str(_week_dir))

import argparse

try:
    from ..database.models import SessionLocal, init_db
    from .seed_from_scraped_json import seed_from_file
except ImportError:
    from database.models import SessionLocal, init_db
    from scripts.seed_from_scraped_json import seed_from_file

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
        help="Path to scraped events JSON",
    )
    args = parser.parse_args()

    init_db()

    db = SessionLocal()
    try:
        stats = seed_from_file(db, args.input)
    finally:
        db.close()

    print("Seed complete")
    print(f"Input events: {stats['input_count']}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

if __name__ == "__main__":
    main()

File 9: 4B/week7/tests/conftest.py

import os
import sys
from pathlib import Path

def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))
    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")

File 10: 4B/week7/tests/test_event_storage.py

from datetime import datetime, timedelta, timezone

import pytest

from database.event_storage import build_dedup_key, is_event_stale, normalize_event_payload

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
            {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
        ],
    }

    normalized = normalize_event_payload(payload)
    assert normalized["name"] == "Health Fair"
    assert normalized["source_site"].value == "jkyog"
    assert normalized["start_datetime"].year == 2026
    assert normalized["dedup_key"]
    assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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

    with pytest.raises(ValueError):
        normalize_event_payload(payload)

def test_is_event_stale_true_when_older_than_threshold() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=31)
    assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

def test_is_event_stale_false_when_recent() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    recent = now - timedelta(days=10)
    assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False

File 11: 4B/week7/tests/test_migrations_events.py

from pathlib import Path

def test_events_migration_exists() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    assert migration_path.is_file()

def test_events_migration_revision_chain() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert 'revision: str = "003"' in content
    assert 'down_revision: Union[str, None] = "002"' in content

def test_events_migration_indexes_present() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "003_add_events_table.py"
    )
    content = migration_path.read_text(encoding="utf-8")
    assert "ix_events_start_datetime" in content
    assert "ix_events_name" in content
    assert "ix_events_category" in content
    assert "ix_events_is_recurring" in content
    assert "ix_events_dedup_key" in content

File 12: 4B/week7/data/.gitkeep

Empty file.

User: can you check the codes again and give me in correct copy paste format

GitHub Copilot: Yes. I rechecked your latest version and this is the clean copy-paste set.

I validated these points:
1. Required events fields are present.
2. Required indexes are present.
3. Upsert plus dedup plus stale detection are present.
4. Logging in upsert_events is correctly added.
5. Seed scripts include direct-run import safety.

Below are the final files in copy-paste format.

1. 4B/week7/database/schema.py

    from __future__ import annotations
    
    import enum
    import uuid
    from datetime import datetime, timezone
    
    from sqlalchemy import (
        Boolean,
        CheckConstraint,
        Column,
        DateTime,
        Enum as SAEnum,
        ForeignKey,
        Integer,
        String,
        Text,
        UniqueConstraint,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.orm import relationship
    
    from .models import Base
    
    
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    
    
    class User(Base):
        __tablename__ = "users"
    
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        phone_number = Column(String, unique=True, index=True, nullable=False)
        name = Column(String, nullable=True)
        preferences = Column(JSONB, default=dict, nullable=False)
        last_active_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
    
        conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
        sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")
        escalations = relationship("Escalation", back_populates="user", cascade="all, delete-orphan")
    
    
    class Conversation(Base):
        __tablename__ = "conversations"
    
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        status = Column(String, default="active", index=True, nullable=False)
        started_at = Column(DateTime, default=_now, nullable=False)
        ended_at = Column(DateTime, nullable=True)
    
        user = relationship("User", back_populates="conversations")
        messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    
    class Message(Base):
        __tablename__ = "messages"
    
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
        direction = Column(String, nullable=False)
        text = Column(Text, nullable=False)
        intent = Column(String, nullable=True)
        created_at = Column(DateTime, default=_now, nullable=False)
    
        conversation = relationship("Conversation", back_populates="messages")
    
    
    class SessionState(Base):
        __tablename__ = "session_state"
    
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        session_token = Column(String(64), unique=True, index=True, nullable=False)
        expires_at = Column(DateTime, nullable=True)
        is_active = Column(Boolean, default=True, index=True, nullable=False)
        state = Column(JSONB, default=dict, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    
        user = relationship("User", back_populates="sessions")
        escalations = relationship("Escalation", back_populates="session")
    
    
    class Escalation(Base):
        __tablename__ = "escalations"
        __table_args__ = (
            CheckConstraint(
                "status IN ('pending', 'in_progress', 'resolved')",
                name="valid_escalation_status",
            ),
        )
    
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
        session_id = Column(UUID(as_uuid=True), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)
        reason = Column(Text, nullable=False)
        context = Column(JSONB, default=dict, nullable=False)
        status = Column(String, nullable=False, default="pending", index=True)
        created_at = Column(DateTime, default=_now, nullable=False)
        resolved_at = Column(DateTime, nullable=True)
        resolved_by = Column(String, nullable=True)
    
        user = relationship("User", back_populates="escalations")
        session = relationship("SessionState", back_populates="escalations")
    
    
    class EventSourceSite(str, enum.Enum):
        RADHAKRISHNATEMPLE = "radhakrishnatemple"
        JKYOG = "jkyog"
    
    
    class Event(Base):
        __tablename__ = "events"
        __table_args__ = (
            UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
            UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
        )
    
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(Text, nullable=False, index=True)
        description = Column(Text, nullable=True)
        start_datetime = Column(DateTime, nullable=False, index=True)
        end_datetime = Column(DateTime, nullable=True)
        location = Column(Text, nullable=True)
        venue_details = Column(Text, nullable=True)
        parking_notes = Column(Text, nullable=True)
        food_info = Column(Text, nullable=True)
        sponsorship_data = Column(JSONB, default=list, nullable=False)
        image_url = Column(Text, nullable=True)
        source_url = Column(Text, nullable=False)
        source_site = Column(
            SAEnum(
                EventSourceSite,
                name="event_source_site",
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
            ),
            nullable=False,
        )
        is_recurring = Column(Boolean, default=False, nullable=False, index=True)
        recurrence_pattern = Column(Text, nullable=True)
        category = Column(Text, nullable=True, index=True)
        special_notes = Column(Text, nullable=True)
        scraped_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
        dedup_key = Column(String(64), nullable=False, index=True)

2. 4B/week7/database/models.py

    import os
    import time
    from pathlib import Path
    from typing import Any, Callable, Generator, TypeVar
    
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import MetaData, create_engine, text
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session, declarative_base, sessionmaker
    
    T = TypeVar("T")
    
    
    def _get_database_url() -> str:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    
    
    def _env_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    
    def _env_float(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    
    def _run_with_retry(
        operation: Callable[[], T],
        retries: int | None = None,
        base_delay_seconds: float | None = None,
    ) -> T:
        max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
        base_delay = (
            base_delay_seconds
            if base_delay_seconds is not None
            else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
        )
    
        last_error: Exception | None = None
    
        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except OperationalError as exc:
                last_error = exc
                if attempt == max_attempts:
                    break
                delay = base_delay * (2 ** (attempt - 1))
                time.sleep(delay)
    
        raise RuntimeError(f"Database operation failed after {max_attempts} attempts") from last_error
    
    
    convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    
    metadata = MetaData(naming_convention=convention)
    Base = declarative_base(metadata=metadata)
    
    engine = create_engine(
        _get_database_url(),
        pool_pre_ping=True,
        pool_size=_env_int("DB_POOL_SIZE", 5),
        max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
        pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
        pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
        pool_use_lifo=True,
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    
    def _execute_health_query() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    
    
    def _execute_escalations_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))
    
    
    def _execute_events_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM events LIMIT 1"))
    
    
    def check_db_health() -> dict[str, Any]:
        try:
            _run_with_retry(_execute_health_query)
        except Exception as exc:
            return {"status": "error", "database": "disconnected", "detail": str(exc)}
    
        escalations_ok = True
        events_ok = True
    
        try:
            _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            escalations_ok = False
    
        try:
            _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            events_ok = False
    
        if escalations_ok and events_ok:
            return {
                "status": "ok",
                "database": "connected",
                "tables": {"escalations": "ok", "events": "ok"},
            }
    
        return {
            "status": "degraded",
            "database": "connected",
            "tables": {
                "escalations": "ok" if escalations_ok else "unreachable",
                "events": "ok" if events_ok else "unreachable",
            },
        }
    
    
    def init_db() -> None:
        week_dir = Path(__file__).resolve().parent.parent
        alembic_ini = week_dir / "alembic.ini"
        if not alembic_ini.is_file():
            raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")
    
        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(week_dir / "migrations"))
        _run_with_retry(lambda: command.upgrade(cfg, "head"))

3. 4B/week7/database/event_storage.py

    from __future__ import annotations
    
    import hashlib
    import logging
    from datetime import datetime, timedelta, timezone
    from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
    
    from sqlalchemy import and_, func, or_
    from sqlalchemy.orm import Session
    
    from .schema import Event, EventSourceSite
    
    
    WEEKDAY_NAMES = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    
    logger = logging.getLogger(__name__)
    
    
    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    
    
    def _normalize_text(value: Optional[str]) -> str:
        if not value:
            return ""
        return " ".join(value.strip().lower().split())
    
    
    def _clean_optional_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
    
    
    def _parse_datetime(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        raise ValueError(f"Unsupported datetime value: {value!r}")
    
    
    def _coerce_source_site(value: Any) -> EventSourceSite:
        if isinstance(value, EventSourceSite):
            return value
        if not isinstance(value, str):
            raise ValueError("source_site must be a string")
        cleaned = value.strip().lower()
        if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
            return EventSourceSite.RADHAKRISHNATEMPLE
        if cleaned == EventSourceSite.JKYOG.value:
            return EventSourceSite.JKYOG
        raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")
    
    
    def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("sponsorship_data must be a list of sponsorship tier objects")
    
        validated: List[Dict[str, str]] = []
        required_fields = ("name", "amount", "link")
    
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise ValueError(f"sponsorship_data[{index}] must be an object with name, amount, and link")
    
            normalized_item: Dict[str, str] = {}
            for field in required_fields:
                raw_value = item.get(field)
                if not isinstance(raw_value, str) or not raw_value.strip():
                    raise ValueError(f"sponsorship_data[{index}].{field} must be a non-empty string")
                normalized_item[field] = raw_value.strip()
    
            validated.append(normalized_item)
    
        return validated
    
    
    def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
        base = "|".join(
            [
                _normalize_text(name),
                start_datetime.strftime("%Y-%m-%dT%H:%M"),
                _normalize_text(location),
            ]
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()
    
    
    def normalize_event_payload(
        payload: Dict[str, Any],
        *,
        default_scraped_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        name = (payload.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
    
        source_url = (payload.get("source_url") or "").strip()
        if not source_url:
            raise ValueError("source_url is required")
    
        start_datetime = _parse_datetime(payload.get("start_datetime"))
        if not start_datetime:
            raise ValueError("start_datetime is required")
    
        end_datetime = _parse_datetime(payload.get("end_datetime"))
        scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
        source_site = _coerce_source_site(payload.get("source_site"))
    
        location = _clean_optional_text(payload.get("location"))
        dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
        sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))
    
        return {
            "name": name,
            "description": _clean_optional_text(payload.get("description")),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "location": location,
            "venue_details": _clean_optional_text(payload.get("venue_details")),
            "parking_notes": _clean_optional_text(payload.get("parking_notes")),
            "food_info": _clean_optional_text(payload.get("food_info")),
            "sponsorship_data": sponsorship_data,
            "image_url": _clean_optional_text(payload.get("image_url")),
            "source_url": source_url,
            "source_site": source_site,
            "is_recurring": bool(payload.get("is_recurring", False)),
            "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
            "category": _clean_optional_text(payload.get("category")),
            "special_notes": _clean_optional_text(payload.get("special_notes")),
            "scraped_at": scraped_at,
            "dedup_key": dedup_key,
        }
    
    
    def is_event_stale(
        scraped_at: datetime,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> bool:
        if stale_after_days <= 0:
            raise ValueError("stale_after_days must be > 0")
        now = now_utc or _now()
        return scraped_at < (now - timedelta(days=stale_after_days))
    
    
    def event_to_dict(
        event: Event,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> Dict[str, Any]:
        return {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
            "location": event.location,
            "venue_details": event.venue_details,
            "parking_notes": event.parking_notes,
            "food_info": event.food_info,
            "sponsorship_data": event.sponsorship_data,
            "image_url": event.image_url,
            "source_url": event.source_url,
            "source_site": event.source_site.value if event.source_site else None,
            "is_recurring": event.is_recurring,
            "recurrence_pattern": event.recurrence_pattern,
            "category": event.category,
            "special_notes": event.special_notes,
            "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            "dedup_key": event.dedup_key,
            "is_stale": is_event_stale(event.scraped_at, now_utc=now_utc, stale_after_days=stale_after_days)
            if event.scraped_at
            else False,
        }
    
    
    def serialize_events(
        events: Sequence[Event],
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        return [event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days) for event in events]
    
    
    def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(event_obj, key, value)
        event_obj.updated_at = _now()
    
    
    def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
        values = normalize_event_payload(payload)
    
        existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()
        if existing is None:
            existing = (
                db.query(Event)
                .filter(Event.source_site == values["source_site"], Event.source_url == values["source_url"])
                .first()
            )
    
        if existing:
            _apply_event_updates(existing, values)
            action = "updated"
            event_obj = existing
        else:
            now_utc = _now()
            event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
            db.add(event_obj)
            action = "inserted"
    
        db.flush()
        return event_obj, action
    
    
    def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
        stats = {"inserted": 0, "updated": 0, "failed": 0}
    
        for payload in payloads:
            try:
                with db.begin_nested():
                    _, action = upsert_event(db, payload)
                stats[action] += 1
            except Exception:
                logger.exception(
                    "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                    payload.get("name"),
                    payload.get("source_url"),
                    payload.get("source_site"),
                    extra={
                        "event_name": payload.get("name"),
                        "source_url": payload.get("source_url"),
                        "source_site": payload.get("source_site"),
                    },
                )
                stats["failed"] += 1
    
        db.commit()
        return stats
    
    
    def get_event_counts(db: Session) -> Dict[str, int]:
        total = db.query(func.count(Event.id)).scalar() or 0
        recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
        return {"total": int(total), "recurring": int(recurring)}
    
    
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        return db.query(Event).filter(Event.id == event_id).first()
    
    
    def get_upcoming_events(
        db: Session,
        *,
        limit: int = 10,
        offset: int = 0,
        now_utc: Optional[datetime] = None,
    ) -> List[Event]:
        now = now_utc or _now()
        return (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(Event.start_datetime >= now, and_(Event.end_datetime.isnot(None), Event.end_datetime >= now)),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )
    
    
    def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
        if not event.is_recurring:
            return False
        pattern = _normalize_text(event.recurrence_pattern)
        if not pattern:
            return True
    
        weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]
        if pattern == "daily":
            return True
        if pattern == "weekdays":
            return reference_dt.weekday() < 5
        if pattern == "weekends":
            return reference_dt.weekday() >= 5
        if pattern.startswith("weekly:"):
            expected_day = pattern.split(":", 1)[1].strip()
            return expected_day == weekday_name
        return False
    
    
    def get_recurring_events(db: Session) -> List[Event]:
        return (
            db.query(Event)
            .filter(Event.is_recurring.is_(True))
            .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
            .all()
        )
    
    
    def get_today_events(db: Session, *, now_utc: Optional[datetime] = None) -> List[Event]:
        now = now_utc or _now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
    
        dated_events = (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(
                    and_(Event.start_datetime >= start_of_day, Event.start_datetime < end_of_day),
                    and_(Event.end_datetime.isnot(None), Event.start_datetime < end_of_day, Event.end_datetime >= start_of_day),
                ),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .all()
        )
    
        recurring_events = [event for event in get_recurring_events(db) if _matches_recurrence(event, now)]
    
        combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
        for event in recurring_events:
            combined_by_id.setdefault(event.id, event)
    
        return sorted(combined_by_id.values(), key=lambda event: (event.start_datetime or datetime.min, event.id))
    
    
    def search_events(db: Session, query: str, *, limit: int = 10, offset: int = 0) -> List[Event]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return []
    
        like_pattern = f"%{cleaned_query}%"
        return (
            db.query(Event)
            .filter(
                or_(
                    Event.name.ilike(like_pattern),
                    Event.description.ilike(like_pattern),
                    Event.category.ilike(like_pattern),
                    Event.special_notes.ilike(like_pattern),
                )
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )

4. 4B/week7/migrations/env.py

    import os
    import sys
    from pathlib import Path
    
    from alembic import context
    from sqlalchemy import engine_from_config, pool
    
    config = context.config
    
    config_file = Path(config.config_file_name).resolve()
    script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
    week_dir = script_location.parent
    if str(week_dir) not in sys.path:
        sys.path.insert(0, str(week_dir))
    
    _models = sys.modules.get("4B.week7.database.models") or sys.modules.get("database.models")
    if _models:
        Base = _models.Base
        if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
            import database.schema
    else:
        from database.models import Base
        import database.schema
    
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        config.set_main_option("sqlalchemy.url", db_url)
    
    target_metadata = Base.metadata
    
    
    def run_migrations_offline() -> None:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
        with context.begin_transaction():
            context.run_migrations()
    
    
    def run_migrations_online() -> None:
        connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    
    
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

5. 4B/week7/migrations/versions/003_add_events_table.py

    from typing import Sequence, Union
    
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql
    
    revision: str = "003"
    down_revision: Union[str, None] = "002"
    branch_labels: Union[str, Sequence[str], None] = None
    depends_on: Union[str, Sequence[str], None] = None
    
    event_source_site_enum = postgresql.ENUM(
        "radhakrishnatemple",
        "jkyog",
        name="event_source_site",
        create_type=True,
    )
    
    
    def upgrade() -> None:
        event_source_site_enum.create(op.get_bind(), checkfirst=True)
    
        op.create_table(
            "events",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("start_datetime", sa.DateTime(), nullable=False),
            sa.Column("end_datetime", sa.DateTime(), nullable=True),
            sa.Column("location", sa.Text(), nullable=True),
            sa.Column("venue_details", sa.Text(), nullable=True),
            sa.Column("parking_notes", sa.Text(), nullable=True),
            sa.Column("food_info", sa.Text(), nullable=True),
            sa.Column(
                "sponsorship_data",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("image_url", sa.Text(), nullable=True),
            sa.Column("source_url", sa.Text(), nullable=False),
            sa.Column("source_site", event_source_site_enum, nullable=False),
            sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("recurrence_pattern", sa.Text(), nullable=True),
            sa.Column("category", sa.Text(), nullable=True),
            sa.Column("special_notes", sa.Text(), nullable=True),
            sa.Column("scraped_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("dedup_key", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
            sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
            sa.UniqueConstraint("source_site", "source_url", name=op.f("uq_events_source_site_source_url")),
        )
    
        op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
        op.create_index(op.f("ix_events_name"), "events", ["name"])
        op.create_index(op.f("ix_events_category"), "events", ["category"])
        op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
        op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])
    
    
    def downgrade() -> None:
        op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
        op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
        op.drop_index(op.f("ix_events_category"), table_name="events")
        op.drop_index(op.f("ix_events_name"), table_name="events")
        op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
        op.drop_table("events")
        event_source_site_enum.drop(op.get_bind(), checkfirst=True)

6. 4B/week7/scripts/__init__.py

    """Week 7 database-side scripts."""

7. 4B/week7/scripts/seed_from_scraped_json.py

    from __future__ import annotations
    
    import sys
    from pathlib import Path
    
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    
    import json
    from typing import Any, Dict, List
    
    from sqlalchemy.orm import Session
    
    try:
        from ..database.event_storage import upsert_events
    except ImportError:
        from database.event_storage import upsert_events
    
    
    def _load_input(path: Path) -> List[Dict[str, Any]]:
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
    
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            events = payload.get("events", [])
        elif isinstance(payload, list):
            events = payload
        else:
            raise ValueError("Input JSON must be a list or an object with an events key")
    
        if not isinstance(events, list):
            raise ValueError("events must be a list")
    
        return [item for item in events if isinstance(item, dict)]
    
    
    def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
        events = _load_input(Path(input_path).resolve())
        stats = upsert_events(db, events)
        stats["input_count"] = len(events)
        return stats

8. 4B/week7/scripts/seed_database.py

    from __future__ import annotations
    
    import sys
    from pathlib import Path
    
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    
    import argparse
    
    try:
        from ..database.models import SessionLocal, init_db
        from .seed_from_scraped_json import seed_from_file
    except ImportError:
        from database.models import SessionLocal, init_db
        from scripts.seed_from_scraped_json import seed_from_file
    
    
    def main() -> None:
        parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
        parser.add_argument(
            "--input",
            default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
            help="Path to scraped events JSON",
        )
        args = parser.parse_args()
    
        init_db()
    
        db = SessionLocal()
        try:
            stats = seed_from_file(db, args.input)
        finally:
            db.close()
    
        print("Seed complete")
        print(f"Input events: {stats['input_count']}")
        print(f"Inserted: {stats['inserted']}")
        print(f"Updated: {stats['updated']}")
        print(f"Failed: {stats['failed']}")
    
    
    if __name__ == "__main__":
        main()

9. 4B/week7/tests/conftest.py

    import os
    import sys
    from pathlib import Path
    
    
    def pytest_configure() -> None:
        week7_dir = Path(__file__).resolve().parents[1]
        if str(week7_dir) not in sys.path:
            sys.path.insert(0, str(week7_dir))
        os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")

10. 4B/week7/tests/test_event_storage.py

    from datetime import datetime, timedelta, timezone
    
    import pytest
    
    from database.event_storage import build_dedup_key, is_event_stale, normalize_event_payload
    
    
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
                {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
            ],
        }
    
        normalized = normalize_event_payload(payload)
        assert normalized["name"] == "Health Fair"
        assert normalized["source_site"].value == "jkyog"
        assert normalized["start_datetime"].year == 2026
        assert normalized["dedup_key"]
        assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"
    
    
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
    
        with pytest.raises(ValueError):
            normalize_event_payload(payload)
    
    
    def test_is_event_stale_true_when_older_than_threshold() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        old = now - timedelta(days=31)
        assert is_event_stale(old, now_utc=now, stale_after_days=30) is True
    
    
    def test_is_event_stale_false_when_recent() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        recent = now - timedelta(days=10)
        assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False

11. 4B/week7/tests/test_migrations_events.py

    from pathlib import Path
    
    
    def test_events_migration_exists() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        assert migration_path.is_file()
    
    
    def test_events_migration_revision_chain() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert 'revision: str = "003"' in content
        assert 'down_revision: Union[str, None] = "002"' in content
    
    
    def test_events_migration_indexes_present() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert "ix_events_start_datetime" in content
        assert "ix_events_name" in content
        assert "ix_events_category" in content
        assert "ix_events_is_recurring" in content
        assert "ix_events_dedup_key" in content

12. 4B/week7/data/.gitkeep

    empty file

If you want, I can next give a single valid 4B/week7/data/scraped_events.json sample that exercises insert, update, dedup, and stale scenarios.

User: do you think these are commit ready

GitHub Copilot: Yes, this set is commit-ready for your Week 7 ownership.

Before pushing, do a final quick gate:
1. Run migrations upgrade on a clean test DB.
2. Run tests for event storage and migration checks.
3. Run seed once with a real scraped JSON sample and verify inserted/updated/failed counts.
4. Run seed again with same file to confirm dedup/upsert behavior.
5. Confirm no unintended file changes outside your scope folders.

If those pass, you can commit with confidence.

User: what about the placeholder url? should it be that only or should it change to real url?

check the requriements once

GitHub Copilot: Good catch. Based on your Week 7 requirements, placeholder URLs are fine only in tests and sample fixtures, but not for demo data.

1. For tests:
Use placeholder values like https://example.org. That is correct and standard for unit tests.

2. For real pipeline output and demo seed input:
Use real source URLs from the actual scraped pages. Your requirement says source_url is where the event was scraped from, and your assignment explicitly asks for real data from radhakrishnatemple.net and jkyog.org.

3. For your final submission expectation:
The code can keep placeholders in test files, but the JSON you use in demo run and DB seeding should contain real event page links.

So the rule is:
Placeholder in tests is OK.
Real URLs in scraper output and seeded demo data are required.

User: according to my requiremetns, should i leave the placeholders as is, or should i change to real url?

GitHub Copilot: According to your requirements: change to real URLs for any actual scraped/seeded event data, keep placeholders only in tests.

So:
1. Keep `https://example.org` in unit tests.
2. Use real `radhakrishnatemple.net` / `jkyog.org` source links in demo JSON, scraper output, and DB seed input.

If you submit/demo with placeholder URLs in the real event dataset, that can be flagged as not meeting the “real data” requirement.

User: for my tasks, as given in the requiremetns, give me a checklist where exactly i should use what urls

GitHub Copilot: Use this checklist for your Week 7 scope.

1. Real URLs required
- Scraper target URLs.
- Scraper output JSON for demo runs.
- Seed input JSON used to populate database for demo.
- Event source_url field stored in DB rows.
- Any screenshot/log evidence you submit to prove real scraping.

2. Placeholder URLs allowed
- Unit test payloads.
- Static test fixtures that are not claimed as real scraped data.
- Pure documentation examples that are clearly marked as examples.

3. Never use placeholders here
- Final demo dataset.
- Anything used for /events, /events/today, /events/search demo.
- Any “real data” claim in weekly summary or PR description.

4. Practical mapping for your work
- In validation tests: keep example.org.
- In runtime seeding: replace with actual radhakrishnatemple.net or jkyog.org event links.
- In source_url for inserted/upserted rows: always real page URL from scrape.
- In sponsorship links inside real event payloads: use real sponsor links if present; if missing from source site, leave null/empty, do not fabricate.

5. Pre-commit URL sanity check
- Search for example.org in runtime/demo inputs and remove it.
- Ensure example.org remains only in tests/docs.
- Verify at least one seeded record per source has a real source_url visible in DB/API response.

If you want, I can give you a quick pass/fail matrix you can paste into your PR description.

User: can you give me branch, folder structure for all my files

GitHub Copilot: Use this branch name:

1. 4B-week7-chakradhar-gummakonda

Use this folder structure under 4B/week7:

1. database/
2. database/schema.py
3. database/models.py
4. database/event_storage.py
5. database/state_tracking.py (unchanged from week6)
6. migrations/
7. migrations/env.py
8. migrations/versions/
9. migrations/versions/001_initial_schema_users_conversations_messages_session_state.py (unchanged)
10. migrations/versions/002_add_escalations_table.py (unchanged)
11. migrations/versions/003_add_events_table.py
12. scripts/
13. scripts/__init__.py
14. scripts/seed_from_scraped_json.py
15. scripts/seed_database.py
16. tests/
17. tests/conftest.py
18. tests/test_event_storage.py
19. tests/test_migrations_events.py
20. data/
21. data/.gitkeep
22. alembic.ini (unchanged from week6)

Suggested commit grouping:

1. Commit 1: schema + migration files
2. Commit 2: storage + seed scripts
3. Commit 3: tests
4. Commit 4: minor logging/import robustness polish

If you want, I can give you the exact git commands sequence for creating the branch and committing in that order.

User: where to insert upserts and dedups

GitHub Copilot: Put both in your storage layer file: 4B/week7/database/event_storage.py.

1. Dedup logic location
- Keep dedup key generation in `build_dedup_key(...)`.
- Normalize and build dedup key in `normalize_event_payload(...)`.
- Enforce DB-level dedup with unique constraints in 4B/week7/database/schema.py and 4B/week7/migrations/versions/003_add_events_table.py:
- `uq_events_dedup_key`
- `uq_events_source_site_source_url`

2. Upsert logic location
- Main per-record upsert goes in `upsert_event(...)` in 4B/week7/database/event_storage.py:
- check existing by `dedup_key`
- fallback check by `(source_site, source_url)`
- update if found, insert if not

3. Batch ingestion location
- Loop and call upsert per payload in `upsert_events(...)` in 4B/week7/database/event_storage.py.
- Keep savepoint pattern (`db.begin_nested()`) there for per-record safety.

4. Where it gets called
- Seed pipeline should call only `upsert_events(...)` from 4B/week7/scripts/seed_from_scraped_json.py, which is triggered by 4B/week7/scripts/seed_database.py.

Short version: do not put upsert/dedup in scripts or migrations; keep logic centralized in 4B/week7/database/event_storage.py, and keep constraints in schema/migration files.

User: cam you check the file structure once, folders.

I'm given tasks to perform.

Can you once check the repos, folders, files:

They might be migrated, so give me files such that they do not have import errors.

First give me the list of files required for cahnges, or files requried to be added. i need a perfect work to be done.

I'm Chakradhar.

Here are the tasks assigned:
Hi Group 4B,

Hope midterms went well! This week we're shifting into real-world data engineering — you're building the event data pipeline that makes the bot temple-aware.

WEEK 7 THEME: Event Data Pipeline — Web Scraping, Storage & API
DEADLINE: Wednesday, April 2, 2026 at 11:59 PM CST

THE CHALLENGE:
The Radha Krishna Temple of Dallas publishes events on their website, but there's no API or calendar feed. You need to:
1. SCRAPE real event data from live websites
2. STORE it in a structured database
3. SERVE it through API endpoints the bot can query

By Friday's demo, someone should be able to hit /events/today and get real temple events back.

DATA SOURCES TO SCRAPE:
• radhakrishnatemple.net — Homepage event carousel + individual event detail pages (schedules, parking info, sponsorship tiers, food, special notes)
• jkyog.org/upcoming_events — Organization-wide calendar (filter for Dallas/Allen, TX events at Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

Current events on the temple site: Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

WHAT MAKES THIS HARD:
• No API — pure HTML parsing
• Inconsistent page formatting across events
• Multi-day events with different daily sub-schedules
• Two websites with completely different HTML structures
• Must handle gracefully: site down, HTML changes, no upcoming events

────────────────────────────
INDIVIDUAL ASSIGNMENTS
────────────────────────────

SYSHA SHARMA (Team Lead) — Scraper Architecture & Orchestration
• Build event_scraper module: scrape radhakrishnatemple.net homepage → extract event carousel → follow each event link → scrape detail pages → scrape jkyog.org/upcoming_events for Dallas events
• Output: structured JSON matching Team 4A's event data model
• Configurable target URLs, scrape intervals, user-agent, request delays (be respectful to their servers)
• Error handling: site down, HTML structure changes, timeouts
• Orchestration: scrape_events script (scrape both sites → output JSON) + seed_database script (JSON → database)

ROHAN BHARGAV KOTHAPALLI — /events API Endpoints + Escalation Auth Fix
• Implement API endpoints:
  - GET /events — All upcoming events (pagination: ?limit=10&offset=0)
  - GET /events/today — Today's events + active recurring programs
  - GET /events/{id} — Single event detail
  - GET /events/search?q={query} — Case-insensitive search by name/description
  - GET /events/recurring — All recurring programs
  - Proper error responses: 404, 400, 200 with empty list
• TECH DEBT (Security Blocker): Add Bearer token auth to ALL /escalations endpoints (POST, GET, PUT). Reject unauthenticated with 401. This was flagged Week 6 — must be fixed.
• Integration: wire scraper → database → API. Demo /events/today with real data.

CHAKRADHAR REDDY GUMMAKONDA — Event Database Schema & Storage Layer
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

SUBODH KRISHNA NIKUMBH — Event Service Wrapper & Test Suite
• EventService: getUpcomingEvents(limit, offset), getTodayEvents(), searchEvents(query), getEventById(id), getRecurringSchedule()
• Caching layer: cache frequent queries, invalidate on re-scrape
• 20+ tests covering: scraper parsing (use real HTML fixtures from both sites), malformed HTML, service cache hit/miss, stale data, pagination, API endpoints, search relevance
• Integration test: scrape → store → query → verify end-to-end

LEENA HUSSEIN — Stripe Webhooks Completion + Event Pipeline Documentation
• TECH DEBT: Handle payment_intent.succeeded and payment_intent.payment_failed webhooks, Stripe-Signature verification, test coverage for both paths
• Event Pipeline Docs: Admin runbook (how to run scraper, trigger refresh, verify data), architecture diagram (website → scraper → DB → API → bot), troubleshooting guide (HTML changes, scrape failures, stale data), all new environment variables documented

────────────────────────────
FRIDAY DEMO TARGET (April 4)
────────────────────────────
Be ready to show:
1. Run the scraper → real JSON from temple websites
2. Query the database → stored events
3. GET /events/today → real events for that day
4. Search "Hanuman Jayanti" → correct result
5. /escalations with auth → 401 without token, 200 with token

────────────────────────────
SUBMISSION
────────────────────────────
• Email your weekly summary by Wednesday April 2, 11:59 PM CST
• Push all deliverables to 4B/week7/ in the repo
• Branch: 4B-week7-[your-name], PR into main by deadline
• Atomic commits with meaningful messages (no "update" or "fix")

Full assignment details are in the repo: 4B/week7/ASSIGNMENT.md

4B/week7/ASSIGNMENT.md:
# Week 7 Assignment — Group 4B
## Event Data Pipeline: Web Scraping, Storage & API
**Sprint: March 30 – April 2, 2026**

---

## 🎯 This Week's Mission

Build the **event data pipeline** that powers the JKYog WhatsApp Bot's event awareness. By the end of this week, you should have:
1. A **web scraper** that extracts real event data from temple websites
2. A **database** to store and query events
3. **API endpoints** to serve event data to the bot
4. **Tests** proving it all works

This is real-world data engineering — you're scraping live websites with unstructured HTML and turning it into clean, queryable data.

---

## Context: The Data Sources

### Source 1: radhakrishnatemple.net (Primary — Dallas Temple)
- **Homepage** — Event carousel with upcoming events (name, date range, time)
- **Individual event pages** — Full details: schedule, parking, sponsorship tiers, food, special notes
- **Daily schedule sidebar** — Darshan timings, aarti, bhog, Satsang, bhajans
- **Example current events:** Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

### Source 2: jkyog.org/upcoming_events (Secondary — Organization-wide)
- Lists JKYog events globally, some Dallas-specific
- Events have: title, date, time, venue, link to detail page
- Filter for Dallas/Allen, TX events (Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

### What Makes This Challenging
- No API — pure HTML scraping
- Event pages have inconsistent formatting (some have parking notes, some don't)
- Multi-day events (Ram Navami spans 4 days with different daily schedules)
- Two different websites with different HTML structures
- Events are published ~1-2 months in advance, so the scraper needs to handle "no upcoming events" gracefully

---

## Individual Assignments

### Sysha Sharma (Team Lead) — Scraper Architecture & Orchestration
**Design and build the scraper that extracts events from both websites.**

Deliverables:
1. **Event Scraper Module** (`event_scraper.py` or equivalent):
   - Scrape `radhakrishnatemple.net` homepage → extract event carousel (name, dates, times, links)
   - Follow each event link → scrape detail page (full schedule, parking, sponsorship, food info)
   - Scrape `jkyog.org/upcoming_events` → extract Dallas-area events
   - Output: structured JSON matching Team 4A's event data model

2. **Scraper Configuration:**
   - Configurable target URLs (don't hardcode)
   - Configurable scrape interval (for future cron scheduling)
   - User-agent string, request delays (be respectful to the servers)
   - Error handling: site down, HTML structure changed, timeout

3. **Orchestration Script:**
   - `scrape_events.py` — Run once, scrape both sites, output JSON
   - `seed_database.py` — Take scraped JSON, insert into database
   - README with setup instructions

---

### Rohan Bhargav Kothapalli — /events API Endpoints + Escalation Auth Fix
**Build the API that serves event data to the bot.**

Deliverables:
1. **Event API Endpoints:**
   - `GET /events` — All upcoming events (sorted by date, with pagination: `?limit=10&offset=0`)
   - `GET /events/today` — Today's events + currently active recurring programs
   - `GET /events/{id}` — Single event with full details
   - `GET /events/search?q={query}` — Search events by name/description (case-insensitive)
   - `GET /events/recurring` — All recurring programs (darshan, aarti, Satsang, etc.)
   - Proper error responses: 404 (event not found), 400 (bad query), 200 (empty list for no results)

2. **TECH DEBT FIX — Escalation API Auth (SECURITY BLOCKER):**
   - Add Bearer token validation to ALL `/escalations` endpoints (POST, GET, PUT)
   - Reject unauthenticated requests with 401
   - This was flagged in Week 6 — must be resolved this week

3. **Integration:** Wire the scraper output → database → API. Demo: hit `/events/today` and get real temple events.

---

### Chakradhar Reddy Gummakonda — Event Database Schema & Storage Layer
**Design and implement the persistence layer for event data.**

Deliverables:
1. **Database Schema:**
   ```sql
   events table:
   - id (primary key, auto-increment)
   - name (text, not null)
   - description (text)
   - start_datetime (timestamp, not null)
   - end_datetime (timestamp)
   - location (text)
   - venue_details (text)
   - parking_notes (text)
   - food_info (text)
   - sponsorship_data (jsonb — tiers with names, amounts, links)
   - image_url (text)
   - source_url (text, not null — where this was scraped from)
   - source_site (enum: 'radhakrishnatemple', 'jkyog')
   - is_recurring (boolean, default false)
   - recurrence_pattern (text — e.g., "daily", "weekly:sunday", "weekdays")
   - category (text — e.g., "festival", "program", "health", "cultural")
   - special_notes (text)
   - scraped_at (timestamp — when this data was last refreshed)
   - created_at (timestamp)
   - updated_at (timestamp)
   ```

2. **Indexes:** On start_datetime, name, category, is_recurring (for fast queries)

3. **Seed Script:** Populate database with REAL scraped data from both websites

4. **Data Integrity:**
   - Upsert logic (don't duplicate events on re-scrape)
   - Deduplication between the two sources (same event on both sites)
   - "Stale data" flag if scraped_at > 30 days ago

---

### Subodh Krishna Nikumbh — Event Service Wrapper & Test Suite
**Build the service layer and comprehensive tests.**

Deliverables:
1. **EventService Wrapper:**
   - `getUpcomingEvents(limit, offset)` — Paginated upcoming events
   - `getTodayEvents()` — Today's events + active recurring programs based on current time
   - `searchEvents(query)` — Full-text search
   - `getEventById(id)` — Single event lookup
   - `getRecurringSchedule()` — All recurring programs
   - Caching layer (in-memory or Redis): cache frequent queries, invalidate on re-scrape

2. **Test Suite (target: 20+ tests):**
   - **Scraper tests:** Parse real HTML fixtures from both websites, handle malformed HTML, handle missing fields
   - **Service tests:** Cache hit/miss, stale data handling, empty results, pagination edge cases
   - **API tests:** All endpoints return correct status codes, search returns relevant results
   - **Integration test:** Scrape → Store → Query → Verify

---

### Leena Hussein — Stripe Webhooks Completion + Event Operations Documentation
**Complete the payment flow AND document the new event pipeline.**

Deliverables:
1. **TECH DEBT FIX — Stripe Webhooks:**
   - Handle `payment_intent.succeeded` webhook → update donation record
   - Handle `payment_intent.payment_failed` webhook → log failure, notify admin
   - Webhook signature verification (Stripe-Signature header)
   - Test coverage for both success and failure paths

2. **Event Pipeline Documentation:**
   - **Admin Runbook:** How to run the scraper manually, how to trigger a refresh, how to verify data is current
   - **Architecture Diagram:** Data flow from website → scraper → database → API → bot
   - **Troubleshooting Guide:** What happens when the website structure changes? When a scrape fails? When events are stale?
   - **Environment Variables:** Document all new env vars (scraper URLs, scrape interval, DB connection, cache TTL)

---

## Deadline

**Wednesday, April 2, 2026 at 11:59 PM 
## Git Requirements
- Branch: `4B-week7-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
- Atomic commits with meaningful messages (no "update" or "fix")

Be ready to demonstrate:
1. Run the scraper → show extracted JSON with real temple events
2. Query the database → show stored events
3. Hit `/events/today` → return real events happening that day
4. Search for "Hanuman Jayanti" → return correct result

My files:
1. 4B/week7/database/schema.py
 
    from __future__ import annotations
    import enum
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy import (
        Boolean,
        CheckConstraint,
        Column,
        DateTime,
        Enum as SAEnum,
        ForeignKey,
        Integer,
        String,
        Text,
        UniqueConstraint,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.orm import relationship
    from .models import Base

    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    class User(Base):
        __tablename__ = "users"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        phone_number = Column(String, unique=True, index=True, nullable=False)
        name = Column(String, nullable=True)
        preferences = Column(JSONB, default=dict, nullable=False)
        last_active_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
        conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
        sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")
        escalations = relationship("Escalation", back_populates="user", cascade="all, delete-orphan")

    class Conversation(Base):
        __tablename__ = "conversations"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        status = Column(String, default="active", index=True, nullable=False)
        started_at = Column(DateTime, default=_now, nullable=False)
        ended_at = Column(DateTime, nullable=True)
        user = relationship("User", back_populates="conversations")
        messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    class Message(Base):
        __tablename__ = "messages"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
        direction = Column(String, nullable=False)
        text = Column(Text, nullable=False)
        intent = Column(String, nullable=True)
        created_at = Column(DateTime, default=_now, nullable=False)
        conversation = relationship("Conversation", back_populates="messages")

    class SessionState(Base):
        __tablename__ = "session_state"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        session_token = Column(String(64), unique=True, index=True, nullable=False)
        expires_at = Column(DateTime, nullable=True)
        is_active = Column(Boolean, default=True, index=True, nullable=False)
        state = Column(JSONB, default=dict, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
        user = relationship("User", back_populates="sessions")
        escalations = relationship("Escalation", back_populates="session")

    class Escalation(Base):
        __tablename__ = "escalations"
        __table_args__ = (
            CheckConstraint(
                "status IN ('pending', 'in_progress', 'resolved')",
                name="valid_escalation_status",
            ),
        )
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
        session_id = Column(UUID(as_uuid=True), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)
        reason = Column(Text, nullable=False)
        context = Column(JSONB, default=dict, nullable=False)
        status = Column(String, nullable=False, default="pending", index=True)
        created_at = Column(DateTime, default=_now, nullable=False)
        resolved_at = Column(DateTime, nullable=True)
        resolved_by = Column(String, nullable=True)
        user = relationship("User", back_populates="escalations")
        session = relationship("SessionState", back_populates="escalations")

    class EventSourceSite(str, enum.Enum):
        RADHAKRISHNATEMPLE = "radhakrishnatemple"
        JKYOG = "jkyog"

    class Event(Base):
        __tablename__ = "events"
        __table_args__ = (
            UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
            UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
        )
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(Text, nullable=False, index=True)
        description = Column(Text, nullable=True)
        start_datetime = Column(DateTime, nullable=False, index=True)
        end_datetime = Column(DateTime, nullable=True)
        location = Column(Text, nullable=True)
        venue_details = Column(Text, nullable=True)
        parking_notes = Column(Text, nullable=True)
        food_info = Column(Text, nullable=True)
        sponsorship_data = Column(JSONB, default=list, nullable=False)
        image_url = Column(Text, nullable=True)
        source_url = Column(Text, nullable=False)
        source_site = Column(
            SAEnum(
                EventSourceSite,
                name="event_source_site",
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
            ),
            nullable=False,
        )
        is_recurring = Column(Boolean, default=False, nullable=False, index=True)
        recurrence_pattern = Column(Text, nullable=True)
        category = Column(Text, nullable=True, index=True)
        special_notes = Column(Text, nullable=True)
        scraped_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
        dedup_key = Column(String(64), nullable=False, index=True)
 
2. 4B/week7/database/models.py
 
    import os
    import time
    from pathlib import Path
    from typing import Any, Callable, Generator, TypeVar
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import MetaData, create_engine, text
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session, declarative_base, sessionmaker
    T = TypeVar("T")

    def _get_database_url() -> str:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    def _env_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _env_float(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _run_with_retry(
        operation: Callable[[], T],
        retries: int | None = None,
        base_delay_seconds: float | None = None,
    ) -> T:
        max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
        base_delay = (
            base_delay_seconds
            if base_delay_seconds is not None
            else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
        )
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except OperationalError as exc:
                last_error = exc
                if attempt == max_attempts:
                    break
                delay = base_delay * (2 ** (attempt - 1))
                time.sleep(delay)
        raise RuntimeError(f"Database operation failed after {max_attempts} attempts") from last_error

    convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    metadata = MetaData(naming_convention=convention)
    Base = declarative_base(metadata=metadata)
    engine = create_engine(
        _get_database_url(),
        pool_pre_ping=True,
        pool_size=_env_int("DB_POOL_SIZE", 5),
        max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
        pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
        pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
        pool_use_lifo=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def _execute_health_query() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def _execute_escalations_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

    def _execute_events_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM events LIMIT 1"))

    def check_db_health() -> dict[str, Any]:
        try:
            _run_with_retry(_execute_health_query)
        except Exception as exc:
            return {"status": "error", "database": "disconnected", "detail": str(exc)}
        escalations_ok = True
        events_ok = True
        try:
            _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            escalations_ok = False
        try:
            _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            events_ok = False
        if escalations_ok and events_ok:
            return {
                "status": "ok",
                "database": "connected",
                "tables": {"escalations": "ok", "events": "ok"},
            }
        return {
            "status": "degraded",
            "database": "connected",
            "tables": {
                "escalations": "ok" if escalations_ok else "unreachable",
                "events": "ok" if events_ok else "unreachable",
            },
        }

    def init_db() -> None:
        week_dir = Path(__file__).resolve().parent.parent
        alembic_ini = week_dir / "alembic.ini"
        if not alembic_ini.is_file():
            raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")
        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(week_dir / "migrations"))
        _run_with_retry(lambda: command.upgrade(cfg, "head"))
 
3. 4B/week7/database/event_storage.py
 
    from __future__ import annotations
    import hashlib
    import logging
    from datetime import datetime, timedelta, timezone
    from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
    from sqlalchemy import and_, func, or_
    from sqlalchemy.orm import Session
    from .schema import Event, EventSourceSite

    WEEKDAY_NAMES = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    logger = logging.getLogger(__name__)

    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def _normalize_text(value: Optional[str]) -> str:
        if not value:
            return ""
        return " ".join(value.strip().lower().split())

    def _clean_optional_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _parse_datetime(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        raise ValueError(f"Unsupported datetime value: {value!r}")

    def _coerce_source_site(value: Any) -> EventSourceSite:
        if isinstance(value, EventSourceSite):
            return value
        if not isinstance(value, str):
            raise ValueError("source_site must be a string")
        cleaned = value.strip().lower()
        if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
            return EventSourceSite.RADHAKRISHNATEMPLE
        if cleaned == EventSourceSite.JKYOG.value:
            return EventSourceSite.JKYOG
        raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

    def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("sponsorship_data must be a list of sponsorship tier objects")
        validated: List[Dict[str, str]] = []
        required_fields = ("name", "amount", "link")
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise ValueError(f"sponsorship_data[{index}] must be an object with name, amount, and link")
            normalized_item: Dict[str, str] = {}
            for field in required_fields:
                raw_value = item.get(field)
                if not isinstance(raw_value, str) or not raw_value.strip():
                    raise ValueError(f"sponsorship_data[{index}].{field} must be a non-empty string")
                normalized_item[field] = raw_value.strip()
            validated.append(normalized_item)
        return validated

    def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
        base = "|".join(
            [
                _normalize_text(name),
                start_datetime.strftime("%Y-%m-%dT%H:%M"),
                _normalize_text(location),
            ]
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def normalize_event_payload(
        payload: Dict[str, Any],
        *,
        default_scraped_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        name = (payload.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        source_url = (payload.get("source_url") or "").strip()
        if not source_url:
            raise ValueError("source_url is required")
        start_datetime = _parse_datetime(payload.get("start_datetime"))
        if not start_datetime:
            raise ValueError("start_datetime is required")
        end_datetime = _parse_datetime(payload.get("end_datetime"))
        scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
        source_site = _coerce_source_site(payload.get("source_site"))
        location = _clean_optional_text(payload.get("location"))
        dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
        sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))
        return {
            "name": name,
            "description": _clean_optional_text(payload.get("description")),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "location": location,
            "venue_details": _clean_optional_text(payload.get("venue_details")),
            "parking_notes": _clean_optional_text(payload.get("parking_notes")),
            "food_info": _clean_optional_text(payload.get("food_info")),
            "sponsorship_data": sponsorship_data,
            "image_url": _clean_optional_text(payload.get("image_url")),
            "source_url": source_url,
            "source_site": source_site,
            "is_recurring": bool(payload.get("is_recurring", False)),
            "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
            "category": _clean_optional_text(payload.get("category")),
            "special_notes": _clean_optional_text(payload.get("special_notes")),
            "scraped_at": scraped_at,
            "dedup_key": dedup_key,
        }

    def is_event_stale(
        scraped_at: datetime,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> bool:
        if stale_after_days <= 0:
            raise ValueError("stale_after_days must be > 0")
        now = now_utc or _now()
        return scraped_at < (now - timedelta(days=stale_after_days))

    def event_to_dict(
        event: Event,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> Dict[str, Any]:
        return {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
            "location": event.location,
            "venue_details": event.venue_details,
            "parking_notes": event.parking_notes,
            "food_info": event.food_info,
            "sponsorship_data": event.sponsorship_data,
            "image_url": event.image_url,
            "source_url": event.source_url,
            "source_site": event.source_site.value if event.source_site else None,
            "is_recurring": event.is_recurring,
            "recurrence_pattern": event.recurrence_pattern,
            "category": event.category,
            "special_notes": event.special_notes,
            "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            "dedup_key": event.dedup_key,
            "is_stale": is_event_stale(event.scraped_at, now_utc=now_utc, stale_after_days=stale_after_days)
            if event.scraped_at
            else False,
        }

    def serialize_events(
        events: Sequence[Event],
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        return [event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days) for event in events]

    def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(event_obj, key, value)
        event_obj.updated_at = _now()

    def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
        values = normalize_event_payload(payload)
        existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()
        if existing is None:
            existing = (
                db.query(Event)
                .filter(Event.source_site == values["source_site"], Event.source_url == values["source_url"])
                .first()
            )
        if existing:
            _apply_event_updates(existing, values)
            action = "updated"
            event_obj = existing
        else:
            now_utc = _now()
            event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
            db.add(event_obj)
            action = "inserted"
        db.flush()
        return event_obj, action

    def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
        stats = {"inserted": 0, "updated": 0, "failed": 0}
        for payload in payloads:
            try:
                with db.begin_nested():
                    _, action = upsert_event(db, payload)
                stats[action] += 1
            except Exception:
                logger.exception(
                    "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                    payload.get("name"),
                    payload.get("source_url"),
                    payload.get("source_site"),
                    extra={
                        "event_name": payload.get("name"),
                        "source_url": payload.get("source_url"),
                        "source_site": payload.get("source_site"),
                    },
                )
                stats["failed"] += 1
        db.commit()
        return stats

    def get_event_counts(db: Session) -> Dict[str, int]:
        total = db.query(func.count(Event.id)).scalar() or 0
        recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
        return {"total": int(total), "recurring": int(recurring)}

    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        return db.query(Event).filter(Event.id == event_id).first()

    def get_upcoming_events(
        db: Session,
        *,
        limit: int = 10,
        offset: int = 0,
        now_utc: Optional[datetime] = None,
    ) -> List[Event]:
        now = now_utc or _now()
        return (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(Event.start_datetime >= now, and_(Event.end_datetime.isnot(None), Event.end_datetime >= now)),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )

    def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
        if not event.is_recurring:
            return False
        pattern = _normalize_text(event.recurrence_pattern)
        if not pattern:
            return True
        weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]
        if pattern == "daily":
            return True
        if pattern == "weekdays":
            return reference_dt.weekday() < 5
        if pattern == "weekends":
            return reference_dt.weekday() >= 5
        if pattern.startswith("weekly:"):
            expected_day = pattern.split(":", 1)[1].strip()
            return expected_day == weekday_name
        return False

    def get_recurring_events(db: Session) -> List[Event]:
        return (
            db.query(Event)
            .filter(Event.is_recurring.is_(True))
            .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
            .all()
        )

    def get_today_events(db: Session, *, now_utc: Optional[datetime] = None) -> List[Event]:
        now = now_utc or _now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        dated_events = (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(
                    and_(Event.start_datetime >= start_of_day, Event.start_datetime < end_of_day),
                    and_(Event.end_datetime.isnot(None), Event.start_datetime < end_of_day, Event.end_datetime >= start_of_day),
                ),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .all()
        )
        recurring_events = [event for event in get_recurring_events(db) if _matches_recurrence(event, now)]
        combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
        for event in recurring_events:
            combined_by_id.setdefault(event.id, event)
        return sorted(combined_by_id.values(), key=lambda event: (event.start_datetime or datetime.min, event.id))

    def search_events(db: Session, query: str, *, limit: int = 10, offset: int = 0) -> List[Event]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return []
        like_pattern = f"%{cleaned_query}%"
        return (
            db.query(Event)
            .filter(
                or_(
                    Event.name.ilike(like_pattern),
                    Event.description.ilike(like_pattern),
                    Event.category.ilike(like_pattern),
                    Event.special_notes.ilike(like_pattern),
                )
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )
 
4. 4B/week7/migrations/env.py
 
    import os
    import sys
    from pathlib import Path
    from alembic import context
    from sqlalchemy import engine_from_config, pool
    config = context.config
    config_file = Path(config.config_file_name).resolve()
    script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
    week_dir = script_location.parent
    if str(week_dir) not in sys.path:
        sys.path.insert(0, str(week_dir))
    _models = sys.modules.get("4B.week7.database.models") or sys.modules.get("database.models")
    if _models:
        Base = _models.Base
        if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
            import database.schema
    else:
        from database.models import Base
        import database.schema
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        config.set_main_option("sqlalchemy.url", db_url)
    target_metadata = Base.metadata

    def run_migrations_offline() -> None:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online() -> None:
        connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
 
5. 4B/week7/migrations/versions/003_add_events_table.py
 
    from typing import Sequence, Union
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql
    revision: str = "003"
    down_revision: Union[str, None] = "002"
    branch_labels: Union[str, Sequence[str], None] = None
    depends_on: Union[str, Sequence[str], None] = None
    event_source_site_enum = postgresql.ENUM(
        "radhakrishnatemple",
        "jkyog",
        name="event_source_site",
        create_type=True,
    )

    def upgrade() -> None:
        event_source_site_enum.create(op.get_bind(), checkfirst=True)
        op.create_table(
            "events",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("start_datetime", sa.DateTime(), nullable=False),
            sa.Column("end_datetime", sa.DateTime(), nullable=True),
            sa.Column("location", sa.Text(), nullable=True),
            sa.Column("venue_details", sa.Text(), nullable=True),
            sa.Column("parking_notes", sa.Text(), nullable=True),
            sa.Column("food_info", sa.Text(), nullable=True),
            sa.Column(
                "sponsorship_data",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("image_url", sa.Text(), nullable=True),
            sa.Column("source_url", sa.Text(), nullable=False),
            sa.Column("source_site", event_source_site_enum, nullable=False),
            sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("recurrence_pattern", sa.Text(), nullable=True),
            sa.Column("category", sa.Text(), nullable=True),
            sa.Column("special_notes", sa.Text(), nullable=True),
            sa.Column("scraped_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("dedup_key", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
            sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
            sa.UniqueConstraint("source_site", "source_url", name=op.f("uq_events_source_site_source_url")),
        )
        op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
        op.create_index(op.f("ix_events_name"), "events", ["name"])
        op.create_index(op.f("ix_events_category"), "events", ["category"])
        op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
        op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

    def downgrade() -> None:
        op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
        op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
        op.drop_index(op.f("ix_events_category"), table_name="events")
        op.drop_index(op.f("ix_events_name"), table_name="events")
        op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
        op.drop_table("events")
        event_source_site_enum.drop(op.get_bind(), checkfirst=True)
 
6. 4B/week7/scripts/__init__.py
 
    """Week 7 database-side scripts."""
 
7. 4B/week7/scripts/seed_from_scraped_json.py
 
    from __future__ import annotations
    import sys
    from pathlib import Path
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    import json
    from typing import Any, Dict, List
    from sqlalchemy.orm import Session
    try:
        from ..database.event_storage import upsert_events
    except ImportError:
        from database.event_storage import upsert_events

    def _load_input(path: Path) -> List[Dict[str, Any]]:
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            events = payload.get("events", [])
        elif isinstance(payload, list):
            events = payload
        else:
            raise ValueError("Input JSON must be a list or an object with an events key")
        if not isinstance(events, list):
            raise ValueError("events must be a list")
        return [item for item in events if isinstance(item, dict)]

    def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
        events = _load_input(Path(input_path).resolve())
        stats = upsert_events(db, events)
        stats["input_count"] = len(events)
        return stats
 
8. 4B/week7/scripts/seed_database.py
 
    from __future__ import annotations
    import sys
    from pathlib import Path
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    import argparse
    try:
        from ..database.models import SessionLocal, init_db
        from .seed_from_scraped_json import seed_from_file
    except ImportError:
        from database.models import SessionLocal, init_db
        from scripts.seed_from_scraped_json import seed_from_file

    def main() -> None:
        parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
        parser.add_argument(
            "--input",
            default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
            help="Path to scraped events JSON",
        )
        args = parser.parse_args()
        init_db()
        db = SessionLocal()
        try:
            stats = seed_from_file(db, args.input)
        finally:
            db.close()
        print("Seed complete")
        print(f"Input events: {stats['input_count']}")
        print(f"Inserted: {stats['inserted']}")
        print(f"Updated: {stats['updated']}")
        print(f"Failed: {stats['failed']}")

    if __name__ == "__main__":
        main()
 
9. 4B/week7/tests/conftest.py
 
    import os
    import sys
    from pathlib import Path

    def pytest_configure() -> None:
        week7_dir = Path(__file__).resolve().parents[1]
        if str(week7_dir) not in sys.path:
            sys.path.insert(0, str(week7_dir))
        os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
 
10. 4B/week7/tests/test_event_storage.py
 
    from datetime import datetime, timedelta, timezone
    import pytest
    from database.event_storage import build_dedup_key, is_event_stale, normalize_event_payload

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
                {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
            ],
        }
        normalized = normalize_event_payload(payload)
        assert normalized["name"] == "Health Fair"
        assert normalized["source_site"].value == "jkyog"
        assert normalized["start_datetime"].year == 2026
        assert normalized["dedup_key"]
        assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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
        with pytest.raises(ValueError):
            normalize_event_payload(payload)

    def test_is_event_stale_true_when_older_than_threshold() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        old = now - timedelta(days=31)
        assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

    def test_is_event_stale_false_when_recent() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        recent = now - timedelta(days=10)
        assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
 
11. 4B/week7/tests/test_migrations_events.py
 
    from pathlib import Path

    def test_events_migration_exists() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        assert migration_path.is_file()

    def test_events_migration_revision_chain() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert 'revision: str = "003"' in content
        assert 'down_revision: Union[str, None] = "002"' in content

    def test_events_migration_indexes_present() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert "ix_events_start_datetime" in content
        assert "ix_events_name" in content
        assert "ix_events_category" in content
        assert "ix_events_is_recurring" in content
        assert "ix_events_dedup_key" in content
 
12. 4B/week7/data/.gitkeep
 
    empty file

Give me areview of the files, check for import errors

GitHub Copilot: I’ll quickly scan your workspace to verify whether these Week 7 files now exist, then I’ll give you a strict import-error review with exact findings and fixes.

[Internal file-search trace removed]

I found your actual Week 7 folder, and I’m now checking real file contents plus diagnostics to identify import issues versus your intended file list.

Checked , no problems found

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

Compacted conversationI’ve confirmed two key files are missing in your current tree, and I’m now checking migration and DB bootstrap files to determine exactly what will break at runtime.

[Internal file-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

I’m extracting exact line locations now so you get a precise pass/fail review with file-linked findings.

[Internal code-search trace removed]

[Internal local file-read trace removed]

[Internal file-search trace removed]

**Findings (ordered by severity)**

1. Critical: Week 7 event storage core is not actually implemented yet.
- schema.py ends with Escalation and has no Event ORM model.
- 001_initial_schema_users_conversations_messages_session_state.py and 002_add_escalations_table.py exist, but there is no third migration for an events table.
- Result: migration-safe event persistence is not in place yet.

2. High: Seed flow currently masks missing event storage imports and can “succeed” without DB upsert.
- In seed_database.py, import of database.event_storage is wrapped in broad exception handling, then falls back to a no-op path.
- seed_database.py explicitly proceeds with “upsert layer not available yet,” so runtime can look healthy while events are not persisted.

3. Medium: DB health probe does not include events table readiness.
- models.py probes escalations only.
- models.py reports table health only for escalations.
- For Week 7 ownership, this misses detection of broken event storage migration/deploys.

4. Medium: Event-focused tests are missing.
- No event-storage or migration validation tests were found under tests matching event scope.
- Risk: import or migration regressions for Week 7 can pass unnoticed.

**Import-error status**
- Static workspace diagnostics returned no current editor errors.
- But this is a false sense of safety for Week 7 goals, because the seed script intentionally swallows the missing event-storage import path.

**Exact files required now**

Add:
1. 4B/week7/database/event_storage.py  
2. 4B/week7/migrations/versions/003_add_events_table.py  
3. 4B/week7/scripts/seed_from_scraped_json.py  
4. 4B/week7/tests/test_event_storage.py  
5. 4B/week7/tests/test_migrations_events.py  

Modify:
1. schema.py  
2. models.py  
3. seed_database.py  
4. env.py (ensure metadata picks up new Event model cleanly)

If you want, I can next give you a strict pass/fail checklist mapped to Chakradhar Week 7 rubric lines so you can sign off before commit.

User: i have given you my files to check the codes, i will copy paste the files right now, first check for the codes in the files

GitHub Copilot: Paste the files one by one (or in small batches), and I’ll review the code immediately.

I’ll check for:
1. Import and module path issues.
2. Migration consistency and missing dependencies.
3. Runtime logic risks (silent failures, fallback paths, contract mismatches).
4. Week 7 scope alignment for event schema/storage.

Start with these first for fastest signal:
1. schema.py
2. models.py
3. env.py
4. seed_database.py

Then paste any new files you added (especially event storage and migration 003).

User: 1. 4B/week7/database/schema.py
 
    from __future__ import annotations
    import enum
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy import (
        Boolean,
        CheckConstraint,
        Column,
        DateTime,
        Enum as SAEnum,
        ForeignKey,
        Integer,
        String,
        Text,
        UniqueConstraint,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.orm import relationship
    from .models import Base

    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    class User(Base):
        __tablename__ = "users"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        phone_number = Column(String, unique=True, index=True, nullable=False)
        name = Column(String, nullable=True)
        preferences = Column(JSONB, default=dict, nullable=False)
        last_active_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
        conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
        sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")
        escalations = relationship("Escalation", back_populates="user", cascade="all, delete-orphan")

    class Conversation(Base):
        __tablename__ = "conversations"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        status = Column(String, default="active", index=True, nullable=False)
        started_at = Column(DateTime, default=_now, nullable=False)
        ended_at = Column(DateTime, nullable=True)
        user = relationship("User", back_populates="conversations")
        messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    class Message(Base):
        __tablename__ = "messages"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
        direction = Column(String, nullable=False)
        text = Column(Text, nullable=False)
        intent = Column(String, nullable=True)
        created_at = Column(DateTime, default=_now, nullable=False)
        conversation = relationship("Conversation", back_populates="messages")

    class SessionState(Base):
        __tablename__ = "session_state"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        session_token = Column(String(64), unique=True, index=True, nullable=False)
        expires_at = Column(DateTime, nullable=True)
        is_active = Column(Boolean, default=True, index=True, nullable=False)
        state = Column(JSONB, default=dict, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
        user = relationship("User", back_populates="sessions")
        escalations = relationship("Escalation", back_populates="session")

    class Escalation(Base):
        __tablename__ = "escalations"
        __table_args__ = (
            CheckConstraint(
                "status IN ('pending', 'in_progress', 'resolved')",
                name="valid_escalation_status",
            ),
        )
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
        session_id = Column(UUID(as_uuid=True), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)
        reason = Column(Text, nullable=False)
        context = Column(JSONB, default=dict, nullable=False)
        status = Column(String, nullable=False, default="pending", index=True)
        created_at = Column(DateTime, default=_now, nullable=False)
        resolved_at = Column(DateTime, nullable=True)
        resolved_by = Column(String, nullable=True)
        user = relationship("User", back_populates="escalations")
        session = relationship("SessionState", back_populates="escalations")

    class EventSourceSite(str, enum.Enum):
        RADHAKRISHNATEMPLE = "radhakrishnatemple"
        JKYOG = "jkyog"

    class Event(Base):
        __tablename__ = "events"
        __table_args__ = (
            UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
            UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
        )
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(Text, nullable=False, index=True)
        description = Column(Text, nullable=True)
        start_datetime = Column(DateTime, nullable=False, index=True)
        end_datetime = Column(DateTime, nullable=True)
        location = Column(Text, nullable=True)
        venue_details = Column(Text, nullable=True)
        parking_notes = Column(Text, nullable=True)
        food_info = Column(Text, nullable=True)
        sponsorship_data = Column(JSONB, default=list, nullable=False)
        image_url = Column(Text, nullable=True)
        source_url = Column(Text, nullable=False)
        source_site = Column(
            SAEnum(
                EventSourceSite,
                name="event_source_site",
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
            ),
            nullable=False,
        )
        is_recurring = Column(Boolean, default=False, nullable=False, index=True)
        recurrence_pattern = Column(Text, nullable=True)
        category = Column(Text, nullable=True, index=True)
        special_notes = Column(Text, nullable=True)
        scraped_at = Column(DateTime, default=_now, nullable=False)
        created_at = Column(DateTime, default=_now, nullable=False)
        updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
        dedup_key = Column(String(64), nullable=False, index=True)
 
2. 4B/week7/database/models.py
 
    import os
    import time
    from pathlib import Path
    from typing import Any, Callable, Generator, TypeVar
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import MetaData, create_engine, text
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session, declarative_base, sessionmaker
    T = TypeVar("T")

    def _get_database_url() -> str:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    def _env_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _env_float(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _run_with_retry(
        operation: Callable[[], T],
        retries: int | None = None,
        base_delay_seconds: float | None = None,
    ) -> T:
        max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
        base_delay = (
            base_delay_seconds
            if base_delay_seconds is not None
            else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
        )
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return operation()
            except OperationalError as exc:
                last_error = exc
                if attempt == max_attempts:
                    break
                delay = base_delay * (2 ** (attempt - 1))
                time.sleep(delay)
        raise RuntimeError(f"Database operation failed after {max_attempts} attempts") from last_error

    convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    metadata = MetaData(naming_convention=convention)
    Base = declarative_base(metadata=metadata)
    engine = create_engine(
        _get_database_url(),
        pool_pre_ping=True,
        pool_size=_env_int("DB_POOL_SIZE", 5),
        max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
        pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
        pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
        pool_use_lifo=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def _execute_health_query() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def _execute_escalations_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))

    def _execute_events_probe() -> None:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM events LIMIT 1"))

    def check_db_health() -> dict[str, Any]:
        try:
            _run_with_retry(_execute_health_query)
        except Exception as exc:
            return {"status": "error", "database": "disconnected", "detail": str(exc)}
        escalations_ok = True
        events_ok = True
        try:
            _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            escalations_ok = False
        try:
            _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
        except Exception:
            events_ok = False
        if escalations_ok and events_ok:
            return {
                "status": "ok",
                "database": "connected",
                "tables": {"escalations": "ok", "events": "ok"},
            }
        return {
            "status": "degraded",
            "database": "connected",
            "tables": {
                "escalations": "ok" if escalations_ok else "unreachable",
                "events": "ok" if events_ok else "unreachable",
            },
        }

    def init_db() -> None:
        week_dir = Path(__file__).resolve().parent.parent
        alembic_ini = week_dir / "alembic.ini"
        if not alembic_ini.is_file():
            raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")
        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(week_dir / "migrations"))
        _run_with_retry(lambda: command.upgrade(cfg, "head"))
 
3. 4B/week7/database/event_storage.py
 
    from __future__ import annotations
    import hashlib
    import logging
    from datetime import datetime, timedelta, timezone
    from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
    from sqlalchemy import and_, func, or_
    from sqlalchemy.orm import Session
    from .schema import Event, EventSourceSite

    WEEKDAY_NAMES = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    logger = logging.getLogger(__name__)

    def _now() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def _normalize_text(value: Optional[str]) -> str:
        if not value:
            return ""
        return " ".join(value.strip().lower().split())

    def _clean_optional_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _parse_datetime(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        raise ValueError(f"Unsupported datetime value: {value!r}")

    def _coerce_source_site(value: Any) -> EventSourceSite:
        if isinstance(value, EventSourceSite):
            return value
        if not isinstance(value, str):
            raise ValueError("source_site must be a string")
        cleaned = value.strip().lower()
        if cleaned == EventSourceSite.RADHAKRISHNATEMPLE.value:
            return EventSourceSite.RADHAKRISHNATEMPLE
        if cleaned == EventSourceSite.JKYOG.value:
            return EventSourceSite.JKYOG
        raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")

    def _validate_sponsorship_data(value: Any) -> List[Dict[str, str]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("sponsorship_data must be a list of sponsorship tier objects")
        validated: List[Dict[str, str]] = []
        required_fields = ("name", "amount", "link")
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise ValueError(f"sponsorship_data[{index}] must be an object with name, amount, and link")
            normalized_item: Dict[str, str] = {}
            for field in required_fields:
                raw_value = item.get(field)
                if not isinstance(raw_value, str) or not raw_value.strip():
                    raise ValueError(f"sponsorship_data[{index}].{field} must be a non-empty string")
                normalized_item[field] = raw_value.strip()
            validated.append(normalized_item)
        return validated

    def build_dedup_key(name: str, start_datetime: datetime, location: Optional[str]) -> str:
        base = "|".join(
            [
                _normalize_text(name),
                start_datetime.strftime("%Y-%m-%dT%H:%M"),
                _normalize_text(location),
            ]
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def normalize_event_payload(
        payload: Dict[str, Any],
        *,
        default_scraped_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        name = (payload.get("name") or "").strip()
        if not name:
            raise ValueError("name is required")
        source_url = (payload.get("source_url") or "").strip()
        if not source_url:
            raise ValueError("source_url is required")
        start_datetime = _parse_datetime(payload.get("start_datetime"))
        if not start_datetime:
            raise ValueError("start_datetime is required")
        end_datetime = _parse_datetime(payload.get("end_datetime"))
        scraped_at = _parse_datetime(payload.get("scraped_at")) or default_scraped_at or _now()
        source_site = _coerce_source_site(payload.get("source_site"))
        location = _clean_optional_text(payload.get("location"))
        dedup_key = build_dedup_key(name=name, start_datetime=start_datetime, location=location)
        sponsorship_data = _validate_sponsorship_data(payload.get("sponsorship_data"))
        return {
            "name": name,
            "description": _clean_optional_text(payload.get("description")),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "location": location,
            "venue_details": _clean_optional_text(payload.get("venue_details")),
            "parking_notes": _clean_optional_text(payload.get("parking_notes")),
            "food_info": _clean_optional_text(payload.get("food_info")),
            "sponsorship_data": sponsorship_data,
            "image_url": _clean_optional_text(payload.get("image_url")),
            "source_url": source_url,
            "source_site": source_site,
            "is_recurring": bool(payload.get("is_recurring", False)),
            "recurrence_pattern": _clean_optional_text(payload.get("recurrence_pattern")),
            "category": _clean_optional_text(payload.get("category")),
            "special_notes": _clean_optional_text(payload.get("special_notes")),
            "scraped_at": scraped_at,
            "dedup_key": dedup_key,
        }

    def is_event_stale(
        scraped_at: datetime,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> bool:
        if stale_after_days <= 0:
            raise ValueError("stale_after_days must be > 0")
        now = now_utc or _now()
        return scraped_at < (now - timedelta(days=stale_after_days))

    def event_to_dict(
        event: Event,
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> Dict[str, Any]:
        return {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
            "location": event.location,
            "venue_details": event.venue_details,
            "parking_notes": event.parking_notes,
            "food_info": event.food_info,
            "sponsorship_data": event.sponsorship_data,
            "image_url": event.image_url,
            "source_url": event.source_url,
            "source_site": event.source_site.value if event.source_site else None,
            "is_recurring": event.is_recurring,
            "recurrence_pattern": event.recurrence_pattern,
            "category": event.category,
            "special_notes": event.special_notes,
            "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            "dedup_key": event.dedup_key,
            "is_stale": is_event_stale(event.scraped_at, now_utc=now_utc, stale_after_days=stale_after_days)
            if event.scraped_at
            else False,
        }

    def serialize_events(
        events: Sequence[Event],
        *,
        now_utc: Optional[datetime] = None,
        stale_after_days: int = 30,
    ) -> List[Dict[str, Any]]:
        return [event_to_dict(event, now_utc=now_utc, stale_after_days=stale_after_days) for event in events]

    def _apply_event_updates(event_obj: Event, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(event_obj, key, value)
        event_obj.updated_at = _now()

    def upsert_event(db: Session, payload: Dict[str, Any]) -> Tuple[Event, str]:
        values = normalize_event_payload(payload)
        existing = db.query(Event).filter(Event.dedup_key == values["dedup_key"]).first()
        if existing is None:
            existing = (
                db.query(Event)
                .filter(Event.source_site == values["source_site"], Event.source_url == values["source_url"])
                .first()
            )
        if existing:
            _apply_event_updates(existing, values)
            action = "updated"
            event_obj = existing
        else:
            now_utc = _now()
            event_obj = Event(created_at=now_utc, updated_at=now_utc, **values)
            db.add(event_obj)
            action = "inserted"
        db.flush()
        return event_obj, action

    def upsert_events(db: Session, payloads: Iterable[Dict[str, Any]]) -> Dict[str, int]:
        stats = {"inserted": 0, "updated": 0, "failed": 0}
        for payload in payloads:
            try:
                with db.begin_nested():
                    _, action = upsert_event(db, payload)
                stats[action] += 1
            except Exception:
                logger.exception(
                    "Failed to upsert event payload: name=%r source_url=%r source_site=%r",
                    payload.get("name"),
                    payload.get("source_url"),
                    payload.get("source_site"),
                    extra={
                        "event_name": payload.get("name"),
                        "source_url": payload.get("source_url"),
                        "source_site": payload.get("source_site"),
                    },
                )
                stats["failed"] += 1
        db.commit()
        return stats

    def get_event_counts(db: Session) -> Dict[str, int]:
        total = db.query(func.count(Event.id)).scalar() or 0
        recurring = db.query(func.count(Event.id)).filter(Event.is_recurring.is_(True)).scalar() or 0
        return {"total": int(total), "recurring": int(recurring)}

    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        return db.query(Event).filter(Event.id == event_id).first()

    def get_upcoming_events(
        db: Session,
        *,
        limit: int = 10,
        offset: int = 0,
        now_utc: Optional[datetime] = None,
    ) -> List[Event]:
        now = now_utc or _now()
        return (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(Event.start_datetime >= now, and_(Event.end_datetime.isnot(None), Event.end_datetime >= now)),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )

    def _matches_recurrence(event: Event, reference_dt: datetime) -> bool:
        if not event.is_recurring:
            return False
        pattern = _normalize_text(event.recurrence_pattern)
        if not pattern:
            return True
        weekday_name = WEEKDAY_NAMES[reference_dt.weekday()]
        if pattern == "daily":
            return True
        if pattern == "weekdays":
            return reference_dt.weekday() < 5
        if pattern == "weekends":
            return reference_dt.weekday() >= 5
        if pattern.startswith("weekly:"):
            expected_day = pattern.split(":", 1)[1].strip()
            return expected_day == weekday_name
        return False

    def get_recurring_events(db: Session) -> List[Event]:
        return (
            db.query(Event)
            .filter(Event.is_recurring.is_(True))
            .order_by(Event.name.asc(), Event.start_datetime.asc(), Event.id.asc())
            .all()
        )

    def get_today_events(db: Session, *, now_utc: Optional[datetime] = None) -> List[Event]:
        now = now_utc or _now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        dated_events = (
            db.query(Event)
            .filter(
                Event.is_recurring.is_(False),
                or_(
                    and_(Event.start_datetime >= start_of_day, Event.start_datetime < end_of_day),
                    and_(Event.end_datetime.isnot(None), Event.start_datetime < end_of_day, Event.end_datetime >= start_of_day),
                ),
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .all()
        )
        recurring_events = [event for event in get_recurring_events(db) if _matches_recurrence(event, now)]
        combined_by_id: Dict[int, Event] = {event.id: event for event in dated_events}
        for event in recurring_events:
            combined_by_id.setdefault(event.id, event)
        return sorted(combined_by_id.values(), key=lambda event: (event.start_datetime or datetime.min, event.id))

    def search_events(db: Session, query: str, *, limit: int = 10, offset: int = 0) -> List[Event]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return []
        like_pattern = f"%{cleaned_query}%"
        return (
            db.query(Event)
            .filter(
                or_(
                    Event.name.ilike(like_pattern),
                    Event.description.ilike(like_pattern),
                    Event.category.ilike(like_pattern),
                    Event.special_notes.ilike(like_pattern),
                )
            )
            .order_by(Event.start_datetime.asc(), Event.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
            .all()
        )
 
4. 4B/week7/migrations/env.py
 
    import os
    import sys
    from pathlib import Path
    from alembic import context
    from sqlalchemy import engine_from_config, pool
    config = context.config
    config_file = Path(config.config_file_name).resolve()
    script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
    week_dir = script_location.parent
    if str(week_dir) not in sys.path:
        sys.path.insert(0, str(week_dir))
    _models = sys.modules.get("4B.week7.database.models") or sys.modules.get("database.models")
    if _models:
        Base = _models.Base
        if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
            import database.schema
    else:
        from database.models import Base
        import database.schema
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        config.set_main_option("sqlalchemy.url", db_url)
    target_metadata = Base.metadata

    def run_migrations_offline() -> None:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online() -> None:
        connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
 
5. 4B/week7/migrations/versions/003_add_events_table.py
 
    from typing import Sequence, Union
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql
    revision: str = "003"
    down_revision: Union[str, None] = "002"
    branch_labels: Union[str, Sequence[str], None] = None
    depends_on: Union[str, Sequence[str], None] = None
    event_source_site_enum = postgresql.ENUM(
        "radhakrishnatemple",
        "jkyog",
        name="event_source_site",
        create_type=True,
    )

    def upgrade() -> None:
        event_source_site_enum.create(op.get_bind(), checkfirst=True)
        op.create_table(
            "events",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("start_datetime", sa.DateTime(), nullable=False),
            sa.Column("end_datetime", sa.DateTime(), nullable=True),
            sa.Column("location", sa.Text(), nullable=True),
            sa.Column("venue_details", sa.Text(), nullable=True),
            sa.Column("parking_notes", sa.Text(), nullable=True),
            sa.Column("food_info", sa.Text(), nullable=True),
            sa.Column(
                "sponsorship_data",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("image_url", sa.Text(), nullable=True),
            sa.Column("source_url", sa.Text(), nullable=False),
            sa.Column("source_site", event_source_site_enum, nullable=False),
            sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("recurrence_pattern", sa.Text(), nullable=True),
            sa.Column("category", sa.Text(), nullable=True),
            sa.Column("special_notes", sa.Text(), nullable=True),
            sa.Column("scraped_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("dedup_key", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
            sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
            sa.UniqueConstraint("source_site", "source_url", name=op.f("uq_events_source_site_source_url")),
        )
        op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
        op.create_index(op.f("ix_events_name"), "events", ["name"])
        op.create_index(op.f("ix_events_category"), "events", ["category"])
        op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
        op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])

    def downgrade() -> None:
        op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
        op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
        op.drop_index(op.f("ix_events_category"), table_name="events")
        op.drop_index(op.f("ix_events_name"), table_name="events")
        op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
        op.drop_table("events")
        event_source_site_enum.drop(op.get_bind(), checkfirst=True)
 
6. 4B/week7/scripts/__init__.py
 
    """Week 7 database-side scripts."""
 
7. 4B/week7/scripts/seed_from_scraped_json.py
 
    from __future__ import annotations
    import sys
    from pathlib import Path
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    import json
    from typing import Any, Dict, List
    from sqlalchemy.orm import Session
    try:
        from ..database.event_storage import upsert_events
    except ImportError:
        from database.event_storage import upsert_events

    def _load_input(path: Path) -> List[Dict[str, Any]]:
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            events = payload.get("events", [])
        elif isinstance(payload, list):
            events = payload
        else:
            raise ValueError("Input JSON must be a list or an object with an events key")
        if not isinstance(events, list):
            raise ValueError("events must be a list")
        return [item for item in events if isinstance(item, dict)]

    def seed_from_file(db: Session, input_path: str) -> Dict[str, int]:
        events = _load_input(Path(input_path).resolve())
        stats = upsert_events(db, events)
        stats["input_count"] = len(events)
        return stats
 
8. 4B/week7/scripts/seed_database.py
 
    from __future__ import annotations
    import sys
    from pathlib import Path
    _week_dir = Path(__file__).resolve().parent.parent
    if str(_week_dir) not in sys.path:
        sys.path.insert(0, str(_week_dir))
    import argparse
    try:
        from ..database.models import SessionLocal, init_db
        from .seed_from_scraped_json import seed_from_file
    except ImportError:
        from database.models import SessionLocal, init_db
        from scripts.seed_from_scraped_json import seed_from_file

    def main() -> None:
        parser = argparse.ArgumentParser(description="Seed Week 7 events table from scraped JSON")
        parser.add_argument(
            "--input",
            default=str(Path(__file__).resolve().parents[1] / "data" / "scraped_events.json"),
            help="Path to scraped events JSON",
        )
        args = parser.parse_args()
        init_db()
        db = SessionLocal()
        try:
            stats = seed_from_file(db, args.input)
        finally:
            db.close()
        print("Seed complete")
        print(f"Input events: {stats['input_count']}")
        print(f"Inserted: {stats['inserted']}")
        print(f"Updated: {stats['updated']}")
        print(f"Failed: {stats['failed']}")

    if __name__ == "__main__":
        main()
 
9. 4B/week7/tests/conftest.py
 
    import os
    import sys
    from pathlib import Path

    def pytest_configure() -> None:
        week7_dir = Path(__file__).resolve().parents[1]
        if str(week7_dir) not in sys.path:
            sys.path.insert(0, str(week7_dir))
        os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
 
10. 4B/week7/tests/test_event_storage.py
 
    from datetime import datetime, timedelta, timezone
    import pytest
    from database.event_storage import build_dedup_key, is_event_stale, normalize_event_payload

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
                {"name": "Gold Sponsor", "amount": "$501", "link": "https://example.org/gold"}
            ],
        }
        normalized = normalize_event_payload(payload)
        assert normalized["name"] == "Health Fair"
        assert normalized["source_site"].value == "jkyog"
        assert normalized["start_datetime"].year == 2026
        assert normalized["dedup_key"]
        assert normalized["sponsorship_data"][0]["name"] == "Gold Sponsor"

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
        with pytest.raises(ValueError):
            normalize_event_payload(payload)

    def test_is_event_stale_true_when_older_than_threshold() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        old = now - timedelta(days=31)
        assert is_event_stale(old, now_utc=now, stale_after_days=30) is True

    def test_is_event_stale_false_when_recent() -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        recent = now - timedelta(days=10)
        assert is_event_stale(recent, now_utc=now, stale_after_days=30) is False
 
11. 4B/week7/tests/test_migrations_events.py
 
    from pathlib import Path

    def test_events_migration_exists() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        assert migration_path.is_file()

    def test_events_migration_revision_chain() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert 'revision: str = "003"' in content
        assert 'down_revision: Union[str, None] = "002"' in content

    def test_events_migration_indexes_present() -> None:
        migration_path = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
            / "003_add_events_table.py"
        )
        content = migration_path.read_text(encoding="utf-8")
        assert "ix_events_start_datetime" in content
        assert "ix_events_name" in content
        assert "ix_events_category" in content
        assert "ix_events_is_recurring" in content
        assert "ix_events_dedup_key" in content
 
12. 4B/week7/data/.gitkeep
 
    empty fil

GitHub Copilot: Checked all 12 files you pasted. Overall, this is solid and much better aligned with Week 7 ownership. I do not see obvious import-path breakage in the current code set.

**Findings (by severity)**

1. Medium: Hard dependency on DATABASE_URL at import time can still cause startup/import failures in some contexts.  
   - models.py  
   - Engine is created when module imports, and _get_database_url raises immediately if env var is missing.  
   - Impact: commands that import models before env is set can fail even if alembic.ini exists.

2. Medium: Missing validation for end time before start time.  
   - 4B/week7/database/event_storage.py  
   - normalize_event_payload parses both times but does not reject end_datetime < start_datetime.  
   - Impact: invalid event windows can be stored and break downstream sorting/UX assumptions.

3. Low: Migration test is string-based and brittle.  
   - 4B/week7/tests/test_migrations_events.py  
   - Asserting exact text like revision type annotation can fail on harmless formatting changes.  
   - Impact: flaky test maintenance, not runtime breakage.

**What looks correct**

1. Event model and enum wiring are consistent between schema and migration.  
   - schema.py  
   - 4B/week7/migrations/versions/003_add_events_table.py

2. Seed script import strategy is migration-safe for both module and direct execution.  
   - seed_database.py  
   - 4B/week7/scripts/seed_from_scraped_json.py

3. Health check now includes events probe, which is correct for Week 7.  
   - models.py

4. Event storage core (dedup, upsert, stale computation, sponsorship contract) is implemented cleanly.  
   - 4B/week7/database/event_storage.py

If you want, next I can do a strict sponsor-readiness pass and give only must-fix items before final commit.

User: Findings (by severity)

Medium: Hard dependency on DATABASE_URL at import time can still cause startup/import failures in some contexts.

models.py
Engine is created when module imports, and _get_database_url raises immediately if env var is missing.
Impact: commands that import models before env is set can fail even if alembic.ini exists.
Medium: Missing validation for end time before start time.

4B/week7/database/event_storage.py
normalize_event_payload parses both times but does not reject end_datetime < start_datetime.
Impact: invalid event windows can be stored and break downstream sorting/UX assumptions.
Low: Migration test is string-based and brittle.
4B/week7/tests/test_migrations_events.py
Asserting exact text like revision type annotation can fail on harmless formatting changes.
Impact: flaky test maintenance, not runtime breakage.

Elaborate these clearly, also let me know if the files can be created or modified

GitHub Copilot: Yes, these files can be modified (and new files can be created) in your current Week 7 structure.  
For your current set, only modifications are needed, not new files.

Here is a clear breakdown of each finding and what to change.

**1. Medium: DATABASE_URL hard dependency at import time**
- File: models.py
- Current behavior:
  - The engine is created at module import time.
  - Engine creation calls _get_database_url immediately.
  - If DATABASE_URL is not set yet, import fails before runtime flow can recover.
- Why this matters:
  - Some tools/scripts import modules before env vars are loaded.
  - This can fail local scripts, tests, or one-off commands even if Alembic config exists.
- Practical fix:
  - Delay engine creation until first DB use, or provide a fallback URL only in controlled dev/test contexts.
  - Keep production strict, but avoid hard crash during plain imports.
- Recommended change scope:
  - Modify only models.py

**2. Medium: Missing end-before-start validation**
- File: 4B/week7/database/event_storage.py
- Current behavior:
  - normalize_event_payload parses start_datetime and end_datetime.
  - It does not reject cases where end_datetime is earlier than start_datetime.
- Why this matters:
  - Invalid event windows can be stored.
  - Later queries and UI sorting logic assume chronological validity.
- Practical fix:
  - In normalize_event_payload, add:
    - if end_datetime is not None and end_datetime < start_datetime: raise ValueError
- Recommended change scope:
  - Modify only 4B/week7/database/event_storage.py
  - Add one test in 4B/week7/tests/test_event_storage.py for this invalid case

**3. Low: Migration test is brittle due to exact string assertions**
- File: 4B/week7/tests/test_migrations_events.py
- Current behavior:
  - Test checks exact string text for revision and down_revision declarations.
- Why this matters:
  - Harmless formatting/type-annotation changes can fail tests.
  - This increases maintenance noise without improving runtime safety.
- Practical fix:
  - Parse values more flexibly (regex for revision/down_revision), or import migration module and assert its variables directly.
- Recommended change scope:
  - Modify only 4B/week7/tests/test_migrations_events.py

**Can files be created or modified?**
- Yes, absolutely.
- For your three findings:
  - Required: modify existing files.
  - Optional: no new files required unless you want an extra dedicated validation test file.

If you want, I can give you exact copy-paste patch blocks for these three fixes in final sponsor-ready form.

User: can you go through my files and folderws once and let me know if htey meet my requriemetns:

Hi Group 4B,

Hope midterms went well! This week we're shifting into real-world data engineering — you're building the event data pipeline that makes the bot temple-aware.

WEEK 7 THEME: Event Data Pipeline — Web Scraping, Storage & API
DEADLINE: Wednesday, April 2, 2026 at 11:59 PM CST

THE CHALLENGE:
The Radha Krishna Temple of Dallas publishes events on their website, but there's no API or calendar feed. You need to:
1. SCRAPE real event data from live websites
2. STORE it in a structured database
3. SERVE it through API endpoints the bot can query

By Friday's demo, someone should be able to hit /events/today and get real temple events back.

DATA SOURCES TO SCRAPE:
• radhakrishnatemple.net — Homepage event carousel + individual event detail pages (schedules, parking info, sponsorship tiers, food, special notes)
• jkyog.org/upcoming_events — Organization-wide calendar (filter for Dallas/Allen, TX events at Radha Krishna Temple of Dallas, 1450 North Watters Road, Allen, TX 75013)

Current events on the temple site: Ram Navami (Mar 26-29), Chaitra Navratri (Mar 19-29), Hanuman Jayanti (Apr 1 & 4), Health Fair (Apr 4), Annamacharya Aradhanotsavam (Apr 4)

WHAT MAKES THIS HARD:
• No API — pure HTML parsing
• Inconsistent page formatting across events
• Multi-day events with different daily sub-schedules
• Two websites with completely different HTML structures
• Must handle gracefully: site down, HTML changes, no upcoming events

────────────────────────────
INDIVIDUAL ASSIGNMENTS
────────────────────────────

SYSHA SHARMA (Team Lead) — Scraper Architecture & Orchestration
• Build event_scraper module: scrape radhakrishnatemple.net homepage → extract event carousel → follow each event link → scrape detail pages → scrape jkyog.org/upcoming_events for Dallas events
• Output: structured JSON matching Team 4A's event data model
• Configurable target URLs, scrape intervals, user-agent, request delays (be respectful to their servers)
• Error handling: site down, HTML structure changes, timeouts
• Orchestration: scrape_events script (scrape both sites → output JSON) + seed_database script (JSON → database)

ROHAN BHARGAV KOTHAPALLI — /events API Endpoints + Escalation Auth Fix
• Implement API endpoints:
  - GET /events — All upcoming events (pagination: ?limit=10&offset=0)
  - GET /events/today — Today's events + active recurring programs
  - GET /events/{id} — Single event detail
  - GET /events/search?q={query} — Case-insensitive search by name/description
  - GET /events/recurring — All recurring programs
  - Proper error responses: 404, 400, 200 with empty list
• TECH DEBT (Security Blocker): Add Bearer token auth to ALL /escalations endpoints (POST, GET, PUT). Reject unauthenticated with 401. This was flagged Week 6 — must be fixed.
• Integration: wire scraper → database → API. Demo /events/today with real data.

CHAKRADHAR REDDY GUMMAKONDA — Event Database Schema & Storage Layer
• Design events table: id, name, description, start_datetime, end_datetime, location, venue_details, parking_notes, food_info, sponsorship_data (jsonb), image_url, source_url, source_site (enum), is_recurring, recurrence_pattern, category, special_notes, scraped_at, created_at, updated_at
• Indexes on: start_datetime, name, category, is_recurring
• Seed script with REAL scraped data from both websites
• Upsert logic (no duplicates on re-scrape), deduplication across sources, stale data flagging (scraped_at > 30 days)

SUBODH KRISHNA NIKUMBH — Event Service Wrapper & Test Suite
• EventService: getUpcomingEvents(limit, offset), getTodayEvents(), searchEvents(query), getEventById(id), getRecurringSchedule()
• Caching layer: cache frequent queries, invalidate on re-scrape
• 20+ tests covering: scraper parsing (use real HTML fixtures from both sites), malformed HTML, service cache hit/miss, stale data, pagination, API endpoints, search relevance
• Integration test: scrape → store → query → verify end-to-end

LEENA HUSSEIN — Stripe Webhooks Completion + Event Pipeline Documentation
• TECH DEBT: Handle payment_intent.succeeded and payment_intent.payment_failed webhooks, Stripe-Signature verification, test coverage for both paths
• Event Pipeline Docs: Admin runbook (how to run scraper, trigger refresh, verify data), architecture diagram (website → scraper → DB → API → bot), troubleshooting guide (HTML changes, scrape failures, stale data), all new environment variables documented

────────────────────────────
FRIDAY DEMO TARGET (April 4)
────────────────────────────
Be ready to show:
1. Run the scraper → real JSON from temple websites
2. Query the database → stored events
3. GET /events/today → real events for that day
4. Search "Hanuman Jayanti" → correct result
5. /escalations with auth → 401 without token, 200 with token

Feedback i got from sysha:
Here’s a concise review after pulling Chakradhar’s work.
What looks good and in sync
seed_database.py → seed_from_scraped_json.py → upsert_events: The seed path is wired correctly and matches your scraper default: 4B/week7/data/scraped_events.json.
_load_input: Accepts either a top-level list or {"events": [...]}, which matches scrape_all_events() output (wrapper with events + errors).
database/schema.py Event + EventSourceSite: Aligns with what event_storage.normalize_event_payload expects (radhakrishnatemple / jkyog, sponsorship_data as JSONB list, etc.).
database/models.py: Health check probes events alongside escalations — consistent with the new table.
migrations/versions/003_add_events_table.py: Present and matches the model shape (indexes, enum, unique constraints).
Tests: validation_tests/ exercises normalize_event_payload, dedup key, stale logic, and migration file presence — matches Chakradhar’s design.
Main discrepancy (you should address on the scraper side)
start_datetime is required in normalize_event_payload (and NOT NULL in the DB). Your scrapers often emit start_datetime: null when they don’t find an ISO-like string in the page text:
radhakrishnatemple.pyLines 113-136
    # Datetime parsing is highly inconsistent; emit nulls unless we find ISO-like strings.
    ...
        "start_datetime": start_dt,
        "end_datetime": end_dt,
 
Same pattern in jkyog.py (start_dt can stay None).
Effect: upsert_events will not crash the whole seed; those rows go to failed in stats. For a working demo (/events/today with real rows), you need reliable start_datetime parsing (or a documented fallback, e.g. event date range from structured fields on the site).
Smaller notes
Plan vs repo layout: The plan mentioned events/storage/ for upsert helpers; Chakradhar implemented database/event_storage.py instead. Functionally fine; only the folder ownership in the plan differs.
Pytest discovery: Event DB tests live under validation_tests/, not tests/. If CI only runs pytest 4B/week7/tests, those tests won’t run unless you also run pytest 4B/week7/validation_tests or pytest 4B/week7.
events/schemas/event_payload.py: ScrapedEventPayload requires start_datetime as a real datetime. Raw scraper dicts with null or string-only dates don’t match that model until you normalize them — fine if you don’t use this model on raw output yet; worth aligning when you add validation.
Bottom line
Chakradhar’s layer is consistent internally and wired to your seed path and JSON shape, except for the start_datetime requirement vs nullable scraper output. Your next meaningful change is improving date/time extraction (or fallbacks) so most scraped events pass normalize_event_payload and insert instead of failing.

GitHub Copilot: I’m validating your current Week 7 workspace against the assignment checklist, first by confirming structure and then by checking whether each required capability is implemented or still at risk.

[Internal local file-read trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

Quick update: the required files now exist, including event storage, migration 003, and both seed scripts. Next I’m checking the actual code paths for requirements coverage and demo risk points, especially real scraping output compatibility.

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

I’ve confirmed your storage layer is present and coherent; now I’m checking scraper output quality, API endpoints, and escalation auth to verify Friday demo requirements end to end.

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal code-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

I found a major gap: events API endpoints are currently missing from the app, so I’m now verifying scraper orchestration and auth wiring to give you a strict requirement-by-requirement status.

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal code-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

Progress update: I verified the seed pipeline and schema contract; next I’m checking whether demo-critical endpoints, webhook debt, and documentation deliverables are actually present so you get a true pass/fail matrix.

[Internal local file-read trace removed]

[Internal code-search trace removed]

[Internal file-search trace removed]

Searched for text `pytest|test|fixture|scrape|events` (`**/4B/week7/README.md`), 21 results

[Internal local file-read trace removed]

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal code-search trace removed]

Searched for text `start_datetime is required|if not start_datetime` (`**/4B/week7/database/event_storage.py`), 2 results

Searched for text `def test_` (`**/4B/week7/**/*.py`), 47 results

[Internal code-search trace removed]

Short answer: not fully yet. Your Week 7 workspace is strong on the Event DB layer, but the full assignment and Friday demo criteria are only partially met.

**Critical Gaps (must-fix for requirement compliance)**

1. Missing /events API endpoints
- I could not find any route definitions for /events, /events/today, /events/search, /events/recurring, or /events/{id}.
- Main app currently wires only escalations router: main.py
- Existing routes shown are health and webhook, not events: main.py, main.py

2. Escalations Bearer auth blocker is still open
- Escalations endpoints currently depend on DB session only, with no Bearer auth dependency.
- Create/get/resolve endpoints: escalations.py, escalations.py, escalations.py
- Dependency shape currently: escalations.py, escalations.py, escalations.py

3. Scraper-to-storage mismatch can cause many seed failures
- Scrapers can emit null start_datetime:
  - radhakrishnatemple.py
  - jkyog.py, jkyog.py
- Storage requires start_datetime and rejects missing values:
  - event_storage.py, event_storage.py

4. Real scraped seed data file is not present in repo
- Data folder currently has only placeholder: data
- For the demo target, you need real JSON output from scraper run (not just .gitkeep).

**What is already good (your layer is mostly in place)**

1. Event schema and constraints are implemented
- Event model + enum + unique constraints/indexed fields: schema.py
- Migration chain includes events table: 003_add_events_table.py

2. Upsert + dedup + stale computation are implemented
- Core storage logic: event_storage.py

3. Seed pipeline wiring exists and is import-safe
- Orchestrator: seed_database.py
- Loader/upsert bridge: seed_from_scraped_json.py
- Scrape orchestrator script exists: scrape_events.py

**Requirement-by-requirement status**

1. Chakradhar (Event DB Schema & Storage): Mostly met, with one demo risk
- Met: schema, indexes, upsert/dedup, stale logic.
- Risk: real-data seeding success depends on fixing datetime extraction.

2. Sysha (scraper architecture/orchestration): Partially met
- Met: dual-source scraper structure, config/env options, respectful client, output wrapper.
- Gap: datetime extraction quality is insufficient for reliable inserts.

3. Rohan (/events endpoints + escalation auth): Not met
- /events endpoints not present.
- Bearer auth for escalations not present.

4. Subodh (EventService + cache + event integration tests): Not met from current files
- I did not find an EventService implementation with those methods/caching in Week 7.
- Tests exist, but mostly wrapper-focused; not the required event-pipeline/service coverage.

5. Leena (Stripe webhook debt + event pipeline docs): Not met/unclear from current code
- I did not find handlers for payment_intent.succeeded/payment_intent.payment_failed or Stripe-Signature verification paths.
- Docs folder exists, but no obvious Week 7 event runbook/architecture/troubleshooting package dedicated to this deliverable set.

If you want, I can next give you a strict “minimum edits to pass by deadline” checklist in priority order (P0 today, P1 tomorrow) mapped to each teammate owner.

User: Can you check my area of focus please. I'm Chakradhar and also check Sysha's feedback

GitHub Copilot: I’ll do a focused Chakradhar-only verification against Week 7 requirements and explicitly validate each point in Sysha’s feedback with file-level evidence.

[Internal file-search trace removed]

[Internal code-search trace removed]

Searched for text `def seed_from_file|events = _load_input|upsert_events` (`**/4B/week7/scripts/seed_from_scraped_json.py`), 5 results

[Internal code-search trace removed]

Searched for text `def upsert_event|def upsert_events|def is_event_stale|start_datetime is required` (`**/4B/week7/database/event_storage.py`), 4 results

I confirmed your DB/seed path pieces; I’ll do one last quick check on Sysha’s specific mismatch points (nullable scrape datetimes and test folder placement) and then give a focused verdict for your ownership.

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

**Focused Review: Chakradhar Scope + Sysha Feedback**

**Findings (ordered by severity)**

1. High: Real-data demo risk remains due to scraper datetime nullability vs DB requirement.
- Storage enforces required start_datetime at ingest: event_storage.py.
- Both scrapers intentionally emit null when parsing is uncertain:
  - radhakrishnatemple.py
  - radhakrishnatemple.py
  - jkyog.py
  - jkyog.py
- Impact: many rows can go to failed during seed, reducing usable data for /events/today demo.

2. Medium: Real scraped JSON input file is not present in repo snapshot.
- Seed default expects this path: seed_database.py.
- Current data folder has no scraped_events.json committed: data.
- Impact: teammates running seed without first scraping will fail or seed nothing.

3. Low: Event validation tests are outside tests folder.
- Event tests exist here:
  - test_event_storage.py
  - test_migrations_events.py
- No matching event test file under main tests folder.
- Impact: if CI runs only tests path, your event tests can be skipped.

**What is solid in your ownership (Chakradhar)**

1. Events schema is complete and aligned.
- Required constraints and core columns are present:
  - dedup unique: schema.py
  - source-site+url unique: schema.py
  - required start datetime: schema.py
  - sponsorship_data JSONB list field: schema.py

2. Upsert/dedup/stale logic is implemented.
- Upsert single and batch:
  - event_storage.py
  - event_storage.py
- Stale computation helper:
  - event_storage.py

3. Migration for events table is present and wired.
- 003_add_events_table.py

4. Seed pipeline wiring is correct.
- Seed orchestrator calls file-loader then upsert:
  - seed_database.py
  - seed_from_scraped_json.py
  - seed_from_scraped_json.py

**Sysha feedback validation**
- Sysha’s main feedback is accurate: your DB/seed/storage layer is internally consistent, and the biggest integration gap is start_datetime quality from scrapers.
- Her note on tests location is also accurate: event tests are in validation_tests, not tests.
- Her note on event payload model strictness is valid: raw scrape output can violate required datetime shape before normalization.

**Bottom line for your area**
- Your core deliverable is mostly done and technically strong.
- To make it demo-safe, the highest-priority dependency is improved scraper datetime extraction or fallback policy so rows actually insert at high success rate.

User: Chakradhar’s layer is consistent internally and wired to your seed path and JSON shape, except for the start_datetime requirement vs nullable scraper output.

Do you recommend this change?

GitHub Copilot: Yes, I recommend addressing the start_datetime gap. Your storage layer is robust, but for a successful demo and real data flow, you need to ensure that most scraped events have a valid start_datetime.

**Recommended change:**  
- Improve the scrapers to extract or infer start_datetime more reliably (e.g., fallback to event date ranges, parse from structured fields, or use heuristics if ISO strings are missing).
- If a date cannot be found, consider logging/skipping with a clear error, but avoid inserting nulls—your DB and upsert logic require this field.

**Why:**  
- Without this, many real events will fail to insert, and /events/today will return few or no results, hurting the demo and real-world utility.

**Summary:**  
Fixing start_datetime extraction in the scrapers is the most important next step for your layer to deliver real value and pass the integration demo.

User: Sysha’s main feedback is accurate: your DB/seed/storage layer is internally consistent, and the biggest integration gap is start_datetime quality from scrapers.
Her note on tests location is also accurate: event tests are in validation_tests, not tests.
Her note on event payload model strictness is valid: raw scrape output can violate required datetime shape before normalization.

Do you recommend this change?

Also, how does file location come into picture here?

GitHub Copilot: Yes, I recommend making those changes.

1. Start_datetime quality: Yes, fix it.
- This is the highest-impact integration fix because your DB layer correctly enforces required datetime.
- If scrapers keep emitting null, seed success drops and demo endpoints depend on sparse/failed data.

2. Test location: Yes, align it.
- Keeping event tests only in test_event_storage.py and test_migrations_events.py is fine only if CI runs that folder.
- If teammates/CI run only tests, your event tests are silently skipped.

3. Payload strictness: Yes, keep strict storage contract.
- Strict validation in event_storage.py is correct.
- The fix belongs in scraper normalization quality before seeding, not by loosening DB constraints.

How file location matters here:

1. Test discovery and CI pass/fail
- Most pipelines run fixed commands like pytest on tests.
- Tests outside that path might never execute, so regressions go undetected.

2. Import behavior and script execution
- Script/module imports depend on package layout and run mode.
- Your seed scripts are already handling both module and direct execution via path bootstrap in:
  - seed_database.py
  - seed_from_scraped_json.py

3. Team ownership clarity
- Where code lives signals ownership and expected integration point.
- Your choice of event_storage.py is functionally correct; mismatch is mostly documentation/expectation noise.

4. Operational defaults
- Seed default input path is hardcoded to 4B/week7/data/scraped_events.json from seed_database.py.
- If that file is not generated before seed, flow fails or does nothing useful.

If you want a practical convention: keep source where it is, and ensure CI runs pytest on whole week7 so both tests and validation_tests are included.

User: i agree with 1, 2- test location (i'll talk about it with sysha), 3- you want me to store event_storage.py in database or events/storage. (If events/storage, i guess few files needs to be changed right? to prevent import errors)

GitHub Copilot: I’ll quickly map every current reference to event_storage so I can give you a precise, import-safe recommendation on whether to keep it in database or move it to events/storage.

[Internal code-search trace removed]

Recommendation: keep it in event_storage.py.

Why this is the best choice now:
1. Your module is DB-centric (schema-bound normalization, upsert, query helpers), so database is a natural home.
2. Current imports are already stable and minimal.
3. Moving it now adds churn and import-risk without functional gain before deadline.

Current references you would have to update if you move to events/storage:
1. seed_from_scraped_json.py
2. seed_from_scraped_json.py
3. test_event_storage.py

If you still want events/storage, yes, a few changes are required to avoid import errors:
1. Create package path:
- events
- storage
- add __init__.py files

2. Move file:
- from event_storage.py
- to 4B/week7/events/storage/event_storage.py

3. Update imports in the 3 files above.

4. Optional compatibility shim (recommended during transition):
- keep a tiny event_storage.py that re-exports from events/storage so old imports keep working temporarily.

Bottom line:
- For deadline safety: keep it in database.
- For long-term domain organization: move later with a compatibility shim and one cleanup PR.

User: so, i want to move event_storage.py from database to events/storage.

Do you recommend this change?

also, make code changes in files where there will be import error.

i guess you gave 3 files above whihc might change, so please take a look at it

GitHub Copilot: You want an actual move, so I’m now updating the module location and every known import reference to keep runtime and tests import-safe.

[Internal code-search trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

I found exactly three active import references, so I’m now moving the module and patching those references in one pass to avoid breakage.

Generating patch (399 lines) in []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] []([local-path-redacted]

```

```

```

```

```

```

```

```

Checked []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] no problems found

[Internal code-search trace removed]

[Internal code-search trace removed]

Implemented the move and patched import paths so you should not get import errors from this relocation.

What I changed:

1. Moved storage module to events domain
- Added event_storage.py
- Added __init__.py
- Removed 4B/week7/database/event_storage.py

2. Updated seed import path
- Updated seed_from_scraped_json.py
- Updated seed_from_scraped_json.py

3. Updated validation test import path
- Updated test_event_storage.py

Validation result:

1. No diagnostics errors were reported in the changed files.
2. No remaining references to old database.event_storage imports were found.
3. New references to events.storage.event_storage are present in expected files.

I recommend this move now because you explicitly want domain ownership under events, and we updated the known import points safely.  
If you want, I can next run a focused smoke pass for scrape then seed command flow to verify runtime import behavior too.

Made changes.

User: can you check is sysha's feedback is done

GitHub Copilot: I’m running a targeted checklist against each item in Sysha’s feedback so I can give you a clear done/not-done status with proof.

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal code-search trace removed]

I confirmed most of Sysha’s points are still true after your module move; I’m doing one final check on the two unresolved points she called out (nullable scrape datetimes and test folder placement).

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal file-search trace removed]

[Internal local file-read trace removed]

Yes, Sysha’s feedback is still accurate overall.  
After your move to events/storage, here is exact status:

1. Done: seed path wiring is correct.
- Default path still points to scraped_events.json:
  - seed_database.py
- Wrapper JSON shape support is present:
  - seed_from_scraped_json.py
- Seed flow to upsert is wired:
  - seed_from_scraped_json.py
  - seed_from_scraped_json.py
  - seed_from_scraped_json.py

2. Done: schema/storage consistency is good.
- Event model + required start_datetime + sponsorship JSONB are present:
  - schema.py
  - schema.py
  - schema.py
- Upsert logic exists in new location:
  - event_storage.py

3. Done: DB health probe includes events.
- models.py
- models.py

4. Done: migration 003 exists.
- 003_add_events_table.py

5. Still open (main integration gap): scraper datetime quality.
- Scrapers still emit null start_datetime when parsing fails:
  - radhakrishnatemple.py
  - radhakrishnatemple.py
  - jkyog.py
  - jkyog.py
- Storage still enforces required datetime (correctly):
  - event_storage.py

6. Still open (process/CI risk): test location note remains true.
- Event tests are in validation_tests:
  - test_event_storage.py
  - test_migrations_events.py
- No matching event storage test under tests folder:
  - tests

7. Still valid: payload strictness note.
- Payload model requires start_datetime datetime:
  - event_payload.py
- So raw scraper output with null datetime is incompatible until normalized/fixed upstream.

Bottom line: your Chakradhar layer is done and clean; Sysha’s two risk flags (datetime extraction and test-folder execution scope) are still pending.

User: except for the start_datetime requirement vs nullable scraper output. Your next meaningful change is improving date/time extraction (or fallbacks) so most scraped events pass normalize_event_payload and insert instead of failing.

can you focus on this. 

Main discrepancy (you should address on the scraper side)
start_datetime is required in normalize_event_payload (and NOT NULL in the DB). Your scrapers often emit start_datetime: null when they don’t find an ISO-like string in the page text:
radhakrishnatemple.pyLines 113-136
    # Datetime parsing is highly inconsistent; emit nulls unless we find ISO-like strings.
    ...
        "start_datetime": start_dt,
        "end_datetime": end_dt,
 
Same pattern in jkyog.py (start_dt can stay None).
Effect: upsert_events will not crash the whole seed; those rows go to failed in stats. For a working demo (/events/today with real rows), you need reliable start_datetime parsing (or a documented fallback, e.g. event date range from structured fields on the site).
Smaller notes
Plan vs repo layout: The plan mentioned events/storage/ for upsert helpers; Chakradhar implemented database/event_storage.py instead. Functionally fine; only the folder ownership in the plan differs.
Pytest discovery: Event DB tests live under validation_tests/, not tests/. If CI only runs pytest 4B/week7/tests, those tests won’t run unless you also run pytest 4B/week7/validation_tests or pytest 4B/week7.
events/schemas/event_payload.py: ScrapedEventPayload requires start_datetime as a real datetime. Raw scraper dicts with null or string-only dates don’t match that model until you normalize them — fine if you don’t use this model on raw output yet; worth aligning when you add validation.
Bottom line
Chakradhar’s layer is consistent internally and wired to your seed path and JSON shape, except for the start_datetime requirement vs nullable scraper output. Your next meaningful change is improving date/time extraction (or fallbacks) so most scraped events pass normalize_event_payload and insert instead of failing.

should i make a change or sysha? is it recommended to change my file or shysha's python script?

GitHub Copilot: I’m checking the current scraper and storage files as they exist now so I can give you an ownership-safe recommendation on exactly who should change what.

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

[Internal local file-read trace removed]

Yes, this specific fix should be owned by Sysha (scraper side), not by your storage layer.

Why:
1. The null value is produced in scraper code:
- radhakrishnatemple.py
- radhakrishnatemple.py
- jkyog.py
- jkyog.py

2. Your storage contract is intentionally strict and correct:
- event_storage.py

3. Seed pipeline is already wired correctly to your upsert logic:
- seed_from_scraped_json.py

Recommendation:
1. Sysha should improve date extraction/fallback in scraper outputs so start_datetime is almost always present.
2. You should keep start_datetime required in storage and DB (do not loosen it).
3. Optional support from you: ask Sysha to follow a clear fallback order:
- ISO datetime in text
- date range/day text parse (month/day/year)
- if time missing, use noon local time for that date
- only then skip with explicit error record

So: change Sysha’s scraper scripts for this issue; do not weaken your file.

User: You should keep start_datetime required in storage and DB (do not loosen it).

why shouldn't i loosen it? is it better to loosen or not loosen it?

GitHub Copilot: Not loosen is the better choice for your case.

Why keeping start_datetime required is better:

1. It protects data quality at the source of truth.
- If you allow null, bad scrape output silently enters DB and looks “valid enough,” which hides parser issues.
- Right now your storage correctly fails fast, so scraper issues are visible and fixable.

2. Your demo endpoints depend on time semantics.
- Endpoints like today/upcoming fundamentally require a start time to rank/filter correctly.
- Null-heavy rows make /events/today and sorting behavior unreliable.

3. Dedup and event identity are time-dependent.
- Your dedup strategy includes name + start_datetime + location, so missing datetime weakens duplicate detection and can create noisy repeats.
- This directly hurts rescrape behavior.

4. Contract consistency across layers.
- Schema/payload/storage currently align on start_datetime being required.
- Loosening DB while payload/service still assumes datetime creates mixed semantics and future bugs.

5. Operational hygiene.
- Hard requirements force scraper improvements now, instead of accumulating “unknown date” debt that is painful to clean later.

When would loosening be acceptable:
1. Only as a short-lived emergency bridge.
2. If you add a strict secondary state like date_confidence or ingestion_status, and keep those records out of /today and /upcoming until resolved.
3. If you set a clear rollback plan to restore NOT NULL quickly.

Practical recommendation:
1. Keep start_datetime required in storage and DB.
2. Fix scraper extraction/fallbacks (Sysha side).
3. If needed for interim demo stability, skip events without datetime and log them in scrape errors rather than inserting partial rows.

So overall: do not loosen. It is the safer, cleaner, and more maintainable choice for your pipeline.

User: give me a commit summary and description for the tasks i did, moving the files

GitHub Copilot: I’ll quickly check your current git changes so the commit summary matches exactly what you moved and avoids missing files.

Read changed files in the active git repository

Commit title suggestion:
refactor(events): move event storage module to events/storage and update imports

Commit description suggestion:
- Moved event persistence helpers from 4B/week7/database/event_storage.py to event_storage.py to align code ownership under the events domain.
- Added package init for storage module at __init__.py.
- Updated seed pipeline imports to new module path in seed_from_scraped_json.py.
- Updated event storage validation test import path in test_event_storage.py.
- Removed legacy module at 4B/week7/database/event_storage.py after import migration.

Optional extended body (if you want more context in commit):
- This change is structural only; event storage logic behavior is unchanged.
- Purpose is to keep storage utilities close to scraper/service event modules and reduce cross-domain ambiguity.
- Import paths were updated to prevent runtime and test import errors after relocation.

User: Can you check now and let me know if everything's done?

Here are my results:
Seed complete
Input events: 22
Inserted: 11
Updated: 11
Failed: 0

python -m 4B.week7.scripts.seed_database
Seed complete
Input events: 22
Inserted: 0
Updated: 22
Failed: 0

GitHub Copilot: I’ll quickly verify your current Week 7 event flow artifacts (seed script wiring, storage imports, and scraped JSON datetime completeness) so I can confirm whether your scope is fully done.

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal code-search trace removed]

[Internal file-search trace removed]

[Internal code-search trace removed]

Quick update: your code wiring checks out and migration/schema constraints are still aligned; I’ll do one final diagnostics pass to confirm there are no editor-detected issues in your Week 7 event files.

Checked []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] []([local-path-redacted] no problems found

Yes, for your Chakradhar scope this now looks done.

What your results prove:
1. Seed succeeded with real payload and zero rejects:
- Input 22, Failed 0 means scraper output currently satisfies required DB contract (including start_datetime).
2. Upsert is working correctly:
- First run: Inserted 11, Updated 11
- Second run: Inserted 0, Updated 22
- This is expected idempotent behavior for re-seeding.

Quick verification from code state:
1. Seed imports now point to the moved storage module:
- seed_from_scraped_json.py
- seed_from_scraped_json.py

2. Storage still enforces strict required datetime:
- event_storage.py

3. DB schema and migration still align:
- schema.py
- schema.py
- 003_add_events_table.py

4. No diagnostics errors in checked files.

Bottom line:
- Your event DB/storage + seed pipeline is in good shape and working as intended.
- From your area of focus, this is ready.

User: so can i commit and push to team branch

GitHub Copilot: Yes, you can commit and push your work to the team branch.

Your latest seed runs are exactly what we want for your scope:
1. First run inserted/updated with 0 failures.
2. Second run was fully idempotent (all updates, no failures).

That combination is a strong sign your event storage + seed integration is stable.

Before push, do a quick final command sequence:
1. `git status`
2. `git add 4B/week7`
3. `git commit -m "refactor(events): move event storage module and update seed/test imports"`
4. `git push origin <team-branch>`

If you want, I can give you a tighter final commit message/body matching your exact changed files.

User: can you give me .md file of this chat transcript

GitHub Copilot: ```md
# Week 7 Chat Transcript (Group 4B)  
Date: 2026-03-31 to 2026-04-01  
Participants: User (Chakradhar), GitHub Copilot

---

## 1. Initial Goal
User asked for a migration-safe, import-error-free Week 7 setup review focused on Chakradhar’s ownership:
- Event DB schema
- Storage layer
- Seed path
- Upsert/dedup behavior
- No import errors after migration/copy from Week 6

---

## 2. Early Findings
Copilot reviewed workspace and identified:
- Week 7 initially had gaps/mismatches
- Missing or inconsistent event-related files were flagged at different points
- Seed script had fallback behavior that could hide missing storage imports
- Event table migration and storage wiring needed explicit verification

---

## 3. File-by-File Iteration
User pasted key files for review:
1. `database/schema.py`
2. `database/models.py`
3. `database/event_storage.py`
4. `migrations/env.py`
5. `migrations/versions/003_add_events_table.py`
6. `scripts/__init__.py`
7. `scripts/seed_from_scraped_json.py`
8. `scripts/seed_database.py`
9. `tests/conftest.py`
10. `tests/test_event_storage.py`
11. `tests/test_migrations_events.py`
12. `data/.gitkeep`

Copilot reviewed and highlighted:
- Medium: `DATABASE_URL` hard dependency at import in models
- Medium: no explicit validation for `end_datetime < start_datetime`
- Low: brittle string-based migration test assertions

---

## 4. Scope Validation Against Assignment
User asked for full alignment against Week 7 assignment and Sysha feedback.

Copilot confirmed:
- Chakradhar DB/storage layer was mostly correct and internally consistent
- Main integration risk was scraper output quality for `start_datetime`
- Event tests located under `validation_tests` (CI/discovery risk if only `tests` runs)
- Strict payload model and strict storage contract were acceptable and intentional

---

## 5. Ownership Decision (Who Should Fix Date Parsing?)
User asked whether to change storage contract or scraper output.

Decision:
- Keep `start_datetime` required in DB/storage
- Fix date extraction/fallback on scraper side (Sysha’s scope)
- Do **not** loosen DB constraints just to pass noisy scraper output

Rationale:
- Better data integrity
- Better `/events/today` correctness
- Better dedup quality
- Faster visibility of scraper regressions

---

## 6. Module Relocation Request
User requested moving `event_storage.py` from `database` to `events/storage` and fixing imports.

Copilot performed the move and updated references:
- Added `events/storage/event_storage.py`
- Added `events/storage/__init__.py`
- Updated seed import paths
- Updated validation test import path
- Removed old `database/event_storage.py`
- Checked diagnostics: no errors in changed files

---

## 7. Sysha Feedback Re-check
User asked if Sysha’s feedback was done.

Copilot verified:
- Most points were satisfied
- Remaining concern still valid: scraper may emit nullable `start_datetime` when extraction fails
- Test-location note remained valid as process/CI concern

---

## 8. Final Runtime Results Shared by User
User reported successful seed runs:

- Run 1:
  - Input events: 22
  - Inserted: 11
  - Updated: 11
  - Failed: 0

- Run 2:
  - Input events: 22
  - Inserted: 0
  - Updated: 22
  - Failed: 0

Copilot interpretation:
- Pipeline is working
- Upsert is idempotent
- No failed rows indicates current scraped payload quality is sufficient for storage contract

---

## 9. Final Recommendation
Copilot confirmed user can commit and push to team branch, with confidence for Chakradhar’s area:
- Event schema + migration aligned
- Storage/upsert logic aligned
- Seed integration working
- Import paths updated post-move

---

## 10. Key Decisions Captured
- Keep strict required `start_datetime` in DB/storage
- Fix datetime extraction in scraper layer when needed
- Keep event-storage logic under `events/storage` after user-requested move
- Treat `validation_tests` placement as CI configuration concern, not storage logic defect

---
```

User: I need entire chat transcript

GitHub Copilot: I’ll check whether the session debug log is accessible so I can give you the full transcript source directly instead of a partial reconstruction.I couldn’t open that exact log path, so I’m checking the nearby folder pattern to locate the actual transcript log file name.

[Internal file-search trace removed]

I can provide it, but the entire verbatim transcript is too large for a single message here.

I cannot directly read VS Code’s internal chat log files from this workspace context, so the practical way is:
1. I send the full transcript in sequential parts in chat.
2. You reply “continue” until done.

Part 1/?
- You asked for migration-safe, import-error-free guidance for Week 7 (Group 4B), focused on Chakradhar’s ownership (Event DB Schema & Storage).
- I scanned the repo and initially found no Week 7 folder, then used Week 6 as baseline.
- You repeatedly asked for exact file add/modify lists, strict scope control, and sponsor-grade confidence.
- I reviewed and proposed updates around:
  - event schema model,
  - migration 003 for events table,
  - storage/upsert module,
  - seed scripts and import safety,
  - tests and migration checks.
- You asked multiple times whether old files should remain untouched and whether architecture was correct.
- We aligned on:
  - keep stale as computed from scraped_at,
  - keep sponsorship_data strict as array of tier objects,
  - keep event persistence out of state-tracking logic,
  - avoid import breakage for direct script execution.
- You then asked me to validate actual workspace state; I checked and found key gaps at that time, then you pasted full file contents for review.

Reply “continue” and I’ll send Part 2 with the exact subsequent exchanges (file-by-file checks, findings, move to events/storage, seed run verification, and final go/no-go for commit).
