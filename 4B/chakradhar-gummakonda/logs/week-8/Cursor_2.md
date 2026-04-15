# Week8_Tablestructureidea_cursorai
_Exported on 4/12/2026 at 13:32:06 CDT from Cursor (3.0.9)_

---

**User**

Hi Team 4B, Your pipeline is the most complete backend work in this program. Scrapers running, database seeded, five API endpoints, auth hardened, Stripe webhooks nearly done. That work is real and it matters. This sprint, you get it live and you keep it live while Team 4A builds the bot on top of it. Weeks 8 and 9 are one combined sprint. The deadline is Wednesday, April 15, 2026 at 11:59 PM CST. Your full assignment is in the repo at 4B/week8/ASSIGNMENT.md. This email is your overview. The ASSIGNMENT.md has full deliverable specs, file paths, code-level details, and test requirements. Three Blockers to Fix Before Anything Else These three issues from Week 7 will crash the demo if not resolved in the first two days: Stripe webhook import error — api/stripe_webhooks.py has a wrong import path. The app crashes at startup. One-line fix: change from integrations.stripe import to from ..integrations.stripe import. Start the app after fixing it. Confirm it loads. Events router prefix — Your events are mounted at /events but Team 4A's API contract says /api/v2/events. One-line fix in main.py. Do it before the April 9 sync so Team 4A can test against the correct path. Sponsorship tier schema mismatch — Team 4B stores {name, amount, link}. Team 4A's response templates expect {tier_name, price_usd, price_inr, description}. This will cause silent failures in the bot's sponsorship responses. Resolved at the April 9 sync — Chakradhar and Chanakya agree on one format. Your Individual Tasks Rohan Kothapalli — API Alignment & Deployment You own making the API live and reachable for Team 4A. Fix the events router prefix in main.py: /events → /api/v2/events Add .coverage, stress_test_results_*, and scraped_events.json to .gitignore — these run-output artifacts from Week 7 should not be in version control Deploy the full stack to Render with the events pipeline active. All 5 event endpoints must return real data on the live URL. Share the Render base URL with Team 4A by April 9 at 7:00 PM CST — put it in assignments/week-08-09-sync-notes.md and in Slack before the sync meeting starts Write docs/api-security.md (1 page): document that /events endpoints are intentionally public (read-only), and which endpoints require auth (escalations, Stripe). Team 4A needs to know whether to send auth headers. Chakradhar Gummakonda — Schema Alignment & Database Hardening You own the three most critical pre-integration fixes. Schema alignment (due by April 9 sync): Lock the sponsorship tier field names with Chanakya (4A). After the sync, update event_storage.py and the Pydantic SponsorshipTier model in event_payload.py to match the agreed format. Document the decision in docs/schema-decisions.md. recurrence_pattern validation: _matches_recurrence() silently returns False for unsupported patterns. Add a validator in event_payload.py using Literal or a regex so unsupported patterns fail at write time with a clear error, not silently at query time. SQLite local dev fallback (4-week open flag): Add a DATABASE_URL check in the database connection module. If the URL starts with sqlite:///, configure SQLAlchemy for SQLite. Add .env.local.example showing DATABASE_URL=sqlite:///./local_dev.db. Add local_dev.db to .gitignore. Test all 5 event endpoints with the SQLite fallback. This unblocks Team 4A from testing locally. Seed live data: Run scrape_all.py, seed the Render database, and confirm GET /api/v2/events on the live URL returns real events. Commit a text summary of the scraper run as data/scrape-run-april-2026.log. Sysha Sharma — Scraper Hardening Your Week 7 scrapers are the core data source for the demo. Harden them. Retry logic: Add retry on transient failures to RespectfulHttpClient — up to 3 retries with exponential backoff (1s, 2s, 4s) on HTTP 5xx or connection timeout. No retries on 4xx. Make max_retries and backoff_factor configurable parameters. Expand _guess_category: The current RKT scraper only recognizes 4 categories. The schema supports 8: festival, retreat, satsang, youth, class, workshop, health, special_event, other. Expand the keyword mapping in both scrapers to cover the full set. Events that don't match any keyword default to "other". Document JS rendering limitation: Add a module-level docstring to both scraper files explaining that static HTML parsing will miss any events rendered by JavaScript, and what the upgrade path looks like (Playwright/Selenium). scraped_events.json as fixture: Add a comment at the top marking it as a development snapshot. Update the seed script to accept a --fixture flag for offline dev testing without re-scraping. Subodh Nikumbh — Integration Tests & Knowledge Base Connection Close the testing gap and connect events to the bot's brain. End-to-end integration test — tests/test_event_pipeline_integration.py: Mock scraper JSON → upsert_events() → EventService.get_upcoming_events() → API endpoint response Minimum 6 test cases: single upsert, duplicate upsert (dedup check), search by name, today's events filter, recurring events filter, sponsorship tier rendering Use an in-memory SQLite database per test run — no Render required to run these tests EventQueryCache max size with LRU eviction: The current cache grows unbounded. Add max_size: int = 500 to EventQueryCache.__init__. Use OrderedDict for O(1) LRU eviction. Update get_shared_event_query_cache() to accept max_size. Add a test for eviction behavior. Connect events to the knowledge base: Add ingest_events() to knowledge_base/ingestion.py. It reads all upcoming events from the database via EventService, formats each as a KB document, and indexes them. Wire it to run at the end of seed_from_scraped_json.py. This ensures Team 4A's intent classifier can find events via KB search, not just direct API calls. Leena Hussein — Import Fix, Demo Infrastructure & Docs Fix the startup blocker, prepare the demo environment, and clean up documentation. Fix the Stripe webhook import first (see blockers above). After fixing: start the app, confirm no ImportError, run pytest tests/test_stripe_webhooks.py — all pass. Stripe webhook path: Verify the registered path isn't double-prefixed. Check main.py mount + api/stripe_webhooks.py route decorator. Fix to a clean single path and document the correct URL in docs/render-deployment.md. Demo script — docs/demo-script.md: step-by-step instructions for running the April 15 demo, including: how to start the app locally as a fallback, how to reseed the database, sample curl commands for all 5 event endpoints, and what to do if an endpoint returns empty results or the scraper fails. Commit history: Starting this PR, squash duplicate commits before raising. Add docs/git-workflow.md documenting Team 4B's commit prefix conventions (feat(scope):, fix(scope):, docs(scope):, test(scope):). Mandatory: Cross-Team Sync — April 9 at 7:00 PM CST All 10 students. 45 minutes. Chakradhar and Chanakya lead the schema alignment discussion (20 min). After this sync, field names are locked — no more changes. Rohan confirms the live Render URL is accessible from Team 4A's machines (15 min). Remaining 10 min for any integration blockers. Meeting notes go into assignments/week-08-09-sync-notes.md by 9:00 PM that night. Joint Deliverable — Demo Video Both teams record one 3–5 minute video showing a real WhatsApp message going through Team 4A's bot, calling your live API, and getting a real response back with real temple event data. Minimum: time-based query, event-specific query, recurring schedule query, no-results case. No mockups. No hardcoded responses. Acceptance Criteria What Minimum Bar API live All 5 event endpoints return real data on the public Render URL Schema locked Sponsorship tiers and event ID strategy agreed and implemented SQLite fallback Team 4A can run your API locally without Render credentials Stripe import fix App starts without errors Demo video 3–5 min end-to-end recording with real WhatsApp data Git hygiene Individual branches, one PR, no committed run-output artifacts Deadline Wednesday, April 15, 2026 — 11:59 PM CST Also on April 15: Swami Mukundananda speaks at UTD at 6:15 PM (SSA Auditorium). All 10 of you are expected to attend. Plan to have your Render deployment stable by Monday, April 13 so Team 4A has buffer to test against it before the deadline. Full deliverable specs, code-level details, and test requirements are in the repo: 4B/week8/ASSIGNMENT.md Other email: What you're doing well: The W7 event storage layer — two-stage dedup, per-upsert savepoints, deterministic SHA-256 keying — is the strongest engineering artifact produced by either team in 7 weeks. The only outstanding issue is the sponsorship tier schema mismatch with Team 4A (name/amount/link vs. tier_name/price_usd/price_inr/description). This is a cross-team alignment gap, not a design flaw, but it will cause integration failures that Chakradhar is best positioned to resolve. Also: stress test result files should not be committed — add stress_test_results_* to .gitignore. Where to push next: There is one cross-team item that only you can fix quickly: the sponsorship tier field names. Pick one and align with Chanakya before both of you write integration code that hits this wall. The fix is small — the coordination is what matters. Also, I was told about something like escalations schema also does not match chanakya's document. so i need to work on it. give me a complete sponsored level project, not basic project, which needs to be done. 

