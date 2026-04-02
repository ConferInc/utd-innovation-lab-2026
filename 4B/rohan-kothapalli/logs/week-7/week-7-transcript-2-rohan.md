# Weekly assignment task completion review
_Exported on 4/1/2026 at 21:35:03 CDT from Cursor (2.6.21)_

---

**User**

"────────────────────────────
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
• Email your weekly summary to students@mail.confersolutions.ai by Wednesday April 2, 11:59 PM CST
• Push all deliverables to 4B/week7/ in the repo
• Branch: 4B-week7-[your-name], PR into main by deadline
• Atomic commits with meaningful messages (no "update" or "fix")

Full assignment details are in the repo: 4B/week7/ASSIGNMENT.md
"

check completion of everyone's task based on above.

---

**Cursor**


Exploring `4B/week7/` to assess each team member's deliverables against the assignment.





Here is an **evidence-based completion check** against what is actually in `4B/week7/` (not git blame or branch hygiene).

---

### **Sysha Sharma — Scraper architecture and orchestration**  
**Status: ~complete (minor nuance)**

- **Dual-source scraper**: `events/scrapers/radhakrishnatemple.py` pulls the homepage, targets carousel-like regions and `/event/...` links, fetches detail pages, and merges supplemental URLs. `events/scrapers/jkyog.py` hits `https://www.jkyog.org/upcoming_events` (and extra pages) with Dallas-area filtering.
- **Structured JSON**: Orchestrated in `events/scrapers/scrape_all.py`; shape aligns with the storage/schema story (`events/schemas/event_payload.py`, `data/scraped_events.json` contains real-looking rows).
- **Config / politeness**: `events/scrapers/http_client.py` — user-agent, timeouts, min delay between requests, retries/backoff; URLs overridable via CLI/env in `scripts/scrape_events.py`.
- **Errors**: Per-source `errors` list plus skip path for invalid datetimes in `scrape_all.py`; HTTP layer retries then surfaces failures.
- **Scripts**: `scripts/scrape_events.py` (JSON out) and `scripts/seed_database.py` → `seed_from_scraped_json`.

**Nuance:** “Scrape intervals” in the brief usually means delays between requests; there is no separate **scheduled** interval in code (no cron/loop)—only inter-request spacing and env-tunable knobs.

---

### **Rohan Bhargav Kothapalli — `/events` API + escalations auth**  
**Status: ~complete (small spec interpretation)**

- **Endpoints** (`api/events.py`, mounted in `main.py` under `/events`): list with `limit`/`offset`, `/today`, `/{id}`, `/search?q=...`, `/recurring`. **404** for unknown id, **400** for bad pagination or empty search query; **200** with empty `events` when applicable.
- **Escalations auth**: `api/escalations.py` uses router-level `Depends(verify_escalations_bearer)`; `authentication/internal_bearer.py` enforces `Authorization: Bearer` and compares to `ESCALATIONS_API_TOKEN` (401 when missing/wrong; also 401 if token not configured).

**Nuance:** `GET ""` lists **upcoming non-recurring** events only (`get_upcoming_events` filters `is_recurring is False`). The assignment text says “all upcoming events”; recurring are available on **`GET /events/recurring`** instead of the main list.

---

### **Chakradhar Reddy Gummakonda — Schema, storage, seed**  
**Status: ~complete**

- **Migration** `migrations/versions/003_add_events_table.py`: columns match the assignment (plus `dedup_key` for upserts). **`source_site`** enum, **indexes** on `start_datetime`, `name`, `category`, `is_recurring`.
- **Storage**: `events/storage/event_storage.py` — normalize/validate payloads, **upsert** by `dedup_key` or `(source_site, source_url)`, cross-source dedup helpers in scraper + DB constraints, **`is_stale`** in serialized output (30-day rule via `is_event_stale`).
- **Seed**: `scripts/seed_database.py` + `data/scraped_events.json` (committed sample of scraped output).

---

### **Subodh Krishna Nikumbh — Event service wrapper, caching, 20+ tests**  
**Status: incomplete vs assignment**

- **No** dedicated **`EventService`** layer or **named** methods like `getUpcomingEvents` / `getTodayEvents` — the API calls **`event_storage`** functions directly.
- **No** **caching** layer or **invalidate-on-re-scrape** hook in code (only unrelated “invalidate” wording in session code).
- **Tests**: There are many tests across `validation_tests/` and `tests/` (well over 20), but they **do not** match the brief: **no** `TestClient` **API tests** for `/events/*`, **no** cache hit/miss tests, **no** documented **HTML fixture files** from both live sites, **no** clear **end-to-end** scrape → DB → query test in-repo (grep shows no `/events` API test usage).

So: **good unit coverage for pieces of the pipeline**, **not** the specified service + cache + API + E2E story.

---

### **Leena Hussein — Stripe webhooks + event pipeline docs**  
**Status: major gaps**

- **Stripe webhooks**: `main.py` has **`/webhook/whatsapp`**, not Stripe. **No** `payment_intent.succeeded` / `payment_intent.payment_failed` handlers, **no** **`Stripe-Signature`** verification, **no** webhook-focused tests (existing `tests/test_stripe_wrapper.py` targets the wrapper, not webhooks).
- **Event pipeline documentation**: `docs/` has **no** scraper/seed/runbook/troubleshooting-for-HTML-staleness content (grep in `docs/` found nothing). `README.md` barely mentions the new pipeline. `docs/environment-variables.md` lists core bot vars but **not** scraper env vars or `ESCALATIONS_API_TOKEN` (those **are** in **`.env.example`**).

---

### **Friday demo checklist (from your list)**

