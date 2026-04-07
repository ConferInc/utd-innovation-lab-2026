# Week 8/9 Assignment — Group 4A
## Integration Sprint: Implement the Bot
**Sprint: April 7 – April 15, 2026**

---

## 🎯 This Sprint's Mission

Seven weeks of design, intent catalogs, data models, response templates, and API contracts. This sprint, you implement all of it.

Team 4B has a live scraper, a running database, and five working API endpoints. Your job is to write the Python code that connects the Twilio webhook to Team 4B's events API and sends a formatted WhatsApp response back to the user.

By April 15, a user must be able to send a real WhatsApp message to the bot number and get back a real response with real temple event data.

You are expected to use AI coding tools (Cursor, Copilot, Claude). This sprint tests whether you can take your own specifications and turn them into working software — not whether you can write every line from scratch.

---

## Context: What Team 4B Has Built

Team 4B's deployed stack (Render) exposes:

| Endpoint | What It Returns |
|----------|----------------|
| `GET /api/v2/events` | Paginated list of upcoming temple events |
| `GET /api/v2/events/today` | Events happening today + active recurring programs |
| `GET /api/v2/events/{id}` | Full event details (parking, sponsorship, food, logistics) |
| `GET /api/v2/events/search?q=` | Full-text search across event names/descriptions |
| `GET /api/v2/events/recurring` | All recurring programs (darshan, aarti, Satsang, bhajans) |

Data is sourced from real scrapes of `radhakrishnatemple.net` and `jkyog.org`. All endpoints are available at Team 4B's Render base URL (to be confirmed at the April 9 sync).

---

## Individual Assignments

---

### Rujul Shukla (Team Lead) — Intent Classifier Implementation
**Take your Week 7 intent catalog from design to running code.**

Your Week 7 document defined 8 intents and 5 edge cases with Mermaid flowcharts for each. Now implement the classifier that turns an incoming WhatsApp message string into one of those intents.

Deliverables:

1. **`4A/week8/intent_classifier.py`**
   - `classify(message: str) -> dict` — returns:
     ```json
     {
       "intent": "time_based",
       "confidence": 0.92,
       "entities": {
         "timeframe": "this_weekend"
       }
     }
     ```
   - Handle all 8 intents from your Week 7 design:
     - `time_based` — "What's happening this weekend?"
     - `event_specific` — "When is Hanuman Jayanti?"
     - `recurring_schedule` — "What time is Sunday Satsang?"
     - `logistics` — "Is there parking for Ram Navami?"
     - `sponsorship` — "How do I sponsor an event?"
     - `discovery` — "What events are coming up this month?"
     - `ambiguous` — "Tell me about Navratri"
     - `no_results_check` — "Is there anything at 3 AM tonight?"
   - Implement confidence threshold: if confidence < 0.6, set `intent: "clarification_needed"`
   - Use the vocabulary definitions from `api_contract_v2.1.md` for intent naming

2. **`4A/week8/entity_extractor.py`**
   - Extract structured entities from the classified message:
     - Timeframe entities: `today`, `tonight`, `this_weekend`, `this_month`, date strings
     - Event name entities: extract proper nouns that match known event names
     - Program name entities: darshan, aarti, Satsang, bhajans, Mahaprasad, bhog
   - Output maps to the query parameters Team 4B's API accepts

3. **`4A/week8/tests/test_intent_classifier.py`** — minimum 15 test cases:
   - At least 2 test messages per intent
   - At least 3 edge case / ambiguous message tests
   - Test that low-confidence inputs trigger clarification

**Note:** You may use an LLM-backed approach (call Claude/GPT to classify), a rule-based approach, or a hybrid. Document your choice and why in a brief comment at the top of `intent_classifier.py`.

---

### Chanakya Sairam Varma Alluri — Response Builder & API Integration
**Implement the response layer that calls Team 4B and formats WhatsApp messages.**

