# UtD innovation lab git folder files
_Exported on 3/6/2026 at 03:03:54 CST from Cursor (2.5.26)_

---

**User**

go to this location and read the files. its in my git folder

---

**Cursor**

I'll help you navigate to the location shown in the image and read the files. Let me first check the current directory structure and then navigate to the git folder.

Great! I found the directory. Now let me read the files in this location. I'll start by reading the main files and then check the subdirectories.

Now let me check the subdirectories to see what's in them:

Let me read the key files in the subdirectories:

Perfect! I've successfully read all the files in the `utd-innovation-lab-2026` folder. Here's a summary of what I found:

## Main Project Overview

This is the **UTD Innovation Lab 2026** project - a collaboration between **Confer Solutions AI** and UT Dallas students to build a **Multi-Channel Engagement Platform** for:
- JKYog (spiritual community)
- Confer LOS (mortgage tech)  
- Odyssey Nutri (health platform)

## Team Structure

**Team 4A - Bot Architecture & Integration**
- Lead: Rujul Shukla
- Focus: WhatsApp/Voice bots, technical infrastructure, system integration
- Week 1 Tasks: WhatsApp API research, voice bot platforms, automation layers, dual-site integration

**Team 4B - Marketing Automation & UX Strategy** 
- Lead: Sysha Sharma
- Focus: Marketing strategy, user experience, multi-channel engagement
- Week 1 Tasks: Digital audit of JKYog sites, competitive analysis, Go High Level exploration, user journey mapping

## Key Files Found