| Demo item | Ready in code/repo? |
|-----------|----------------------|
| Run scraper → real JSON | Yes — `scripts/scrape_events.py`, `data/scraped_events.json` sample |
| Query DB → stored events | Yes — after migrate + seed |
| `GET /events/today` with real data | Yes — depends on DB contents |
| Search “Hanuman Jayanti” | **Plausible** — temple supplemental URLs include hanuman path; quality depends on scraped text in DB |
| `/escalations` 401 without token, 200 with | **Protected** — requires valid `ESCALATIONS_API_TOKEN` and bearer header |

---

### **Bottom line**

| Person | Completion (against your brief) |
|--------|----------------------------------|
| **Sysha** | **Done** (or very close) |
| **Rohan** | **Done** (minor “all upcoming” vs non-recurring list nuance) |
| **Chakradhar** | **Done** |
| **Subodh** | **Partly done** — missing service abstraction, cache, API/E2E tests as specified |
| **Leena** | **Not done** — Stripe webhooks + signature + tests + dedicated event-pipeline docs/env doc sync |

If you want, we can next either **implement the missing Leena/Subodh pieces** or **produce a short PR comment** you can paste for each owner.

---

**User**

fix and complete rohans work

---

**Cursor**


Completing Rohan's work: aligning `GET /events` with "all upcoming events" (including recurring), verifying routes and errors, and adding API tests. Reviewing the implementation now.




Updating `get_upcoming_events` to include recurring programs (assignment: "All upcoming events") and adding API tests that use a minimal FastAPI app to avoid running full `main` lifespan/migrations.




Removing the weak storage mock test and adding an escalations Bearer test. Fixing the API test patch: use the path where the name is resolved.




Fixing imports: `api` uses parental relative imports (`..database`), so we must import via the `week7` package with `4B` on `sys.path`.




Here is what was completed for **Rohan’s** slice.

### 1. **`GET /events` = all upcoming events (spec-aligned)**  
Previously only **non-recurring** rows were returned. It now includes:

- **One-off events** that are still ongoing or in the future (same time rules as before).
- **Recurring programs** that are still active: `end_datetime` is null or `>= now`.

Ordering: **non-recurring first** (`is_recurring` ascending), then by `start_datetime`, then `id`, so dated one-offs surface before standing programs.

```285:317:c:\Github Repo\utd-innovation-lab-2026\4B\week7\events\storage\event_storage.py
def get_upcoming_events(
    db: Session,
    *,
    limit: int = 10,
    offset: int = 0,
    now_utc: Optional[datetime] = None,
) -> List[Event]:
    """
    Paginated upcoming events: one-off sessions that have not ended, plus recurring
    programs that are still active (no end date or end in the future).

    Non-recurring rows sort before recurring so near-term dated events surface first.
    """
    now = now_utc or _now()
    one_off_upcoming = and_(
        Event.is_recurring.is_(False),
        or_(
            Event.start_datetime >= now,
            and_(Event.end_datetime.isnot(None), Event.end_datetime >= now),
        ),
    )
    recurring_active = and_(
        Event.is_recurring.is_(True),
        or_(Event.end_datetime.is_(None), Event.end_datetime >= now),
    )
    return (
        db.query(Event)
        .filter(or_(one_off_upcoming, recurring_active))
        .order_by(Event.is_recurring.asc(), Event.start_datetime.asc(), Event.id.asc())
        ...
    )
```

### 2. **API docstring**  
`api/events.py` list handler text now matches “all upcoming events + pagination”.

### 3. **Tests (Rohan + escalations demo)**  
- `validation_tests/test_events_api.py` — `/events`, `/today`, `/recurring`, `/search`, `/{id}`, 400/404/200 empty list behaviors, with `get_db` overridden so no DB is required.  
- `validation_tests/test_escalations_bearer.py` — **401** without / wrong Bearer, **404** with valid token (proves auth passes through to the handler).

Imports use `4B` on `sys.path` and `week7.*` so the same package layout as `main.py` works.

**Already in place (unchanged):** routers on `main`, Bearer on all `/escalations` routes, search, pagination, error codes.

All **54** `validation_tests/` tests pass locally.

---

**User**

give me a git summary and desc for this

---

**Cursor**


### Commit title (short summary)
```
feat(events): include recurring programs in GET /events and add API auth tests
```

### Description (body for commit or PR)

**What changed**

- **`GET /events`** now matches the assignment wording for “all upcoming events”: it returns paginated **one-off** events that are still current or upcoming **and** **recurring** programs that are still active (no end time or end in the future). **Non-recurring** rows are ordered **before** recurring so dated events appear first; both groups are sorted by `start_datetime` and `id`.
- **Docs**: the list handler docstring in `api/events.py` was updated to describe that behavior.
- **Tests**: added **`validation_tests/test_events_api.py`** for `/events`, `/today`, `/recurring`, `/search`, and `/{id}` (including 400/404 and 200 with an empty list) using a small FastAPI app and dependency overrides. Added **`validation_tests/test_escalations_bearer.py`** so **`/escalations`** returns **401** without a valid Bearer token and reaches the handler with a good token (e.g. **404** for a missing id).

**Why**

- Aligns the public events API with the Week 7 spec and demo expectations while locking in behavior with tests, including the escalations Bearer requirement.

**Files touched (for reference)**

- `4B/week7/events/storage/event_storage.py` — `get_upcoming_events` filter and ordering  
- `4B/week7/api/events.py` — docstring  
- `4B/week7/validation_tests/test_events_api.py` — new  
- `4B/week7/validation_tests/test_escalations_bearer.py` — new

