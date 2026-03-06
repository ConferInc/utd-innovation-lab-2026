---
name: Deploy WhatsApp Bot Render
overview: Complete Rohan's bot logic files and add deployment infrastructure for Render + Twilio WhatsApp sandbox integration with Supabase PostgreSQL database.
todos:
  - id: complete-intent-classifier
    content: Create bot/intent_classifier.py with OpenAI embeddings and keyword fallback
    status: completed
  - id: complete-entity-extractor
    content: Create bot/entity_extractor.py with regex patterns for dates, times, locations
    status: completed
  - id: complete-response-builder
    content: Create bot/response_builder.py with intent routing and integration handlers
    status: completed
  - id: add-init-files
    content: Add __init__.py files to authentication, database, integrations, knowledge_base modules
    status: completed
  - id: reorganize-structure
    content: Move bot folder from rohan-kothapalli to root level
    status: completed
  - id: create-fastapi-app
    content: Create app.py with FastAPI application and health check endpoint
    status: completed
  - id: create-webhook-handler
    content: Create webhook_handler.py to process Twilio webhooks and call bot pipeline
    status: completed
  - id: create-render-yaml
    content: Create render.yaml for automatic deployment configuration
    status: completed
  - id: consolidate-requirements
    content: Create consolidated requirements.txt with all dependencies including FastAPI and Twilio
    status: completed
  - id: create-env-example
    content: Create comprehensive .env.example with all API keys and configuration
    status: completed
  - id: create-gitignore
    content: Create .gitignore to exclude sensitive files and cache
    status: completed
  - id: create-readme
    content: Create detailed README.md with deployment and testing instructions
    status: completed
isProject: false
---

# Deploy WhatsApp Bot to Render with Twilio Integration

## Overview

Complete Rohan's bot logic core (intent classifier, entity extractor, response builder) and add the necessary deployment infrastructure to run the complete WhatsApp bot on Render with Twilio sandbox integration and Supabase database.

## Current Structure

```
C:\Users\rohan\Downloads\Week3 Files\
├── authentication/              (Sysha - existing)
├── database/                    (Chakradhar - existing)
├── integrations/                (Subodh - existing)
├── knowledge_base/              (Leena - existing)
└── rohan-kothapalli/           (Partial - needs completion)
    ├── bot/
    │   ├── __init__.py         (exists)
    │   ├── intent_classifier.py (NEEDS CREATION)
    │   ├── entity_extractor.py  (NEEDS CREATION)
    │   └── response_builder.py  (NEEDS CREATION)
    ├── .env.example            (exists)
    └── requirements.txt        (exists)
```

## Target Structure for Deployment

```
C:\Users\rohan\Downloads\Week3 Files\
├── authentication/
│   ├── __init__.py             (NEW)
│   ├── auth.py
│   ├── phone_verification.py
│   └── session_manager.py
├── database/
│   ├── __init__.py             (NEW)
│   ├── models.py
│   ├── schema.py
│   └── state_tracking.py
├── integrations/
│   ├── __init__.py             (NEW)
│   ├── calendar.py
│   ├── google_maps.py
│   └── stripe.py
├── knowledge_base/
│   ├── __init__.py             (NEW)
│   ├── events.json
│   ├── faqs.json
│   └── ingestion.py
├── bot/                        (MOVE from rohan-kothapalli/)
│   ├── __init__.py
│   ├── intent_classifier.py    (NEW)
│   ├── entity_extractor.py     (NEW)
│   └── response_builder.py     (NEW)
├── app.py                      (NEW - FastAPI application)
├── webhook_handler.py          (NEW - Twilio webhook logic)
├── requirements.txt            (NEW - consolidated)
├── render.yaml                 (NEW - Render deployment config)
├── .env.example                (NEW - all env vars)
├── .gitignore                  (NEW)
└── README.md                   (NEW - deployment instructions)
```

## Architecture Flow

```mermaid
flowchart TD
    WhatsApp[WhatsApp User] -->|message| Twilio[Twilio API]
    Twilio -->|webhook POST| Render[Render Web Service]
    
    Render --> FastAPI[FastAPI app.py]
    FastAPI --> WebhookHandler[webhook_handler.py]
    
    WebhookHandler --> Auth[authentication module]
    Auth --> DB[(Supabase PostgreSQL)]
    
    WebhookHandler --> IntentClassifier[bot/intent_classifier.py]
    IntentClassifier -->|OpenAI API| Embeddings[text-embedding-3-small]
    
    IntentClassifier --> EntityExtractor[bot/entity_extractor.py]
    EntityExtractor --> ResponseBuilder[bot/response_builder.py]
    
    ResponseBuilder --> KB[knowledge_base/ingestion.py]
    ResponseBuilder --> Integrations[integrations module]
    Integrations --> GoogleMaps[Google Maps API]
    Integrations --> Calendar[Google Calendar API]
    Integrations --> Stripe[Stripe Payment Links]
    
    ResponseBuilder --> StateTracking[database/state_tracking.py]
    StateTracking --> DB
    
    ResponseBuilder --> WebhookHandler
    WebhookHandler --> FastAPI
    FastAPI --> Render
    Render --> Twilio
    Twilio --> WhatsApp
```