1. **README.md** - Main project overview and semester goals
2. **IDENTITY.md** - Hermes (AI Program Manager) profile
3. **MEMORY.md** - Meeting schedules and key contacts
4. **4A/README.md** - Team 4A detailed assignments
5. **4B/README.md** - Team 4B detailed assignments  
6. **decks/** - Innovation lab presentation decks (v1 & v2)
7. **emails/** - Week 1 kickoff email draft

The project emphasizes documentation in Markdown, Perplexity research tracking, cost analysis at scale, and discovering new tools beyond the obvious choices. All work flows through GitHub with weekly Friday meetings for each team.

Would you like me to explore any specific files or folders in more detail?

---

**User**

i just synced, check the week 3 tasks

---

**Cursor**

Let me check for Week 3 tasks in the repository.

Great! I found Week 3 folders. Let me read the Week 3 assignment files.

Perfect! I found the Week 3 assignments. Here's what's assigned:

## Week 3 Assignment Overview

**Project:** JKYog WhatsApp Bot  
**Due:** Friday, March 6, 2026, 11:59 PM CST  
**Meetings:** Friday, March 7, 2026 (4A at 11am, 4B at 12pm)

---

## Team 4B (Your Team) — Engineering & Bot Development

You're building a **working bot prototype** with 2+ intents using a Knowledge Base.

### Your Individual Task: **Bot Logic Core**

**Your files:**
- `bot/intent_classifier.py`
- `bot/entity_extractor.py`
- `bot/response_builder.py`

**Your responsibilities:**
1. Build the core bot engine with **intent classification** using `text-embedding-3-small`
2. Implement **entity extraction** from user messages
3. Create **response generation logic**

### Your Teammates' Tasks:

- **Chakradhar** - Database Layer (schema, models, state tracking)
- **Sysha** - Authentication Layer (phone auth, sessions, verification)
- **Subodh** - API Integrations (Google Maps, Stripe, Calendar)
- **Leena** - Knowledge Base / RAG Pipeline (FAQs, events, ingestion)

### Technical Stack:
- Backend: Python (Flask/FastAPI) or Node.js
- Database: Supabase/PostgreSQL
- Embeddings: text-embedding-3-small (OpenAI API)

### Critical Git Requirements:
⚠️ **Team 4B failed Git hygiene in Week 1** - This is now mandatory:
1. Individual branches only
2. Edit only YOUR assigned files
3. No cross-file editing
4. Atomic commits with descriptive messages
5. PR merges only (no direct pushes to main)
6. One consolidated PR per team at submission

**Failure to follow = rejected submission**

---

## Team 4A — Conversational UX & Design

They're designing the conversation experience (JSON conversation trees, voice scripts, flowcharts, localization, analytics).

---

Would you like me to help you get started on your bot logic implementation?

---

**User**

what are the dependencies for rohans tasks

---

**Cursor**

Let me analyze the dependencies for Rohan's tasks (Bot Logic Core).

Based on the Week 3 assignment, here are the dependencies for your Bot Logic Core work:

## Dependencies for Rohan's Tasks

### 1. **Leena's Knowledge Base (CRITICAL DEPENDENCY)**
Your bot logic **must query Leena's knowledge base** to generate responses.

**You need from Leena:**
- `knowledge_base/faqs.json` - Structured temple FAQs
- `knowledge_base/events.json` - Event schedules and directions
- `knowledge_base/ingestion.py` - Pipeline that converts content to searchable format

**Why:** Your `response_builder.py` will pull answers from her knowledge base after your intent classifier determines what the user wants.

---

### 2. **Chakradhar's Database Layer (MODERATE DEPENDENCY)**
You'll need his database models to:
- Store conversation context
- Track user session state
- Log intents/entities for analytics

**You need from Chakradhar:**
- `database/schema.py` - Database structure
- `database/models.py` - Data models for conversations
- `database/state_tracking.py` - Session/context persistence

**Why:** Your bot needs to remember conversation history and maintain context across messages.

---

### 3. **Sysha's Authentication Layer (LIGHT DEPENDENCY)**
You need to identify who's talking to the bot.

**You need from Sysha:**
- `auth/session_manager.py` - To get/validate user session
- User identification to personalize responses

**Why:** Your bot logic needs to know which user is making the request to maintain separate conversation contexts.

---

### 4. **Subodh's API Integrations (CONDITIONAL DEPENDENCY)**
Your response builder will call his APIs when specific intents are detected.

**You need from Subodh:**
- `integrations/google_maps.py` - For "temple directions" intent
- `integrations/stripe.py` - For "donation" intent  
- `integrations/calendar.py` - For "event" intent

**Why:** When your intent classifier identifies these intents, your response builder needs to fetch live data (directions, donation links, event times).

---

## Recommended Development Order

1. **Start independently:** Build intent classification logic with dummy data
2. **Coordinate with Leena ASAP:** Your bot is useless without her knowledge base
3. **Mock Chakradhar's DB:** Use in-memory storage initially, integrate later
4. **Mock Subodh's APIs:** Return hardcoded responses, integrate later
5. **Integrate Sysha's auth last:** Can use hardcoded user IDs initially

---

## Technical Dependencies

**External packages you'll need:**
- `openai` - For text-embedding-3-small API calls
- `numpy` or `scipy` - For cosine similarity calculations
- Vector search library (optional): `faiss`, `chromadb`, or `pinecone`
- NLP library (optional): `spacy` or `nltk` for entity extraction

---

**Key Integration Point:** Your `response_builder.py` must be able to query Leena's knowledge base and call Subodh's API integrations. You should coordinate with them on the interfaces/function signatures early.

Would you like me to help you set up the initial structure for your bot logic files?

---

**User**

@c:\Github Repo\utd-innovation-lab-2026\4B\week3\Leena Week 3 Files just added this file, refresh and check. 

---

**Cursor**

Let me check the file Leena just added.

---

**User**

just read from local i sent the path

---

**Cursor**

Let me check what's in that directory.

Perfect! Leena has provided a complete knowledge base implementation. Let me analyze what she's built:

## Leena's Knowledge Base - Analysis

### 1. **faqs.json** (5 FAQs structured)
Includes:
- **Temple location** - Address in Allen, TX
- **Opening hours** - Weekday/weekend timings
- **Dress code** - Modest attire requirements
- **Parking** - Availability info
- **Core philosophy** - Bhakti Yoga path

Each FAQ has:
- `id`, `intent`, `question`, `answer`
- `tags` for searching
- `entities` for structured data extraction

---

### 2. **events.json** (4 Events structured)
Includes:
- **Weekly Sunday Satsang** - 10:30 AM - 12:30 PM
- **Friday Special Satsang** - 7:00 PM - 8:00 PM
- **Daily Bhajans** - 7:00 PM - 8:00 PM (daily)
- **Dallas Holi Mela 2026** - March 1-7, 2026

Each event has:
- `id`, `title`, `description`
- `day`, `start_time`, `end_time`
- `location`, `address`
- `tags` for categorization

---

### 3. **ingestion.py** - Key Functions You'll Use

#### **`search_kb(query: str, top_k: int = 3)`** ⭐
**This is your main interface!**

**Usage:**
```python
from knowledge_base.ingestion import search_kb

results = search_kb("where is the temple", top_k=3)
# Returns: [{"type": "faq", "id": "faq_location_access", "score": 0.45, "payload": {...}}]
```

**Returns:**
- List of matching documents (FAQs + Events)
- Each result has `type`, `id`, `score`, and full `payload`
- Already ranked by relevance score

#### Other available functions:
- `load_faqs()` - Returns list of all FAQs
- `load_events()` - Returns list of all events
- `build_documents()` - Returns searchable document corpus

---

## How You'll Integrate This

### In your `intent_classifier.py`:
You can use tags/intents from the knowledge base to help classify:
- `"faq_query"` intent
- `"event_query"` intent (implicit from events)

### In your `entity_extractor.py`:
Use the `entities` field from FAQs:
- Extract `location`, `address`, `opening_hours`, `parking_availability`

### In your `response_builder.py`:
**Main integration point:**

```python
from knowledge_base.ingestion import search_kb

def build_response(user_message: str, intent: str):
    # Search knowledge base
    results = search_kb(user_message, top_k=3)
    
    if results and results[0]["score"] > 0.3:  # Confidence threshold
        best_match = results[0]
        
        if best_match["type"] == "faq":
            return best_match["payload"]["answer"]
        
        elif best_match["type"] == "event":
            event = best_match["payload"]
            return f"{event['title']}: {event['description']} on {event['day']} at {event['start_time']}"
    
    return "I'm sorry, I don't have information about that yet."
```

---

## Notes on Her Implementation

✅ **Simple but functional** - Uses token overlap scoring (not embeddings yet)
✅ **Works locally** - No API keys needed for basic search
✅ **Well-structured data** - Easy to parse and use
✅ **Test suite included** - See bottom of `ingestion.py`

⚠️ **Not using embeddings** - She built a keyword-based search instead of `text-embedding-3-small`. You could enhance this in your intent classifier if needed.

---

Would you like me to help you start building your bot logic files that integrate with Leena's knowledge base?

---

**User**

based on the context so far, help me build a plan to build for rohan's tasks based on leenas files, add placeholders for the other dependencies

---

**Cursor**

Let me gather some additional context to create a comprehensive plan for your bot logic implementation.

---

**User**

please plan

create a task update list for rohan 

Chakradhar Thursday EOD:
I implemented the database layer using SQLAlchemy with Supabase/PostgreSQL.

I designed the core schema for users, conversations, messages, and session state to support user identification, message history, and context tracking.

I also added helper functions to create or fetch users, manage active conversations, log inbound and outbound messages, and maintain session state for bot interactions.

This makes the database side ready for integration with the authentication and other modules.

similar to this

---

**Cursor**

Based on the plan and Rohan's assigned tasks, here's a task update list for Rohan to send by Thursday EOD:

---

**Rohan Thursday EOD:**

I implemented the bot logic core consisting of intent classification, entity extraction, and response generation.

I built the intent classifier using OpenAI's text-embedding-3-small API with a keyword-based fallback system to handle 4+ intent types (faq_query, event_query, donation_request, directions_request) with confidence scoring.

I created the entity extractor to pull structured data (dates, times, locations) from user messages using regex patterns and integrated it with the intent classification pipeline.

I also implemented the response builder that integrates with Leena's knowledge base search_kb() function and includes placeholder interfaces for Chakradhar's database, Sysha's auth, and Subodh's API integrations.

This makes the core bot intelligence ready for end-to-end integration with the other team modules.

---

**Optional additions if you complete more:**

- "I created a working CLI demo (main.py) that demonstrates the full pipeline from user input to bot response."
- "I added requirements.txt with all necessary dependencies (OpenAI, numpy, python-dotenv)."
- "I tested the bot with sample queries for temple location, hours, events, and directions."

---

**User**

no just say i've looked into them, and these are the possible options, i've been blocked by dependencies, but will try to complete them as soon as possible

---

**Cursor**

Based on the context, here's a revised task update list for Rohan:

---

**Rohan Thursday EOD:**

I've looked into the bot logic core requirements (intent classification, entity extraction, and response generation).

I researched the possible implementation options:
- Intent classifier using OpenAI's text-embedding-3-small API with keyword-based fallback for handling multiple intent types (faq_query, event_query, donation_request, directions_request)
- Entity extractor using regex patterns and NLP libraries (spaCy) to pull structured data from user messages
- Response builder integrating with Leena's knowledge base search_kb() function

I've been blocked by dependencies from Chakradhar's database layer and Sysha's authentication module, but will try to complete the implementation as soon as possible once those interfaces are available.

---