These were given by sponsor.

Week 7 — Event Data Model & Response Templates
Owner: Chanakya Sairam Varma Alluri
Project: JKYog / Radha Krishna Temple event ingestion for bot + WhatsApp responses
Date: 2026-04-01

1) Canonical Event JSON Schema
The schema below is designed to normalize event data from JKYog / Radha Krishna Temple pages into one canonical structure that can support: - event search - WhatsApp responses - logistics questions - sponsorship questions - recurring event handling - source traceability back to the website

{
  "id": "string",
  "name": "string",
  "subtitle": "string | null",
  "category": "festival | retreat | satsang | youth | class | workshop | special_event | other",
  "event_type": "in_person | online | hybrid | unknown",
  "is_recurring": "boolean",
  "recurrence_text": "string | null",

  "start_datetime": "ISO-8601 string | null",
  "end_datetime": "ISO-8601 string | null",
  "timezone": "string | null",

  "location_name": "string | null",
  "address": "string | null",
  "city": "string | null",
  "state": "string | null",
  "postal_code": "string | null",
  "country": "string | null",

  "description": "string | null",

  "registration_required": "boolean | null",
  "registration_status": "open | closed | unknown",
  "registration_url": "string | null",

  "contact_email": "string | null",
  "contact_phone": "string | null",

  "parking_notes": "string | null",
  "transportation_notes": "string | null",
  "food_info": "string | null",

  "price": {
    "amount": "number | null",
    "notes": "string | null"
  },

  "sponsorship_tiers": [
    {
      "tier_name": "string",
      "price": "number | null",
      "description": "string | null"
    }
  ],

  "source_url": "string",
  "source_site": "jkyog.org | radhakrishnatemple.net",
  "source_page_type": "event_detail | upcoming_events | sponsorship_page | logistics_page",

  "scraped_at": "ISO-8601 string",
  "source_confidence": "high | medium | low",
  "notes": "string | null"
}
Field design notes
id: stable internal key such as jkyog-dallas-holi-mela-2026
subtitle: useful for pages that show a short descriptor under the event title
category: normalized bucket for routing user queries
event_type: inferred from page labels like “In-person” or “Online”
is_recurring + recurrence_text: helps answer “Does this happen every week/year?”
parking_notes, food_info, transportation_notes: dedicated logistics fields so the bot does not hide important practical details inside one long description
price: simplified object with amount and notes
sponsorship_tiers: array with tier_name, price, and description to support event-specific sponsorship / seva options
source_confidence: marks whether a value came directly from a detailed event page or only from a summary/calendar listing
2) Sample JSON for real events from the website
Below are normalized samples based on the public event/calendar pages and related event/sponsorship pages.

