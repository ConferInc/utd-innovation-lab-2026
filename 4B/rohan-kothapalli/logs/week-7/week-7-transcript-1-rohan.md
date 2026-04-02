# Rohan's API endpoints and auth tasks
_Exported on 4/1/2026 at 21:25:08 CDT from Cursor (2.6.21)_

---

**User**

go through week 7.

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


check for rohans tasks

---

**Cursor**

Searching the codebase for Week 7 work and Rohan's assigned tasks (events API, escalations Bearer auth, integration).



Here is an audit of **Rohan’s Week 7 items** against `4B/week7` in this repo.

## Rohan’s tasks — status

### 1. `/events` HTTP API — **not implemented**

`4B/week7/main.py` only mounts the escalations router; there is **no** `events` router and no `api/events.py` (only `api/escalations.py` exists).

| Requirement | In repo |
|-------------|---------|
| `GET /events` (`limit` / `offset`) | No route |
| `GET /events/today` | No route |
| `GET /events/{id}` | No route |
| `GET /events/search?q=` | No route |
| `GET /events/recurring` | No route |
| 404 / 400 / 200 + empty list | Not applicable until routes exist |

**What exists instead:** `events/storage/event_storage.py` already implements the underlying queries (`get_upcoming_events`, `get_today_events`, `get_event_by_id`, `search_events`, `get_recurring_events`, serialization). That matches **Chakradhar’s storage layer** and **Subodh’s service** direction, but **Rohan’s FastAPI surface is missing**.

### 2. Escalations Bearer auth — **not implemented (security item still open)**

`4B/week7/api/escalations.py` exposes `POST ""`, `GET /{escalation_id}`, and `PUT /{escalation_id}/resolve` with **no** `Authorization: Bearer …` check. There is no shared dependency that returns 401 when the token is missing or wrong.

`.env.example` also has **no** variable for an internal API / escalation token (unlike docs that only mention Bearer in passing).

### 3. Integration: scraper → DB → API — **partial**

- **Scraper → JSON:** `scripts/scrape_events.py`, `events/scrapers/*`, `data/scraped_events.json` — present.  
- **JSON → DB:** `scripts/seed_database.py` / `seed_from_scraped_json.py` + `upsert_events` — present.  
- **DB → public API:** **not wired** — no `/events/*` to demo `/events/today` with scraped rows.

The bot path (`response_builder`, `integrations/calendar.py`) still centers on **Google Calendar + `knowledge_base/events.json`**, not the scraped `events` table, so the “demo `/events/today` with real scraped data” story is **not completed** at the HTTP API layer.

---

## Bottom line

| Rohan deliverable | Status |
|-------------------|--------|
| REST `/events` suite | **Missing** (storage helpers exist; HTTP layer does not) |
| Bearer on all `/escalations` routes | **Missing** |
| End-to-end demo via API | **Incomplete** (pipeline stops before FastAPI) |

If you want this closed out in-repo, the minimal follow-up is: add `api/events.py` + `app.include_router(..., prefix="/events")`, implement query params and error shapes using `event_storage`, add a small `Depends` for Bearer validation (shared with escalations), set something like `ESCALATIONS_API_TOKEN` / `INTERNAL_API_BEARER_TOKEN` in `.env.example`, and optionally point docs or a one-line README note at the demo URL—only if you explicitly want doc changes.

---

**User**

plan to complete rohans part of tasks. 

additionally, project has been changed from week 6 to week 7. ensure code functionality is carried on to work with this new environment. no need to refactor any comments, just any functional code

---

**Cursor**

Reviewing Week 6 vs Week 7 structure and event/escalation code so we can plan Rohan's work and compatibility.



Checking FastAPI route-ordering constraints and whether `week6` includes an `events` table migration for parity.



Identifying an import-path issue: `event_storage.py` uses `from database.schema`, which works when `4B/week7` is on `sys.path` (scripts/tests) but can break when the module loads as part of `4B.week7` via uvicorn. The plan will address this.



---

**User**

is this anything extra. make sure to only work under rohans scope of work.

---

**Cursor**

Reviewing the plan file and trimming anything outside Rohan's assignment.



Updating the plan: removing items outside Rohan's assignment (Subodh's tests, render.yaml, optional totals, stress-test/doc churn, deployment notes). Keeping the import shim as the minimum change so Rohan's `/events` router can load when the app runs as `4B.week7`.



Here is what was **extra** relative to Rohan’s assignment, and what changed in the plan.

### Removed or marked out of scope
- **`render.yaml`** — not part of Rohan’s brief; dropped from the plan.
- **Optional `total` / `get_event_counts` on `GET /events`** — spec only asks pagination, not totals.
- **New tests** — Subodh’s work; removed.
- **`fix-callers` / stress tests / `integration-testing.md`** — Week 7’s escalations stress script talks to the **database**, not HTTP `/escalations`, so no required updates; removed from todos.
- **Week 6 → Week 7 deploy / migration narrative** — ops/docs, not Rohan’s list; removed.
- **Mermaid + README** — trimmed from the plan body.

### Kept as **in** Rohan’s scope
- **All required endpoints** and error behavior.
- **Bearer on every `/escalations` route** + **401** behavior.
- **`main.py` + new `api/events.py`** for scraper → DB → **API** (integration is explicitly Rohan’s).
- **`.env.example` line for `ESCALATIONS_API_TOKEN`** — minimal config so auth is actually usable (not a separate “docs” deliverable like Leena’s runbook).

