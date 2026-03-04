# Week 3 Assignment — JKYog WhatsApp Bot
## Team 4B: Engineering & Bot Development

**Due:** Friday, March 6, 2026, 11:59 PM CST  
**Team Deliverable:** Working bot prototype (2+ intents using Knowledge Base)

---

## 🎯 PROJECT CONTEXT

You are building a functional WhatsApp bot prototype for JKYog. This is hands-on engineering — you will write code that actually runs.

**Technical Stack:**
- Backend: Python (Flask/FastAPI) or Node.js
- Database: Supabase/PostgreSQL
- Embeddings: text-embedding-3-small (OpenAI API preferred, local fallback if no key)

---

## 👤 INDIVIDUAL TASKS & FILE OWNERSHIP

### Chakradhar Gummakonda — Database Layer
**Your files:**
- `database/schema.py`
- `database/models.py`
- `database/state_tracking.py`

**Your task:** Design and implement database tables for:
- Users (phone numbers, preferences)
- Conversations (message history)
- Session state (context tracking)

---

### Sysha Sharma — Authentication Layer
**Your files:**
- `auth/auth.py`
- `auth/session_manager.py`
- `auth/phone_verification.py`

**Your task:** Implement:
- Phone-based authentication
- Session token management
- User identification across conversations

---

### Rohan Kothapalli — Bot Logic Core
**Your files:**
- `bot/intent_classifier.py`
- `bot/entity_extractor.py`
- `bot/response_builder.py`

**Your task:** Build the core bot engine:
- Intent classification using text-embedding-3-small
- Entity extraction from user messages
- Response generation logic

---

### Subodh Krishna Nikumbh — API Integrations
**Your files:**
- `integrations/google_maps.py`
- `integrations/stripe.py`
- `integrations/calendar.py`

**Your task:** Implement external API connections:
- Google Maps for temple directions
- Stripe for donation links
- Calendar API for event queries

---

### Leena Hussein — Knowledge Base / RAG Pipeline
**Your files:**
- `knowledge_base/faqs.json`
- `knowledge_base/events.json`
- `knowledge_base/ingestion.py`

**Your task:** Build the content layer:
- Format temple FAQs into structured JSON
- Structure event schedules and directions data
- Create ingestion pipeline that converts raw content into searchable format
- Ensure Rohan's bot logic can query your knowledge base

---

## ⚠️ CRITICAL: GIT WORKFLOW REQUIREMENTS

**Team 4B failed Git hygiene in Week 1. This is mandatory for Week 3:**

1. **Individual branches only** — Each member works on their own branch
2. **File ownership** — Edit only your assigned files (see above)
3. **No cross-file editing** — Coordinate via Slack if you need changes to someone else's code
4. **Atomic commits** — Commit frequently with descriptive messages
5. **PR merges only** — No direct pushes to main
6. **One consolidated PR** per team at submission time

**Failure to follow = rejected submission**

---

## 📝 SUBMISSION REQUIREMENTS

1. **Code:** Working Python/Node.js bot that handles at least 2 intents
2. **Integration:** Uses Leena's Knowledge Base for responses
3. **External API:** At least one working integration (Google Maps preferred)
4. **Documentation:** README explaining how to run the bot
5. **Deadline:** Friday, March 6, 2026, 11:59 PM CST
6. **Repository:** Upload to `4B/week3/` directory

---

## 📅 FRIDAY MEETING

**Team 4B Call:** Friday, March 7, 2026, 12:00 PM – 1:00 PM CST

Come prepared to demo your working prototype.

---

*This assignment was designed by Shrikanth Vilvadrinath and approved for distribution.*