Sample 1 — Dallas Holi Mela
{
  "id": "jkyog-dallas-holi-mela-2026",
  "name": "Dallas Holi Mela",
  "subtitle": "Holika dahan & Phoolon ki Holi Celebration",
  "category": "festival",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Annual Holi festival style event",
  "start_datetime": "2026-03-01T10:30:00-06:00",
  "end_datetime": "2026-03-07T22:00:00-06:00",
  "timezone": "CST",
  "location_name": "Radha Krishna Temple of Dallas",
  "address": "1450 North Watters Road",
  "city": "Allen",
  "state": "TX",
  "postal_code": "75013",
  "country": "USA",
  "description": "Celebrate the Vibrant Festival of Holi in Dallas! Join us for a joyful day filled with colours, music, dancing, and traditional festivities. Experience the true essence of Holi with family and friends.",
  "registration_required": null,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": "[email protected]",
  "contact_phone": "[redacted phone]",
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "price": {
    "amount": null,
    "notes": null
  },
  "sponsorship_tiers": [],
  "source_url": "https://www.jkyog.org/retreat/festival-of-holi-in-dallas",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "high",
  "notes": "Date/time also appears in JKYog upcoming events calendar."
}
Sample 2 — Mahashivratri retreat entry from the upcoming events calendar
{
  "id": "jkyog-mahashivratri-retreat-2026-dallas",
  "name": "Mahashivratri",
  "subtitle": null,
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Likely annual festival/retreat entry tied to Mahashivratri",
  "start_datetime": "2026-02-13T09:30:00-06:00",
  "end_datetime": "2026-02-16T20:30:00-06:00",
  "timezone": "CST",
  "location_name": "Radha Krishna Temple of Dallas",
  "address": "1450 North Watters Road",
  "city": "Allen",
  "state": "TX",
  "postal_code": "75013",
  "country": "USA",
  "description": null,
  "registration_required": null,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": null,
  "contact_phone": null,
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "price": {
    "amount": null,
    "notes": "Calendar listing only"
  },
  "sponsorship_tiers": [],
  "source_url": "https://www.jkyog.org/upcoming_events",
  "source_site": "jkyog.org",
  "source_page_type": "upcoming_events",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "medium",
  "notes": "This record is from the aggregated upcoming events calendar and contains fewer details than a full event page."
}
Sample 3 — Dallas Spiritual Retreat / Family Camp
{
  "id": "jkyog-dallas-spiritual-retreat-family-camp",
  "name": "Dallas Spiritual Retreat with Swami Mukundananda",
  "subtitle": "JKYog Family Camp",
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": true,
  "recurrence_text": "Recurring retreat/family camp program",
  "start_datetime": null,
  "end_datetime": null,
  "timezone": null,
  "location_name": "Hyatt Place Garland / Radha Krishna Temple of Dallas",
  "address": "5101 N President George Bush Hwy, Garland, TX 75040, USA",
  "city": "Garland",
  "state": "TX",
  "postal_code": "75040",
  "country": "USA",
  "description": "Immerse in three days of bliss with yoga, meditation, kirtans, discourses by Swami Mukundananda, festival celebrations, and special programs for kids & youth!",
  "registration_required": true,
  "registration_status": "closed",
  "registration_url": null,
  "contact_email": "[email protected]",
  "contact_phone": "[redacted phone]",
  "parking_notes": null,
  "transportation_notes": "Guests are responsible for arranging their own transportation from the airport to their hotel, as well as between the hotel and the temple.",
  "food_info": "Three meals (breakfast, lunch, dinner) are covered by the retreat registration fee.",
  "price": {
    "amount": 275,
    "notes": "Page lists both in-person and online price and states children are ages 4\u201312."
  },
  "sponsorship_tiers": [
    {
      "tier_name": "Grand Sponsor",
      "price": 2501,
      "description": "Seva opportunity listed on Family Camp sponsorship page"
    },
    {
      "tier_name": "Daily Yajman",
      "price": 500,
      "description": "Seva opportunity listed on Family Camp sponsorship page"
    },
    {
      "tier_name": "Daily Lunch",
      "price": 251,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Daily Dinner",
      "price": 251,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Daily Breakfast",
      "price": 151,
      "description": "Meal sponsorship"
    },
    {
      "tier_name": "Guru Purnima Daavat for Maharaj Ji",
      "price": 101,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Pagadi for Maharaj Ji",
      "price": 101,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Fruits & Flowers",
      "price": 101,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Radha Krishna Abhishek",
      "price": 51,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Maharaj Ji Jhoolan (Fri)",
      "price": 51,
      "description": "Seva opportunity"
    },
    {
      "tier_name": "Aarti",
      "price": 25,
      "description": "Seva opportunity"
    }
  ],
  "source_url": "https://www.jkyog.org/dallas-spiritual-retreat-with-swami-mukundananda",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "high",
  "notes": "Sponsorship tiers supplemented from the related Family Camp sevas page."
}
Sample 4 — Bhakti Kirtan Retreat entry visible on the retreat page
{
  "id": "jkyog-bhakti-kirtan-retreat-2025",
  "name": "Bhakti Kirtan Retreat",
  "subtitle": null,
  "category": "retreat",
  "event_type": "in_person",
  "is_recurring": false,
  "recurrence_text": null,
  "start_datetime": "2025-04-18T00:00:00-05:00",
  "end_datetime": "2025-04-20T23:59:59-05:00",
  "timezone": "CDT",
  "location_name": null,
  "address": null,
  "city": null,
  "state": null,
  "postal_code": null,
  "country": null,
  "description": "Join us for the inspiring Bhakti Kirtan Retreat with Swami Mukundananda from April 18\u201320, 2025.",
  "registration_required": true,
  "registration_status": "unknown",
  "registration_url": null,
  "contact_email": null,
  "contact_phone": null,
  "parking_notes": null,
  "transportation_notes": null,
  "food_info": null,
  "price": {
    "amount": null,
    "notes": null
  },
  "sponsorship_tiers": [],
  "source_url": "https://www.jkyog.org/dallas-spiritual-retreat-with-swami-mukundananda",
  "source_site": "jkyog.org",
  "source_page_type": "event_detail",
  "scraped_at": "2026-04-01T00:00:00Z",
  "source_confidence": "medium",
  "notes": "Visible in the 'Upcoming Events with Swamiji' section on the retreat page."
}
3) WhatsApp response templates
These templates are designed to remain safely under WhatsApp’s 4096-character message limit.

