# Week 7 Assignment — Group 4A
## Event Discovery UX Design & Data Architecture
**Sprint: March 30 – April 2, 2026**

---

## 🎯 This Week's Mission

The JKYog WhatsApp Bot needs to answer questions like:
- "What's happening at the temple tonight?"
- "When is Hanuman Jayanti?"
- "What time is Sunday Satsang?"
- "Is there parking for Ram Navami?"
- "How do I sponsor an event?"

Your job this week: **Design the complete user experience for event discovery** and **define the data model** that makes it possible.

---

## Context: How Temple Events Work Today

The Radha Krishna Temple of Dallas manages events across two websites:
- **radhakrishnatemple.net** — Homepage event carousel + individual event pages (schedules, parking, sponsorships, food)
- **jkyog.org/upcoming_events** — Organization-wide event calendar (retreats, programs, Dallas-specific events)

There is no API or calendar feed. Events are published as HTML pages, typically 1-2 months in advance. The bot needs to work with data scraped from these pages.

The temple also has **recurring daily/weekly programs** that rarely change:
- **Darshan:** Mon-Fri 9:30am-1pm & 5:30pm-8:30pm; Sat-Sun 9:30am-8:30pm
- **Aarti:** 12:15pm & 7:00pm daily
- **Bhog:** 12:00pm & 6:45pm daily
- **Sunday Satsang:** 10:30am-12:30pm
- **Daily Bhajans:** 7:00pm-8:00pm
- **Mahaprasad:** Friday dinner & Sunday lunch

---

## Individual Assignments

### Rujul Shukla (Team Lead) — Event Query Intent Design
**Design the complete set of user intents for event discovery.**

Deliverables:
1. **Intent Catalog** — Minimum 8 distinct event-related intents:
   - Time-based: "What's happening today/tonight/this weekend?"
   - Event-specific: "When is [event name]?"
   - Recurring: "What time is darshan/Satsang/aarti?"
   - Logistics: "Is there parking for [event]?", "Where is [event]?"
   - Financial: "How do I donate/sponsor for [event]?"
   - Discovery: "What events are coming up this month?"
   - Ambiguous: "Tell me about Navratri" (could be schedule, could be description)
   - Negative: "Is there anything happening on [date with no events]?"

2. **Conversation Flow Diagrams** for each intent (Mermaid format)
   - Include: clarification prompts, multi-result handling, no-result handling
   - Example: User asks "What's happening this weekend?" → bot lists 3 events → user picks one → bot shows details

3. **Edge Cases Document:**
   - Multi-day events (Ram Navami spans 4 days)
   - Overlapping events (Health Fair + Annamacharya on same day)
   - Past events (user asks about something that already happened)
   - Events on jkyog.org vs radhakrishnatemple.net (different sources)

---

### Chanakya Sairam Varma Alluri — Event Data Model & Response Templates
**Define the canonical event schema that both teams will use.**

Deliverables:
1. **Event Data Model (JSON Schema):**
   ```
   Required fields: id, name, start_datetime, end_datetime, location, source_url
   Optional fields: description, parking_notes, sponsorship_tiers[], food_info, 
                     image_url, is_recurring, recurrence_pattern, category, 
                     venue_details, special_notes
   ```
   - Must handle: single-day events, multi-day events, recurring programs, all-day events
   - Include sample JSON for 3+ real events from the temple website

2. **WhatsApp Response Templates:**
   - Single event detail (with character limits — WhatsApp max 4096 chars)
   - Event list (today's events, weekend events, monthly overview)
   - "No events found" response
   - Sponsorship/donation response with links
   - Parking & logistics response
   
3. **Data Source Mapping:** For each field in your schema, document WHERE on the temple website(s) that data comes from (which HTML element, which page)

---

### Ananth Subramaniam Vangala — Recurring Schedule Model & "What's Happening Now?" Logic
**Build the time-awareness layer for the bot.**

Deliverables:
1. **Recurring Schedule Data Structure:**
   - Model all recurring programs (darshan, aarti, bhog, Satsang, bhajans, Mahaprasad)
   - Handle day-of-week variations (weekday vs weekend darshan times)
   - Handle exceptions (e.g., darshan closed during eclipse)

2. **"Right Now" Decision Logic:**
   - Given current day/time → what's happening RIGHT NOW?
   - Given current day/time → what's NEXT?
   - Given a future date → what's the full schedule?
   - State diagram showing how the bot determines temporal context

3. **Time Zone Handling:**
   - All events in CST/CDT
   - Handle user messages from different time zones
   - "This evening" vs "tonight" vs "today" disambiguation

---

### Nikita Pal & Harshith Bharathbhushan — Tech Debt Resolution + Events API Contract
**Clean up ALL outstanding documentation issues and extend the API contract for events.**

Deliverables:
1. **TECH DEBT (Critical — Overdue):**
   - **Shared Vocabulary Table** — Define every term used across both teams' docs (escalation, intent, slot, state, webhook, etc.) with consistent definitions. This has been outstanding for 4 weeks.
   - **Doc Contradiction Audit** — Find and fix EVERY instance of: TwiML vs JSON inconsistency, /v2/ prefix vs no prefix, Bearer auth vs no auth. Create a changelog documenting what was wrong and what was fixed.

2. **Events API Contract v2.1:**
   - `GET /events` — List all upcoming events (with pagination)
   - `GET /events/today` — Today's events + currently active recurring programs  
   - `GET /events/{id}` — Single event detail
   - `GET /events/search?q={query}` — Full-text search across event names/descriptions
   - `GET /events/recurring` — All recurring programs with schedules
   - Include: request/response schemas, error codes, rate limiting, SLA expectations

---

## Deadline

**Wednesday, April 2, 2026 at 11:59 PM CST**

Submit your weekly summary email to `students@mail.confersolutions.ai` AND push all deliverables to the repo under `4A/week7/`.

## Git Requirements
- Branch: `4A-week7-[your-name]`
- PR into `main` by deadline
- Individual file ownership — your name in the filename or directory
