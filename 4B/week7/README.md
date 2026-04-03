# JKYog WhatsApp Bot

FastAPI-based WhatsApp bot for JKYog Radha Krishna Temple.

Core features:
- Twilio WhatsApp webhook integration
- Phone-based user authentication
- Session management with state tracking
- Gemini-powered intent classification and response generation
- Knowledge base (FAQs + events)
- External integrations (Google Maps, Google Calendar, Stripe)

---

##  Quick Start (10-minute setup)

1. Push repository to GitHub  
2. Create a **Render Web Service**  
3. Add PostgreSQL database (`DATABASE_URL`)  
4. Configure environment variables  
5. Deploy  
6. Connect Twilio webhook  
7. Send a WhatsApp message → bot replies  

---

##  Prerequisites

- GitHub account  
- Render account  
- Twilio WhatsApp sandbox  
- PostgreSQL database  
- Google API key (Gemini)

Optional:
- Google Maps API key  
- Google Calendar credentials  
- Stripe API keys or donation links  

---

##  Project Structure


```
4B/week7/
├── main.py
├── requirements.txt
├── render.yaml
├── .env.example
├── alembic.ini
├── README.md
├── escalations-api.md
├── escalations-schema.md
├── file-organization-guide.md

├── api/
│ ├── init.py
│ └── escalations.py

├── authentication/
│ ├── init.py
│ ├── auth.py
│ ├── phone_verification.py
│ └── session_manager.py

├── bot/
│ ├── init.py
│ ├── entity_extractor.py
│ ├── intent_classifier.py
│ └── response_builder.py

├── database/
│ ├── init.py
│ ├── models.py
│ ├── schema.py
│ └── state_tracking.py

├── integrations/
│ ├── init.py
│ ├── calendar.py
│ ├── google_maps.py
│ └── stripe.py

├── knowledge_base/
│ ├── init.py
│ ├── events.json
│ ├── faqs.json
│ └── ingestion.py

├── migrations/
│ ├── env.py
│ ├── script.py.mako
│ └── versions/

├── service_wrappers/
│ ├── __init__.py
│ ├── base_wrapper.py
│ ├── calendar_wrapper.py
│ ├── maps_wrapper.py
│ └── stripe_wrapper.py

├── stress_test/
│ ├── stress_test_db_health.py
│ ├── stress_test_db_health_v2.py
│ ├── stress_test_escalations.py
│ ├── stress_test_escelations_results_localv1.json
│ ├── stress_test_escelations_results_localv1.txt
│ ├── stress_test_results_localv1.json
│ ├── stress_test_results_localv2.json
│ ├── stress_test_results_localv2.txt
│ ├── stress_test_results_renderv1.json
│ ├── stress_test_results_renderv2.json
│ ├── stress_test_results_renderv2.txt

├── tests/
│ ├── test_calendar_wrapper.py
│ ├── test_maps_wrapper.py
│ ├── test_stripe_wrapper.py

└── docs/
├── mock-server/
├── environment-variables.md
├── integration-testing.md
├── render-deployment.md
├── troubleshooting.md
├──  week4-gemini-fix.md
├── week5-grok-setup.md
├── week5-performance-notes.md
├── week5-pr-description.md
```

---

##  Architecture Overview

```mermaid
flowchart TD
  User[WhatsApp User] --> Twilio[Twilio Webhook]
  Twilio --> Webhook[POST /webhook/whatsapp]
  Webhook --> Auth[Authentication]
  Auth --> Session[Session Management]
  Session --> Intent[Intent Classification]
  Intent --> Response[Response Builder]

  Response --> DB[(Database Logging)]
  Response --> KB[Knowledge Base]
  Response --> Int[Integrations]
  Response --> Reply[Bot Response]

  Int --> Maps[Google Maps]
  Int --> Cal[Google Calendar]
  Int --> Stripe[Stripe]

  Reply --> User
  ```

---

## How it Works
1. Twilio sends incoming message to `/webhook/whatsapp`
2. Request is authenticated using Twilio signature validation
3. User is identified via phone number 
4. Session is either created or reused
5. Message is classified using Gemini
6. Response is generated using:
  - knowledge base
  - integrations
7. Message is logged to database
8. Reply is sent via Twilio
---

## Environment variables

**See full guide:** [Environment Variables Guide](docs/environment-variables.md)

### Required
- `DATABASE_URL`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `GOOGLE_API_KEY`

---

## Deploy to Render

**See full guide:** [Render Deployment Guide](docs/render-deployment.md)
### Build Command
```bash
pip install --upgrade pip
pip install -r 4B/week7/requirements.txt
```

### Start Command
```bash
uvicorn 4B.week7.main:app --host 0.0.0.0 --port $PORT
```

## TwilioWebhook Setup
**Set webhook URL:** 
```
https://<your-service>.onrender.com/webhook/whatsapp
```

---

## API endpoints
### Core

- `GET /` → bot running
- `GET /health` → system health
- `GET /health/db` → database health
- `POST /webhook/whatsapp` → main webhook

### Additional 

- `POST /create-payment` → Stripe payment intent
- `GET /maps` → Google Maps test
- `GET /calendar` → Google Calendar test
- `/escalations` → escalation endpoint

---

## Integrations 
- Google Maps → geocoding and directions
- Google Calendar → event retrieval (with fallback)
- Stripe → payments and donation links

---

## Troubleshooting
**See full guide:** [Troubleshooting Guide](docs/troubleshooting.md)

---

## Dependencies 
Key libraries used:
- FastAPI
- Uvicorn
- SQLAlchemy + PostgreSQL
- Twilio SDK
- Stripe SDK
- Google APIs (Maps + Calendar)
- Google Gemini (AI)
- httpx

---

*Documentation maintained by Leena Hussein (Documentation Lead).*