A. Single event result
 *{{name}}*
{{subtitle_line}}

 {{date_time_text}}
 {{location_text}}

{{description_short}}

{{price_line}}
{{food_line}}
{{parking_line}}
{{registration_line}}

{{contact_line}}
 More info: {{source_url}}
Rendering rules - subtitle_line: include only if subtitle exists - price_line: include only when price is known - food_line: include only when food info exists - parking_line: include only when parking notes exist - registration_line: e.g. Registration: Required / Registration: Closed / Registration: Check website - contact_line: include phone or email if available

B. Event list result
Here are the events I found for *{{query}}*:

1) *{{event_1_name}}*  
    {{event_1_time}}  
    {{event_1_location}}

2) *{{event_2_name}}*  
    {{event_2_time}}  
    {{event_2_location}}

3) *{{event_3_name}}*  
    {{event_3_time}}  
    {{event_3_location}}

Reply with:
- *1*, *2*, or *3* for full details
- *logistics* for parking/food/travel info
- *sponsorship* for seva or sponsorship options
Bot behavior - Cap to 3–5 events per message - If more than 5 matches, send the first 5 and ask a narrowing follow-up

C. No results
I couldn’t find any matching events for *{{query}}* right now.

You can try:
- an event name (example: *Holi*, *retreat*, *family camp*)
- a month or date
- a category like *festival*, *weekly satsang*, or *youth*