Your Week 7 data model defines the canonical event schema. Your Week 7 response templates define exactly what each WhatsApp message should look like. Now implement the code.

Deliverables:

1. **`4A/week8/response_builder.py`**
   - `build_response(classified_intent: dict, session_context: dict) -> str`
   - Calls Team 4B's events API based on the classified intent:
     - `time_based` + `this_weekend` → `GET /api/v2/events?...`
     - `event_specific` + entity → `GET /api/v2/events/search?q={entity}`
     - `recurring_schedule` + program_name → `GET /api/v2/events/recurring`
     - `logistics` + event_id → `GET /api/v2/events/{id}`
     - `sponsorship` + event_id → `GET /api/v2/events/{id}` → render sponsorship tiers
   - Formats responses using your Week 7 WhatsApp templates:
     - Single event response (title, date, time, location, link)
     - Event list (numbered, max 5 items, "reply 1-5 for details")
     - No results: "I couldn't find any events matching that. Here's what's coming up soon: [next 3 events]"
     - Sponsorship: tiers with amounts and links
     - Logistics: parking notes + food info + special notes
   - Enforces WhatsApp 4096 character limit (truncate with "...reply for more" if needed)
   - **Never fabricate data** — if a field is missing from the API response, omit it or say "Not listed on the event page"

2. **`4A/week8/api_client.py`**
   - A thin HTTP client wrapping Team 4B's events API
   - Configurable base URL via env var `EVENTS_API_BASE_URL`
   - All 5 endpoints wrapped as methods: `get_events()`, `get_today_events()`, `get_event_by_id()`, `search_events()`, `get_recurring_events()`
   - Handle: 404 (return None), 400 (raise ValueError), 500 (raise RuntimeError), timeout (30s)

3. **Schema alignment documentation:** Before you write the response builder, confirm the three field mismatches from Week 7 with Chakradhar (4B):
   - Sponsorship tier fields: `name/amount/link` vs `tier_name/price_usd/price_inr/description`
   - Event ID: integer PK vs slug
   - `source_site` enum: `jkyog` vs `jkyog.org`
   - Document the agreed-upon field names in `4A/week8/schema-alignment.md` (one page, signed off by both teams at the April 9 sync)

---

### Ananth Subramaniam Vangala — Recurring Schedule Handler
**Implement the "What's happening now?" logic from your Week 7 design.**

Your Week 7 document defined the recurring schedule data structure, the pseudocode for the "right now / what's next" algorithm, and the exception handling model. Now implement it.

Deliverables:

1. **`4A/week8/recurring_handler.py`**
   - `is_happening_now(program: str, now: datetime) -> bool`
     - Given a program name and current CST datetime, returns whether it's currently running
     - Handles weekday vs weekend schedule differences (darshan hours differ)
   - `get_next_occurrence(program: str, from_time: datetime) -> dict`
     - Returns next start time, end time, and day-of-week for the given program
   - `get_current_schedule(now: datetime) -> list`
     - Returns list of all programs currently running or starting within 2 hours
   - `get_full_day_schedule(date: date) -> list`
     - Returns complete schedule for a given date (recurring programs + any scraped events that day)
   - `check_exception(date: date) -> Optional[str]`
     - Returns exception message if a program is cancelled or modified (e.g., eclipse closure)
     - Loads exception data from `4A/week8/schedule_exceptions.json`

2. **`4A/week8/schedule_data.py`** — The recurring program schedule as a Python data structure:
   - All 5 programs: Darshan, Aarti, Bhog, Sunday Satsang, Daily Bhajans, Mahaprasad
   - Weekday vs weekend time variations for Darshan
   - Data structure that matches Team 4B's `recurrence_pattern` field format (`daily`, `weekly:sunday`, `weekdays`, `weekends`)

3. **`4A/week8/schedule_exceptions.json`** — Exception data:
   ```json
   {
     "2026-04-08": {
       "closed": true,
       "reason": "Solar Eclipse — Temple closed for the day",
       "affected_programs": ["darshan", "aarti", "bhog"]
     }
   }
   ```

