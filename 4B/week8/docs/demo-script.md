# Demo Script — April 15 Consolidated Demo Sprint

This document provides the step-by-step flow for running the Week 8 demo for the JKYog WhatsApp Bot, including local fallback instructions, database reseeding, sample API checks, and troubleshooting steps.

## 1. Demo Goal

The demo should show a real user message going through the bot and returning a response based on live or seeded temple event data.

Expected demo flow:
1. A user sends a WhatsApp message to the bot
2. Team 4A handles intent classification and response building
3. The bot calls Team 4B’s live events API
4. The user receives a real WhatsApp response with formatted temple event data

## 2. Local Fallback Startup

If the deployed environment is unavailable or unstable during the demo, run the app locally.

### Start the app locally

```bash
python -m uvicorn main:app --reload
```

### Expected startup result

Look for logs showing:

``` bash
Initializing database...
Database initialized successfully.
Application startup complete.
```
### Local app URL

```bash
http://127.0.0.1:8000
```
## 3. Pre-Demo Checklist

Before starting the demo, confirm the following:

The Week 8 branch is up to date
Required dependencies are installed
The database is reachable
The app starts with no import errors
The events endpoints return valid data
WhatsApp webhook configuration is ready if using live Twilio
Stripe webhook route is registered at /api/stripe/webhook

## 4. Database Reseed / Refresh

If the events database is empty, stale, or inconsistent, reseed or re-ingest before the demo.

### General reseed step

Run the team’s event ingestion or seed script from the Week 8 project directory.
```bash
python <seed_or_ingestion_script>.py
```
After reseeding, verify:

Events exist in the database
/api/v2/events returns records
/api/v2/events/today returns expected results for the current date
Recurring events are present if required for the demo

## 5. Health Check Endpoints

Run these first to confirm the app is working.

### Root endpoint
```bash
curl http://127.0.0.1:8000/
```
### Health endpoint
```bash
curl http://127.0.0.1:8000/health
```
### Database health endpoint
```bash
curl http://127.0.0.1:8000/health/db
```

## 6. Events API Demo Checks

Use these curl commands before the live demo to verify the events API is returning usable data.

### Get all events
```bash
curl http://127.0.0.1:8000/api/v2/events
```

### Get todays events 
```bash
curl http://127.0.0.1:8000/api/v2/events/today
```

### Get recurring events
```bash
curl http://127.0.0.1:8000/api/v2/events/recurring
```

### Search events 
```bash
curl "http://127.0.0.1:8000/api/v2/events/search?q=satsang"
```

### Get event by ID
```bash
curl http://127.0.0.1:8000/api/v2/events/1
```

## 7. Stripe Webhook Endpoint Check
The Stripe webhook route is registered at:
```bash
/api/stripe/webhook
```
If testing locally:
```bash
http://127.0.0.1:8000/api/stripe/webhook
```

## 8. Demo Message Prompts

Use prompts that match the required intent coverage.

### Time-based query
- What’s happening at the temple this weekend?
- What events are happening today?
### Event-specific query
- Tell me about Hanuman Jayanti
- What is the schedule for the next special event?
### Recurring schedule query
- What time is Sunday Satsang?
- When is the weekly satsang?
### No-results case
- Is there anything at 3 AM tonight?
- Are there any events happening overnight?

## 9. Recommended Demo Flow
### Option A — Full live demo
1. Start with the bot running
2. Send a real WhatsApp message
3. Show logs or API trace
4. Show the returned response
5. Repeat for required query types
### Option B — Local fallback demo
1. Run the app locally
2. Verify events endpoints with curl
3. Demonstrate event data exists
4. Show logs for request/response flow
5. Explain fallback usage if needed

### 10. If an Endpoint Returns Empty Results
- Verify the database was seeded successfully
- Confirm the query date range is valid
- Re-run ingestion if needed
- Check /api/v2/events first to confirm any data exists

## 11. If the Scraper Fails
- Check for source website structure changes
- Review scraper logs
- Re-run ingestion manually
- Use previously seeded data if necessary
- Document fallback clearly in PR

## 12. If the App Fails During Demo
```bash
python -m uvicorn main:app --reload
```
Then:
- Confirm database initialization logs
- Check /health and /health/db
- Retry events endpoints
- Continue with local fallback if needed

## 13. If WhatsApp Does Not Reply
- Verify Twilio webhook URL
- Confirm credentials are set
- Check server logs
- Ensure response builder runs successfully
- Confirm events API returns data

## 14. Minimum Success Criteria

The demo is successful if it shows:

- A real user message
- Intent classification working
- API call to events endpoint
- Real event-based response
- Coverage of required prompt types (or documented blockers)