If you want, I can also show the latest upcoming events.
D. Sponsorship info
 *Sponsorship / Seva Information for {{name}}*

Available options:
{{sponsorship_bullets}}

If you want, I can also help with:
- event dates and venue
- food details
- registration / contact information
Example bullet rendering

• Grand Sponsor — $2501 / Rs.50,001
• Daily Yajman — $500 / Rs.10,000
• Daily Lunch — $251 / Rs.5,001
• Daily Dinner — $251 / Rs.5,001
E. Logistics response
 *Logistics for {{name}}*

 Venue: {{location_text}}
Parking: {{parking_text}}
 Food: {{food_text}}
 Transportation: {{transportation_text}}

{{registration_line}}
{{contact_line}}
 More info: {{source_url}}
Fallback logic - If a logistics field is missing, say Not listed on the event page - Never fabricate parking or food details

4) Data source mapping
This table documents where each field should be captured from on the website.

Schema field	Website source	Where it comes from on the website	Notes
id	Internal/generated	Generated from normalized event slug + year	Not scraped directly
name	Event page / calendar	Event title heading or event name in upcoming events calendar	Primary display field
subtitle	Event detail page	Subtitle / short descriptor under title	Example: Holi page subtitle
category	Inferred	Derived from title, page label, or section taxonomy	Controlled vocabulary
event_type	Event page / calendar	Labels such as “In-person” / “Online”	Direct scrape where shown
is_recurring	Inferred	Determined from event pattern or repeated annual/weekly occurrence	Mark as inferred
recurrence_text	Event page / temple programs page	Weekly/annual wording if explicitly mentioned	Otherwise null
start_datetime	Event page / calendar	Date-time row on event page or date range in upcoming events calendar	Convert to ISO-8601
end_datetime	Event page / calendar	Same as above	Convert to ISO-8601
timezone	Event page / calendar	Timezone marker like CST / EST / IST	Preserve source timezone
location_name	Event page / calendar	Venue line	Example: Radha Krishna Temple of Dallas
address	Event page / calendar	Full address line	Parse into structured parts where possible
city / state / postal_code / country	Event page / calendar	Parsed from venue/address string	Derived from address
description	Event detail page	“Description of the Event” block or event intro text	Keep concise version for WhatsApp
registration_required	Event page / FAQ	Registration text, forms, FAQ	Boolean
registration_status	Event page	Text such as “registration is closed”	Normalize to enum
registration_url	Event page	Register button/form link	If directly exposed
contact_email	Event page	Contact row / email text	Direct scrape
contact_phone	Event page	Contact row / phone text	Direct scrape
parking_notes	Logistics / visitor / event-specific page	Parking instructions on dedicated page or event note	Null if not listed
transportation_notes	Event detail page	Transport policy section	Example: airport-hotel-temple note
food_info	FAQ / event details / retreat price section	Meals included, prasad, food booth references	Keep literal summary
price	Event detail page	Pricing or fee block	Store as simplified object with amount and notes
sponsorship_tiers	Sponsorship / seva page	Dedicated sponsorship table or donation listing	Array with tier_name, price, and description
source_url	Scrape metadata	URL of source page	Required for traceability
source_site	Scrape metadata	Domain name	Useful for trust/source grouping
source_page_type	Scrape metadata	Event detail / upcoming events / sponsorship / logistics	Helps confidence scoring
scraped_at	Scrape metadata	Timestamp of extraction	Operational field
source_confidence	Internal quality field	Based on page richness and directness	High for detail pages; medium for calendar-only entries
notes	Internal	Any extraction caveat	Example: “calendar only”
5) Recommended extraction logic
Priority order for extraction
Event detail page
Best source for title, subtitle, description, contact info, venue, logistics, price
Upcoming events calendar
Best backup source for date/time and venue when a detail page is missing
Sponsorship / seva page
Best source for sponsorship_tiers
Temple logistics / visitor pages
Best source for parking and arrival guidance when event page lacks logistics
Normalization rules
Convert all event dates to ISO-8601, but keep original source timezone
Preserve raw descriptive text in notes if parsing is uncertain
Do not invent missing values; set them to null
Use source_confidence = medium when only a calendar listing is available
Keep sponsorship tiers in an array so the bot can answer partial queries like “daily lunch sponsorship”
6) Bot-facing recommendations
Recommended response strategy
For “What events are coming up?” → use compact event list template
For “Tell me about Holi” → use single event template
For “What are the sponsorship options?” → use sponsorship template
For “Parking / food?” → use logistics template
Recommended fallback strategy
If multiple events match the same keyword, ask the user to choose one
If logistics are missing, explicitly say they are not listed on the current page
If sponsorship info exists on a separate page, merge it into the event response but preserve the source URL list internally
7) Submission note
This deliverable provides: - a canonical event schema - 4 sample event JSON records from real JKYog / temple web pages - WhatsApp-safe response templates - a field-to-source mapping for scraping and normalization