### The only “gray” item: **import shim in `event_storage.py`**
That is **not** listed on Rohan’s card as a separate task, but it is the **smallest functional fix** so his new router can import storage when the app runs as `4B.week7.main` (without touching scrapers, schema, or tests). The plan states that clearly and limits changes to that file to the shim only.

The updated plan file is [`rohan_week7_api_+_auth_163e51ba.plan.md`](c:\Users\rohan\.cursor\plans\rohan_week7_api_+_auth_163e51ba.plan.md) with an explicit **In scope / Out of scope** section and five todos (no `fix-callers`, no `render.yaml`).

---

**User**

okay, you can add the import shim. 

---

**Cursor**

Adding the import shim to `event_storage.py`.



I couldn’t apply the change from here: **plan mode only allows editing markdown** (like the plan file), not Python.

**Switch to Agent mode** (or a normal coding session) and ask again to add the shim, or apply this yourself in [`4B/week7/events/storage/event_storage.py`](4B/week7/events/storage/event_storage.py):

Replace:

```python
from database.schema import Event, EventSourceSite
```

with:

```python
try:
    from ...database.schema import Event, EventSourceSite
except ImportError:
    from database.schema import Event, EventSourceSite
```

That keeps script-style runs (with `4B/week7` on `sys.path`) working and lets `4B.week7.events.storage.event_storage` load when the app is started as `uvicorn 4B.week7.main:app`.

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Implementing the plan: starting with the import shim, then bearer auth, events API, and wiring.



Using explicit validation so invalid `limit`/`offset` return 400 per the plan, and using `event_to_dict` for single-event responses.



Hardening bearer comparison: `secrets.compare_digest` requires equal-length strings and can raise `ValueError` otherwise.



Summary of what was implemented:

### 1. Import shim — [`4B/week7/events/storage/event_storage.py`](4B/week7/events/storage/event_storage.py)
- Tries `from ...database.schema import Event, EventSourceSite`, falls back to `from database.schema import ...` for script-style runs.

### 2. Bearer auth — [`4B/week7/authentication/internal_bearer.py`](4B/week7/authentication/internal_bearer.py)
- `verify_escalations_bearer(request)`: requires `Authorization: Bearer <token>`, compares to `ESCALATIONS_API_TOKEN` with length check + `secrets.compare_digest` (avoids `ValueError` on length mismatch).
- Missing env, missing/invalid header, or wrong token → **401** with `"Not authenticated"`.

### 3. Escalations — [`4B/week7/api/escalations.py`](4B/week7/api/escalations.py)
- `APIRouter(..., dependencies=[Depends(verify_escalations_bearer)])` so **POST** `""`, **GET** `/{id}`, and **PUT** `/{id}/resolve` all require the bearer token.

### 4. Events API — [`4B/week7/api/events.py`](4B/week7/api/events.py)
- `GET /events` — `limit` (default 10), `offset` (default 0); **400** if `limit` not in 1–100 or `offset` &lt; 0; body `{ "events", "limit", "offset" }`.
- `GET /events/today` — `{ "events": [...] }` (may be empty).
- `GET /events/recurring` — same.
- `GET /events/search` — required non-blank `q`; same pagination rules; **400** if `q` missing/blank.
- `GET /events/{event_id}` — single object via `event_to_dict`; **404** if missing.

Static paths are registered before `/{event_id}`.

### 5. App + env — [`4B/week7/main.py`](4B/week7/main.py), [`.env.example`](4B/week7/.env.example)
- `app.include_router(events_router, prefix="/events")`.
- Documented `ESCALATIONS_API_TOKEN` (no `render.yaml` change, per plan).

### Todos
- **import-shim**, **bearer-dep**, **escalations-auth**, **events-router**, **wire-main-env**: completed.  
- **fix-callers**: cancelled (plan: no HTTP stress tests for `/escalations`).

**Local check:** Install deps from [`4B/week7/requirements.txt`](4B/week7/requirements.txt), set `DATABASE_URL` and `ESCALATIONS_API_TOKEN`, run `uvicorn 4B.week7.main:app` from the **repo root** (same as Render). A quick `import` test from this environment was blocked until `pip install` finished; if anything fails on your machine, say what you see and we can fix it.

**Ops:** Any client of `/escalations` must send `Authorization: Bearer <same value as ESCALATIONS_API_TOKEN>`.

---

**User**

give me a commit title and desc in txt format

---

**Cursor**

```
feat(week7): add /events API and Bearer auth for escalations

Implement Rohan's Week 7 scope: GET /events (paginated), /events/today,
/events/recurring, /events/search?q, and /events/{id} backed by
event_storage; return 400 for invalid pagination or missing search q,
404 for unknown event id, and 200 with empty events arrays where
appropriate.

Protect all /escalations routes with Authorization: Bearer matching
ESCALATIONS_API_TOKEN (401 when missing, misconfigured, or wrong).

Add a package/script import shim in events/storage/event_storage.py so
storage loads under uvicorn 4B.week7.main and existing scripts.

Document ESCALATIONS_API_TOKEN in .env.example.
```