## Implementation Plan

### Phase 1: Complete Rohan's Bot Logic Files

#### 1. [bot/intent_classifier.py](C:\Users\rohan\Downloads\Week3 Files\rohan-kothapalli\bot\intent_classifier.py)

Create intent classifier with OpenAI embeddings:

- Use OpenAI text-embedding-3-small model
- Pre-compute embeddings for training examples from knowledge base
- Support 6 intents: faq_query, event_query, donation_request, directions_request, greeting, unknown
- Keyword fallback for when OpenAI API unavailable
- Return confidence scores (0.0-1.0)

Key functions:

```python
def classify_intent(user_message: str) -> dict:
    # Returns {"intent": "faq_query", "confidence": 0.85}
```

#### 2. [bot/entity_extractor.py](C:\Users\rohan\Downloads\Week3 Files\rohan-kothapalli\bot\entity_extractor.py)

Create entity extractor with regex patterns:

- Extract dates: "March 7", "tomorrow", "next Friday" → ISO format
- Extract times: "7pm", "10:30 AM" → 24-hour format
- Extract locations: city names for directions
- Extract event types: satsang, mela, bhajan, meditation
- Context-aware based on intent type

Key functions:

```python
def extract_entities(user_message: str, intent: str) -> dict:
    # Returns {"date": "2026-03-07", "event_type": "satsang"}
```

#### 3. [bot/response_builder.py](C:\Users\rohan\Downloads\Week3 Files\rohan-kothapalli\bot\response_builder.py)

Create response orchestrator:

- Intent-based routing to handler functions
- handle_faq_query(): Query knowledge_base.ingestion.search_kb()
- handle_event_query(): Search events + calendar API
- handle_donation(): Get Stripe payment link
- handle_directions(): Call Google Maps integration
- handle_greeting(): Return welcome message
- handle_unknown(): Fallback response
- Format responses for WhatsApp (emojis, line breaks)

Key functions:

```python
def build_response(user_message: str, user_context: dict = None) -> str:
    # Returns formatted WhatsApp response string
```

### Phase 2: Add Missing **init**.py Files

Create package initialization files for all modules:

- [authentication/__init__.py](C:\Users\rohan\Downloads\Week3 Files\authentication_init__.py)
- [database/__init__.py](C:\Users\rohan\Downloads\Week3 Files\database_init__.py)
- [integrations/__init__.py](C:\Users\rohan\Downloads\Week3 Files\integrations_init__.py)
- [knowledge_base/__init__.py](C:\Users\rohan\Downloads\Week3 Files\knowledge_base_init__.py)

These enable proper Python package imports across modules.

### Phase 3: Reorganize Structure

Move and consolidate files:

1. Move `rohan-kothapalli/bot/` to root level `bot/`
2. Update all import paths to use absolute imports
3. Ensure all modules can import from sibling packages

### Phase 4: Create FastAPI Application

#### [app.py](C:\Users\rohan\Downloads\Week3 Files\app.py)

Main FastAPI application:

```python
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from database.models import get_db, init_db
from webhook_handler import handle_twilio_webhook

app = FastAPI(title="JKYog WhatsApp Bot")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/webhook")
async def twilio_webhook(request: Request, db: Session = Depends(get_db)):
    return await handle_twilio_webhook(request, db)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

Features:

- Health check endpoint for Render
- Twilio webhook endpoint at /webhook
- Database initialization on startup
- CORS configuration for security

#### [webhook_handler.py](C:\Users\rohan\Downloads\Week3 Files\webhook_handler.py)

Twilio webhook processing logic:

```python
async def handle_twilio_webhook(request: Request, db: Session):
    # 1. Parse Twilio webhook payload
    # 2. Authenticate user via phone number
    # 3. Get/create conversation context
    # 4. Process message through bot pipeline:
    #    - classify_intent()
    #    - extract_entities()
    #    - build_response()
    # 5. Log message to database
    # 6. Return TwiML response