These two images and text were given by chanakya

---

**Cursor**

You already have most of what the sponsor is asking for; your job is to lock it down, prove it, and document it at a “sponsored‑level” polish.

Below is a **concrete, non‑basic project plan just for you (Chakradhar)**, centered on (1) canonical events + sponsorship tiers and (2) escalations schema alignment with Chanakya’s docs.

---

### 1) Ground truth: what the sponsor + Chanakya expect

#### **Canonical Event & Sponsorship Schema (from Chanakya)**

Key pieces you must guarantee end‑to‑end:

- **Top‑level event fields (read‑only API)**:  
  `id, name, subtitle, category, event_type, is_recurring, recurrence_text, start_datetime, end_datetime, timezone, location_name, address, city, state, postal_code, country, description, registration_required, registration_status, registration_url, contact_email, contact_phone, parking_notes, transportation_notes, food_info, source_url, source_site, source_page_type, scraped_at, source_confidence, notes`

- **Nested price object**:  
  `price: { amount, notes }`

- **Nested sponsorship tiers array (locked format)**:  
  `sponsorship_tiers: [ { tier_name, price, description } ]`

Your current database & Pydantic models are aligned:

- **DB model** `Event` (in `database/schema.py`)  
  Sponsorship tiers stored as JSON: `sponsorship_tiers` with `{tier_name, price, description}`.
- **Pydantic model** `ScrapedEventPayload` + `SponsorshipTier` (in `events/schemas/event_payload.py`)  
  Exactly uses `tier_name`, `price`, `description`, with validators.
- **Storage layer** `event_storage.normalize_event_payload()`  
  Converts any legacy `{name, amount, link}` into `{tier_name, price, description}`.

So *schema-wise*, sponsorship tiers are already at spec; what’s left is **verification, tests, and docs** so the sponsor can trust it.

#### **Canonical Escalation Schema (from Chanakya’s flow)**

From the screenshot + your `escalations-schema.md`, the required fields are:

- `success`
- `ticket_id`
- `queue_status`
- `assigned_volunteer`
- `next_state`
- `message_for_user`
- `priority`
- `errors`

Your current alignment:

- **DB table** `escalations` (documented in `escalations-schema.md`, implemented in `database/schema.py` as `Escalation`)  
  Columns: `ticket_id (UUID PK), success, queue_status, assigned_volunteer, next_state, message_for_user, priority, errors` with check constraints for `queue_status` and `priority`.