4. **Integration with response_builder:** The `recurring_schedule` intent in `response_builder.py` should call `recurring_handler.get_current_schedule()` or `get_next_occurrence()` — not just call the API blindly. Recurring programs are already modeled locally; the API call to `/api/v2/events/recurring` is for Team 4B's scraped recurring events (which may differ).

---

### Nikita Pal & Harshith Bharathbhushan — Bot Entry Point, Deployment & Integration
**Wire everything together, deploy, and run the end-to-end demo.**

This is the integration task. Both of you are jointly responsible for making the bot run. Individual contributions must be traceable — see Git requirements below.

Deliverables:

1. **`4A/week8/main.py`** — The bot entry point:
   ```python
   # FastAPI (or Flask) app
   # POST /webhook — receives Twilio form-encoded webhook
   # Verifies Twilio signature (reuse Team 4B's auth.py pattern or implement)
   # Extracts: From (phone), Body (message text)
   # Calls: intent_classifier.classify(body)
   # Calls: response_builder.build_response(intent, session)
   # Returns: TwiML <Response><Message>...</Message></Response>
   ```
   - Twilio signature verification on every inbound webhook
   - Session context passed between classifier and builder (reuse `session_manager.py` from Team 4B, or build equivalent)
   - Graceful error handling: if classifier fails → "I'm having trouble understanding that right now. Try: 'What events are happening this weekend?'"

2. **`4A/week8/requirements.txt`** — All Python dependencies pinned to versions

3. **`4A/week8/.env.example`** — All required environment variables:
   ```
   TWILIO_ACCOUNT_SID=
   TWILIO_AUTH_TOKEN=
   TWILIO_PHONE_NUMBER=
   EVENTS_API_BASE_URL=         # Team 4B's Render URL
   EVENTS_API_BEARER_TOKEN=     # If Team 4B requires auth on /events
   OPENAI_API_KEY=              # If using LLM-backed classifier
   ```

4. **Deployment:**
   - Deploy to Render (free tier is fine)
   - Configure Twilio webhook URL to point to your Render deployment
   - Confirm end-to-end: send a WhatsApp message → get a response
   - Share the Render URL and the Twilio sandbox number in the PR description

5. **Schema Alignment Resolution:**
   - After the April 9 sync, update `api_contract_v2.1.md` to reflect the agreed-upon field names
   - Add superseding annotations to the Week 6 files that contained contradictions (`migration-guide.md`, `test-format-spec.md`)
   - This closes the tech debt flag that has been open since Week 5

**Git Requirements for Nikita & Harshith:**
This task requires joint delivery of a single main.py but individual branches are still mandatory.
- Harshith: branch `4A-week8-harshith` — commit `main.py`, `requirements.txt`, `.env.example`, and deployment config
- Nikita: branch `4A-week8-nikita` — commit schema alignment files and the contract update to `api_contract_v2.1.md`
- Both branches merge into `Team-4A-Week8` before the final PR

---

## Deadline

**Wednesday, April 15, 2026 at 11:59 PM CST**

Submit your weekly summary email to `students@mail.confersolutions.ai` AND push all deliverables to the repo under `4A/week8/`.

## Git Requirements
- Branch: `4A-week8-[your-name]`
- PR into `main` by deadline
- Individual file ownership confirmed by individual branch commits
- Atomic, descriptive commit messages: `feat(intent): add recurring_schedule classifier`, not `update`

## Demo Target (April 15)
Be ready to demonstrate live:
1. Send "What's happening at the temple this weekend?" → receive a formatted WhatsApp response listing real events
2. Send "What time is Sunday Satsang?" → receive the recurring schedule response
3. Send "Tell me about Hanuman Jayanti" → receive event details from Team 4B's API
4. Send "Is there anything at 3 AM tonight?" → receive the no-results response gracefully
