# JKYog WhatsApp Bot

## Overview

The JKYog WhatsApp Bot is a FastAPI-based conversational assistant that processes incoming Twilio WhatsApp webhook requests, authenticates users by phone number, manages sessions, logs conversations, and generates responses using bot logic, a knowledge base, and external integrations.

## Key Features
- FastAPI-based backend architecture

- Twilio WhatsApp webhook message handling

- Phone-number-based user authentication

- Session generation and context tracking

- Conversation logging with database persistence

- Intent classification and entity extraction

- Response generation using bot logic

- Knowledge base retrieval for FAQs and events

- Google Maps directions integration

- Google Calendar event lookup

- Stripe donation link integration

- Render deployment support
## Project Structure

```
4B/week4/
│
├── authentication/
│ ├── auth.py
│ ├── phone_verification.py
│ └── session_manager.py
│
├── bot/
│ ├── entity_extractor.py
│ ├── intent_classifier.py
│ └── response_builder.py
│
├── database/
│ ├── models.py
│ ├── schema.py
│ └── state_tracking.py
│
├── integrations/
│ ├── calendar.py
│ ├── google_maps.py
│ └── stripe.py
│
├── knowledge_base/
│ ├── events.json
│ ├── faqs.json
│ └── ingestion.py
│
├── main.py
├── render.yaml
├── requirements.txt
└── README.md
```
## System Architecture
```
WhatsApp User
      ↓
Twilio WhatsApp Webhook
      ↓
POST /webhook/whatsapp
      ↓
FastAPI Application (main.py)
      ↓
Authentication Layer
      ↓
Session Management
      ↓
Intent Classification
      ↓
Response Builder
      ↓
Database Logging
      ↓
External Integrations
    ├── Google Maps
    ├── Google Calendar
    └── Stripe
      ↓
Knowledge Base (FAQs + Events)
      ↓
Bot Response
```
## Prerequisites
Before running the application, the following must be installed:
- Python 3.11+
- pip
- Git
- Virtual environment tool(venv)
- Access to required API credentials
- Twilio-compatible WhatsApp webhook testing setup
## Setup Instructions
### 1. Clone the repository
- git clone https://github.com/ConferInc/utd-innovation-lab-2026.git
- cd utd-innovation-lab-2026
### 2. Create a Virtual Environment
- python -m venv venv
### 3. Activate the virtual environment
#### Mac / Linux
- source venv/bin/activate
#### Windows 
- venv\Scripts\activate

### 4. Install dependencies
- pip install --upgrade pip
- pip install -r 4B/week4/requirements.txt
## Environment Variables

Create a `.env` file in the project root and configure the following:

```env
DATABASE_URL=
LOG_LEVEL=INFO

GOOGLE_MAPS_API_KEY=

STRIPE_DEFAULT_LINK=
STRIPE_DALLAS_LINK=
STRIPE_IRVING_LINK=
STRIPE_HOUSTON_LINK=

GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON=
GOOGLE_CALENDAR_ID=primary
```


These variables configure database access and external integrations used by the bot.
## How to Run Locally

From the project root, start the FastAPI app with:
- uvicorn 4B.week4.main:app --reload

The app should be available at:
- http://127.0.0.1:8000
## API Endpoints

- GET / → confirms the bot is running

- GET /health → health check endpoint

- POST /webhook/whatsapp → main WhatsApp webhook endpoint
## WhatsApp Webhook Flow

1. Twilio sends a form-encoded WhatsApp webhook request to `POST /webhook/whatsapp`.
2. The app reads the `From`, `Body`, and `ProfileName` fields from the request payload.
3. The sender phone number is normalized by removing the `whatsapp:` prefix.
4. The user is authenticated by phone number and linked to an active conversation.
5. If an `X-Session-Token` header is present and valid, the existing session is reused; otherwise a new session is created.
6. The inbound message is logged in the database.
7. Intent classification and response generation are performed by the bot layer.
8. The session context is updated and the outbound response is logged.
9. The API returns a JSON response containing the generated bot reply.
## Integrations

### Google Maps
- Used to return temple directions based on user location and temple address.

### Google Calendar
- Used to retrieve upcoming temple events. If the API is unavailable, the bot falls back to the local knowledge_base/events.json file.

### Stripe
- Used to return pre-configured Stripe donation links for temple locations.
## Deployment (Render)
The Render deployment uses `4B/week4/requirements.txt`, which includes FastAPI, SQLAlchemy, Twilio, `python-multipart`, Google API packages, and Stripe dependencies required for the integrated bot to run successfully.

### Build Command
- pip install --upgrade pip
- pip install -r 4B/week4/requirements.txt

### Start Command
- uvicorn 4B.week4.main:app --host 0.0.0.0 --port $PORT

### Deployment Steps
1. Push the repository to GitHub.
2. Log in to Render.
3. Create a new **Web Service**.
4. Connect the GitHub repository.
5. Ensure Render detects the `render.yaml` configuration.
6. Add the required environment variables in the Render dashboard.
7. Deploy the service.