- **API response format** documented in `escalations-schema.md` section “API Response Format (Aligned with Team 4A)”: JSON contains exactly those fields.

So again, the core shape seems correct; what you need is **hard guarantees that every POST/GET/PUT /escalations endpoint always returns exactly this shape and semantics**.

---

### 2) Tables & contracts you personally own

#### **Events / Sponsorships (DB‑side)**

- **Table**: `events`
- **Critical sponsorship‑related columns** (already present):
  - `price` (JSON, `{amount, notes}`)
  - `sponsorship_tiers` (JSON, `[{tier_name, price, description}]`)
- **Other fields that must match Chanakya’s canonical JSON**:
  - `id` (int PK, but exposed as API `id` string/int – you can keep numeric)
  - `name, subtitle, category, event_type`
  - `is_recurring, recurrence_pattern, recurrence_text`
  - `start_datetime, end_datetime, timezone`
  - `location_name, address, city, state, postal_code, country`
  - `registration_required, registration_status, registration_url`
  - `contact_email, contact_phone`
  - `parking_notes, transportation_notes, food_info`
  - `source_url, source_site, source_page_type, scraped_at, source_confidence`
  - `notes`

#### **Escalations (DB‑side)**

- **Table**: `escalations`
- Columns exactly as in `escalations-schema.md`:
  - `ticket_id (UUID PK)`
  - `success (bool)`
  - `queue_status (queued | assigned | resolved)`
  - `assigned_volunteer (string | null)`
  - `next_state (string, e.g. WAITING_FOR_VOLUNTEER)`
  - `message_for_user (string)`
  - `priority (low | medium | high | critical)`
  - `errors (JSON array)`

---

### 3) Your “sponsored‑level” project plan (practical, not basic)

Use this as your **actual Week 8–9 personal roadmap**. Everything here is scoped so you can demonstrate serious ownership to the sponsor.

---

#### A. Schema & Contract Verification (Events + Sponsorships + Escalations)

**Goal**: Prove that your DB schema, Pydantic models, and API responses 100% match Chanakya’s canonical docs.

1. **Events / Sponsorship Tiers schema audit**
   - Compare Chanakya’s JSON schema (the long spec you pasted) with:
     - `Event` SQLAlchemy model (events table)
     - `ScrapedEventPayload`, `PriceInfo`, `SponsorshipTier` models
     - `event_storage.event_to_dict()` (API response serializer)
   - Produce a **one‑page table** in `docs/schema-decisions.md`:
     - Each canonical field → DB column name → API JSON field → any differences or notes (e.g., `id` is int vs string).
   - Confirm sponsorship tiers are **always** `{tier_name, price, description}` at:
     - scrape output JSON
     - seed script input
     - DB stored value
     - API response.

2. **Escalation schema audit**
   - Open the 4A escalation doc (the one referenced in `escalations-schema.md`) and mirror the same mapping:
     - Each required response field → DB column → API JSON field.
   - Confirm that every `/escalations` endpoint:
     - Returns `success`, `ticket_id`, `queue_status`, `assigned_volunteer`, `next_state`, `message_for_user`, `priority`, `errors` on success.
     - Returns a **consistent error envelope** when something fails (even if just `success: false, errors: [...]`).

3. **Alignment report**
   - Write a short “Alignment status” section in `docs/schema-decisions.md`:
     - **Events**: compliant fields list + any intentional deviations.
     - **Sponsorship tiers**: locked format + legacy mapping behavior.
     - **Escalations**: final agreed contract.

Deliverable: **Updated `docs/schema-decisions.md` and `escalations-schema.md` that someone from Team 4A can read and see “this exactly matches our spec.”**

---

#### B. Strong Validation & Invariants

You’ve already done some work (e.g., recurrence_pattern validator in `event_payload.py` and `event_storage.py`). Extend that to a “production‑grade” level:

1. **Recurrence & category invariants**
   - Ensure that:
     - `ALLOWED_CATEGORIES`, `ALLOWED_EVENT_TYPES`, `ALLOWED_RECURRENCE_PATTERNS`, `ALLOWED_SOURCE_CONFIDENCE` are the *only* values that ever hit the DB.
     - Any invalid value coming from scrapers throws a clear error with context (event name, URL).

