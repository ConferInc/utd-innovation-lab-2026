# Week 5 Integration Testing Guide

## 1. Purpose

This document explains how Group 4B will test the JKYog WhatsApp bot end to end against Group 4A’s API Contract v2.0. It covers environment setup, endpoint validation, webhook flow testing, service integration testing, offline mock testing, and expected-versus-actual response comparison.

## 2. Scope

This guide covers the following integration areas:

- Twilio WhatsApp webhook processing
- Authentication and session handling
- Bot response generation
- Outbound Twilio message delivery
- Stripe donation flow
- Google Maps directions flow
- Google Calendar and event retrieval flow
- Mock testing when real services are unavailable

This guide is for Week 5 integration readiness and cross-team validation. 

## 3. Files Used for Testing

The following files were used to prepare this guide:

- `main.py` - unified FastAPI entrypoint and webhook orchestration
- `auth.py` — request validation and authentication handling
- `stripe.py` — donation link routing
- `google_maps.py` — directions generation
- `calendar.py` — event lookup with API and knowledge-base fallback
- `week_5_api_contract_v_2_twilio_complete.md` — shared Team 4A and Team 4B API Contract v2.0

## 4. Environment Setup

### 4.1 Prerequisites

Before running integration tests, make sure the following are available:

- Python 3.10+
- pip
- virtual environment support
- Git
- repository access
- Twilio credentials
- Google Maps API key
- Google Calendar credentials
- Stripe payment links

### 4.2 Branch Setup

```bash
git checkout main
git pull origin main
git checkout -b feature/week5-integration-docs
git push -u origin feature/week5-integration-docs
```
### 4.3 Virtual Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4.4 Start the App
```bash
uvicorn main:app --reload
```

## 5. Admin Runbook
### Running the Event Pipeline

1. Run scraper:
   python scripts/scrape_events.py

2. Seed database:
   python scripts/seed_database.py

3. Verify data:
   GET /events/today

### Refreshing Data
- Re-run scraper and seed scripts

### Monitoring
- Check logs for scraper errors
- Verify database entries are updated

## 6. Required Environment Variables
The current implementation depends on the following environment variables:

- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_FROM
- GOOGLE_MAPS_API_KEY
- GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON
- GOOGLE_CALENDAR_ID
- STRIPE_DEFAULT_LINK
- STRIPE_DALLAS_LINK
- STRIPE_IRVING_LINK
- STRIPE_HOUSTON_LINK
- LOG_LEVEL (optional)

These values are referenced by the main application and integration modules.


### 6.1 Example `.env` Template

```env
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

GOOGLE_MAPS_API_KEY=your_google_maps_key
GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON=/absolute/path/to/service-account.json
GOOGLE_CALENDAR_ID=your_calendar_id

STRIPE_DEFAULT_LINK=https://buy.stripe.com/test_default
STRIPE_DALLAS_LINK=https://buy.stripe.com/test_dallas
STRIPE_IRVING_LINK=https://buy.stripe.com/test_irving
STRIPE_HOUSTON_LINK=https://buy.stripe.com/test_houston

LOG_LEVEL=INFO
```

## 7. Available Test Endpoints

The main application currently exposes these endpoints:

### 7.1 GET /health
Returns:
```json
{"status": "ok"}
```

### 7.2 GET /
Returns:
```json
{"message": "JKYog WhatsApp Bot is running"}
```

### 7.3 POST /create-payment
Creates a Stripe payment intent through the Stripe integration client and returns a client_secret.

### 7.4 GET /maps
Runs a Google Maps geocode test using "Dallas".

### 7.5 GET /calendar
Runs a Google Calendar or knowledge-base event test using the calendar integration client.

### 7.6 POST /webhook/whatsapp
Main WhatsApp webhook endpoint for inbound user messages. This is the primary endpoint for end-to-end integration testing.



## 8. End-to-End Webhook Flow

The webhook flow in main.py is:

1. Request hits POST /webhook/whatsapp  
2. verify_whatsapp_request() validates and parses the incoming request  
3. If the event is not a user message, the app returns: 
```json
{
  "status": "ignored",
  "message": "Non-message event ignored"
}
```

4. The application extracts:
   - user
   - conversation
   - session
   - message_text
   - phone_number
   - profile_name  

5. The bot classifies the intent using classify_intent  
6. The inbound message is logged using log_message  
7. The response is generated using build_response  
8. The bot sends the WhatsApp reply through Twilio using client.messages.create  
9. The session context is updated using update_session_context  
10. The outbound message is logged  
11. The endpoint returns a JSON success response with:
   - status
   - reply
   - user_id
   - conversation_id
   - session_token  



## 9. Team 4A Contract Requirements