```

Key responsibilities:

- Parse incoming WhatsApp messages from Twilio
- User authentication and session management
- Call bot logic pipeline
- Format response as TwiML for Twilio
- Error handling and logging

### Phase 5: Deployment Configuration

#### [render.yaml](C:\Users\rohan\Downloads\Week3 Files\render.yaml)

Render Blueprint configuration:

```yaml
services:
  - type: web
    name: jkyog-whatsapp-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: OPENAI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: GOOGLE_MAPS_API_KEY
        sync: false
      - key: GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON
        sync: false
      - key: STRIPE_DEFAULT_LINK
        sync: false
    healthCheckPath: /health
```

Auto-deploy on git push to main branch.

#### [requirements.txt](C:\Users\rohan\Downloads\Week3 Files\requirements.txt)

Consolidated dependencies:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
openai>=1.12.0
numpy>=1.24.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
googlemaps>=4.10.0
google-auth>=2.0.0
google-api-python-client>=2.0.0
twilio>=8.10.0
```

#### [.env.example](C:\Users\rohan\Downloads\Week3 Filesenv.example)

Template for all environment variables:

```
# OpenAI
OPENAI_API_KEY=sk-...

# Database (Supabase)
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+14155238886

# Google Maps
GOOGLE_MAPS_API_KEY=AIza...

# Google Calendar
GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GOOGLE_CALENDAR_ID=primary

# Stripe
STRIPE_DEFAULT_LINK=https://buy.stripe.com/...
STRIPE_DALLAS_LINK=https://buy.stripe.com/...
```

#### [.gitignore](C:\Users\rohan\Downloads\Week3 Filesgitignore)

Ignore sensitive and generated files:

```
.env
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
*.log
.DS_Store
```

### Phase 6: Documentation

#### [README.md](C:\Users\rohan\Downloads\Week3 Files\README.md)

Comprehensive deployment guide:

1. **Local Development Setup**
  - Clone repository
  - Create virtual environment
  - Install dependencies
  - Configure .env file
  - Run migrations
  - Start server
2. **Supabase Database Setup**
  - Create Supabase project
  - Run schema migrations
  - Copy DATABASE_URL
3. **Twilio WhatsApp Sandbox Setup**
  - Create Twilio account
  - Enable WhatsApp sandbox
  - Configure webhook URL (Render URL + /webhook)
  - Test with sandbox number
4. **Render Deployment**
  - Connect GitHub repository
  - Configure environment variables
  - Deploy from render.yaml
  - Monitor logs
5. **Testing Instructions**
  - Send test messages to WhatsApp sandbox
  - Verify bot responses
  - Check database logs

## Key Design Decisions

1. **Supabase for Database**: Using Supabase PostgreSQL instead of Render's database for better features and UI
2. **FastAPI Framework**: Lightweight, modern, and perfect for webhook handling
3. **Modular Architecture**: Keep all teammate modules separate for clear ownership
4. **Environment Variables**: All secrets in environment, never committed to git
5. **Health Checks**: Render requires /health endpoint to verify service is running
6. **Import Strategy**: Use absolute imports throughout for clarity:

```python
   from bot.intent_classifier import classify_intent
   from knowledge_base.ingestion import search_kb
   

```

1. **Database Connection**: Use connection pooling for efficient Supabase connections
2. **Error Handling**: Graceful fallbacks at every level - if OpenAI fails, use keywords; if database fails, continue without logging

## Testing Strategy

1. **Local Testing**: Run `uvicorn app:app --reload` and test with curl/Postman
2. **Unit Tests**: Test each module independently
3. **Integration Tests**: Test full pipeline with mock Twilio payloads
4. **Twilio Sandbox**: Test with real WhatsApp messages in sandbox
5. **Production**: Monitor Render logs and Supabase database

## Success Criteria

- FastAPI app runs successfully on Render
- Twilio webhook receives and processes WhatsApp messages
- Bot pipeline (intent → entities → response) works end-to-end
- All teammate modules integrate correctly
- Database logs conversations to Supabase
- Health check returns 200 OK
- README provides clear deployment instructions
- Environment variables properly configured

## Deployment Checklist

- Complete bot logic files (intent_classifier, entity_extractor, response_builder)
- Add **init**.py to all modules
- Create FastAPI app.py
- Create webhook_handler.py
- Consolidate requirements.txt
- Create render.yaml
- Create comprehensive .env.example
- Create .gitignore
- Write detailed README.md
- Test locally with mock Twilio payloads
- Push to GitHub
- Connect Render to GitHub repo
- Configure environment variables in Render
- Set up Supabase database
- Configure Twilio webhook URL
- Test with WhatsApp sandbox
- Monitor logs and fix issues