2. **Sponsorship tiers invariants**
   - Guarantee:
     - Every stored tier has non‑empty `tier_name`.
     - `price` is either `null` or a valid float (no strings left).
     - No legacy `{name, amount, link}` can slip into the DB without being normalized.
   - Add tests (see section C) that:
     - Feed in legacy format and confirm normalized tiers.
     - Feed in invalid tier (e.g., missing tier_name, non‑numeric price) and assert a clean error.

3. **Escalation invariants**
   - Make sure any creation/update path for `Escalation`:
     - Enforces `queue_status` ∈ {queued, assigned, resolved}.
     - Enforces `priority` ∈ {low, medium, high, critical}.
     - Guarantees `errors` is always a list (empty list at minimum).
   - Design a **state transition table**:
     - e.g., `queued → assigned → resolved`, and what `next_state` should be at each step (`WAITING_FOR_VOLUNTEER`, `ACTIVE_HANDOFF`, `RESOLVED`).
   - Document that in `escalations-schema.md`.

Deliverable: **Guaranteed data cleanliness** for scrapers, DB, and escalations, with written invariants.

---

#### C. Test Suite Focused on Your Areas

**Goal**: Sponsored‑level reliability proof for your pieces.

1. **Event storage & sponsorship tiers tests**
   - In `validation_tests/test_event_storage.py` (or a new test module), add tests covering:
     - Valid canonical payload from Chanakya’s samples (like Dallas Spiritual Retreat) → stored correctly → fetched via API with the same structure.
     - Legacy sponsorship format `{name, amount, link}` → normalized to `{tier_name, price, description}`.
     - Invalid sponsorship tiers (missing name, non‑numeric amount) → raise clear `ValueError`.
     - Invalid recurrence_pattern → Pydantic `ScrapedEventPayload` rejects it (before DB).

2. **Escalation contract tests**
   - Add tests (e.g., `tests/test_escalations_api_contract.py`) that:
     - POST creates an escalation and asserts response JSON exactly matches:
       - Has all fields: `success, ticket_id, queue_status, assigned_volunteer, next_state, message_for_user, priority, errors`.
       - Types are correct (e.g., `errors` is a list).
     - GET by ticket returns the same shape.
     - State transitions update `queue_status` and `next_state` as per your mapping table.

3. **End‑to‑end schema sanity check**
   - A simple “golden data” test that:
     - Loads one of Chanakya’s sample event JSONs (slightly adapted for your internal format).
     - Runs it through your full path: Pydantic → `normalize_event_payload` → DB → `event_to_dict`.
     - Asserts that the final API shape matches all the sponsor’s required fields (at least for the ones you populated).

Deliverable: **A test suite you can point to when asked, “How do you know your schema matches the product spec?”**

---

#### D. Documentation for Team 4A & Sponsor

**Goal**: Anyone can understand your schemas and contracts in 5–10 minutes.

1. **`docs/schema-decisions.md` (already present, just expand)**
   - Sections:
     - **Events** — one table mapping canonical‑field → DB column → JSON response.
     - **Sponsorship tiers** — detailed explanation of `{tier_name, price, description}`, legacy mapping, and examples from Chanakya’s Sample 3.
     - **Recurrence** — supported patterns and what they mean (daily, weekdays, weekly:monday, etc.).

2. **`escalations-schema.md` clean final version**
   - Show:
     - DB table schema.
     - API response JSON example (as you already have).
     - Status & state mapping table.
     - Notes on auth (4B’s Bearer requirements) so Team 4A knows how to call it.

3. **Sample JSON bundle**
   - Check in a small file under something like `data/sample-events-from-chanakya.json` (or align with team conventions) containing:
     - Cleaned versions of the four sample events you pasted, in **your canonical format**.
   - This acts as a living contract and test fixture for both 4A and 4B.

Deliverable: **Clear docs that Chanakya can link from his Week 7 schema doc saying “4B’s implementation here.”**

---

### 4) How to talk about this work to the sponsor

When you summarize your contribution, you can truthfully say:

- **“I own schema alignment for both events and escalations.”**
- **“I ensured sponsorship tiers, recurrence, and escalations strictly match the product spec, with validators, migrations, and tests.”**
- **“I wrote the schema decision docs that 4A uses as the ground truth for their bot templates and escalation flow.”**

If you want, I can next help you:

- Draft the exact **tables in markdown** you should paste into `schema-decisions.md`, and  
- Draft 2–3 **test cases** (inputs/expected outputs) you can directly turn into pytest tests.

