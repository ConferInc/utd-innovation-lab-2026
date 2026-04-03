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

**Wednesday, April 2, 2026 at 11:59 PM CST**

Submit your weekly summary email to `students@mail.confersolutions.ai` AND push all deliverables to the repo under `4B/week7/`.

## Git Requirements
- Branch: `4B-week7-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
- Atomic commits with meaningful messages (no "update" or "fix")

## Demo Target (Friday April 4 Call)
Be ready to demonstrate:
1. Run the scraper → show extracted JSON with real temple events
2. Query the database → show stored events
3. Hit `/events/today` → return real events happening that day
4. Search for "Hanuman Jayanti" → return correct result