### 9.1 Inbound Request Format
- Content-Type: application/x-www-form-urlencoded  

Expected fields:
- MessageSid
- From
- Body
- ProfileName  

### 9.2 Normalization Rule
- Remove "whatsapp:"
- Remove "+"

Example:
whatsapp:+19725550123 → 19725550123  

### 9.3 Internal Unified JSON Schema

Expected structure:
- message_id
- user_id
- user_name
- text
- timestamp
- language
- session_token
- channel  

### 9.4 Required Headers
- Content-Type: application/x-www-form-urlencoded  
- X-Session-Token  
- Authorization: Bearer token  

### 9.5 Expected Success Response
- status: success  
- reply_text: bot message  
- next_state: conversation state  
- session_token  

Note: reply_text must match the Twilio outbound message.

### 9.6 Expected Error Codes
- 200 → ignored events  
- 400 → invalid input  
- 401 → auth failure  
- 500 → internal error  



## 10. Authentication and Security Testing

### 10.1 What to Validate
- Webhook request parsing works
- Non-message events are ignored
- Session handling works
- Invalid payloads are rejected
- Errors are logged properly 

### 10.2 Auth Test Cases

Test Case A — Valid Request  
- Expected: request processed successfully  

Test Case B — Non-Message Event  
- Expected: 200 + ignored  

Test Case C — Invalid Payload  
- Expected: 400  

Test Case D — Session Reuse  
- Expected: session token persists  

Test Case E — Internal Failure  
- Expected: 500 error  



## 11. Service Integration Test Scenarios

### 11.1 Donation Flow (Stripe)
- returns temple-specific Stripe link  
- fallback: default Stripe link  

Test input:
"I want to donate to Dallas temple"



### 11.2 Directions Flow (Google Maps)
- returns directions with distance + duration  
- fallback: placeholder message  

Test input:
"How do I get to the temple from downtown Dallas?"


### 11.3 Event Inquiry Flow (Calendar)
- primary: Google Calendar API  
- fallback: knowledge_base/events.json  
- fallback 2: built-in data  

Test input:
"What events are happening this weekend?"



## 12. Online Integration Testing Procedure

Step 1: Run the app  
Step 2: Check /health and /  
Step 3: Verify environment variables  
Step 4: Send request to /webhook/whatsapp  

Step 5: Verify:
- request accepted  
- intent classification runs  
- response generated  
- Twilio message sent  
- session updated  

Step 6: Test:
- donation  
- directions  
- events  
- invalid input  
- ignored events  

Step 7: Capture:
- request  
- response  
- logs  
- screenshots  



## 13. Offline Testing with Mock Server

Purpose:
- simulate API responses without real services  

Environment:
USE_MOCK_SERVER=true  
MOCK_SERVER_BASE_URL=http://localhost:3001  

Mock should simulate:
- webhook response  
- Stripe  
- Maps  
- Calendar  

The offline mock configuration is stored in `mock-server-config.json`. It simulates webhook, donation, directions, and calendar responses so Group 4B can validate request/response handling even when Team 4A’s live API or external services are unavailable.

## 14. Expected vs Actual Response Comparison


| Area | Expected | Actual | Status |
|------|---------|--------|--------|
| Content-Type | form-urlencoded | TBD | Pending |
| Ignored events | 200 ignored | Works | Match |
| Response field | reply_text | reply | Mismatch |
| Response body | includes next_state | missing | Mismatch |
| Session handling | persists | works | Match |
| Error handling | 400/401/500 | partial | Partial |



## 15. Known Integration Gaps

- reply_text vs reply mismatch  
- next_state missing  
- async processing not fully verified  
- contract vs implementation differences  

---

## 16. Troubleshooting

App not running:
- check env
- install dependencies  

Webhook issues:
- check request format
- check logs  

Twilio issues:
- verify credentials  

Maps:
- check API key  

Calendar:
- check credentials  

Stripe:
- check links  

---

## 17. Cross-Team Test Evidence Checklist

- WhatsApp screenshot  
- request logs  
- response logs  
- session token  
- comparison notes  
- issues + fixes  

---

## 18. Recommended Minimum Test Set

1. donation  
2. directions  
3. events  
4. ignored event  
5. invalid request  
6. error case  

---
## 19. Event Pipeline Architecture
The system processes temple event data through the following pipeline:

1. Scraper
   - Extracts event data from temple websites

2. Database
   - Stores structured event data

3. API Layer
   - Exposes endpoints such as /events and /events/today

4. Bot Integration
   - Uses event data to respond to user queries

This pipeline ensures real-time access to temple events.

---

## 20. Conclusion

This document ensures Group 4B’s WhatsApp bot is tested against the shared API contract and ready for cross-team integration validation.