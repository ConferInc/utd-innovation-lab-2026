# Troubleshooting Guide

This document serves as a guide for issues that might occur when trying to run or deploy the JKYog WhatsApp bot. This document explains how to fix these issues. 

## 1. App Won't Start

### Possible causes 
- `DATABASE_URL` is missing 
- Dependencies are not installed 
- The wrong start command is being used
- The Python version is not compatible

### How to Resolve it
- Make sure `DATABASE_URL` is set in the environment 
- Install the dependencies using
```bash
pip install -r 4B/week7/requirements.txt
```
- Start the app using 
```bash
uvicorn 4B.week7.main:app --host 0.0.0.0 --port 8000 --reload
```
- Confirm the Python version matches the deployment configuration

## 2. Database Connection Fails 
### Symptoms 
- App crashes during startup
- Database health check fails
- `/health/db` returns an error or degraded status
### Possible Causes
- invalid `DATABASE_URL`
- PostgreSQL service is down
- Incorrect database credentials
- Network access issue between app and database
### How to Resolve it
- Verify `DATABASE_URL` is set correctly
- Confirm the database is running
- Recheck username, password, host, port, and database name
- Test the `/health/db` endpoint after deployment
## 3. WhatsApp Webhook Returns 401
### Symptoms 
- Twilio webhook requests fail
- Requests are rejected with unauthorized errors
- Bot does not respond to incoming WhatsApp messages
### Possible Cases 
- Missing `X-Twilio-Signature`
- Invalid Twilio signature
- Missing `TWILIO_AUTH_TOKEN`
- Incorrect webhook URL in Twilio sandbox
### How to Resolve it 
- Make sure the Twilio sandbox webhook points to:
```
https://<your-service>.onrender.com/webhook/whatsapp
```
- Verify that TWILIO_AUTH_TOKEN is set correctly
- Confirm Twilio is sending requests to the exact deployed URL
- Check forwarded host/protocol headers if behind Render or another proxy

## 4. Webhook Returns Ignored Status
### Symptoms 
- APU returns 
```bash
{
  "status": "ignored",
  "message": "Non-message event ignored"
}
```
### Possible Causes 
- Request does not contain a valid `From` field
- Request does not contain a message body
- Twilio sent a status callback instead of a user message

### How to Resolve it
- Make sure the webhook request includes:
`From`
`Body`
`ProfileName` (optional but useful)
- Test using a real inbound WhatsApp message from the Twilio sandbox
- Ignore status callbacks during manual testing

## 5. Bot Receives Message But It Does Not Reply 
### Possible Causes
- Twilio credentials are incorrect
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, or `TWILIO_WHATSAPP_FROM` is missing
- Outbound message sending failed
- Background task processing failed
### How to Resolve it
- Verify all Twilio environment variables are configured
- Check application logs for Twilio send errors
- Confirm the sender number matches the Twilio sandbox number
- Make sure the app is not failing during background task execution

## 6. Google Maps Integration Fails 
### Symptoms 
- `/maps` returns an error
- Directions do not work
- Geocoding fails
### Possible Causes
- Missing `OOGLE_MAPS_API-KEY`
- Invalid API key
- Google Maps API not enabled for the project 
### How to Resolve it 
- Set `GOOGLE_MAPS_API_KEY`
- Verify the key is active in Google Cloud
- Make sure the required Maps APIs are enabled
- Check logs for wrapper-level failures
## 7. Google Calendar Integration Fails
### Symptoms
- `/calendar` returns an error
- No events are returned
- Calendar wrapper fails during initialization
### Possible Causes
- Missing credentials file
- Invalid `GOOGLE_CALENDAR_ID`
- Service account does not have calendar access
- Wrong environment variable name for credentials

### How to Resolve it
- Confirm the credentials file path is valid
- Confirm the service account has access to the calendar
- Verify `GOOGLE_CALENDAR_ID`
- Check whether the app expects:
    - `GOOGLE_APPLICATION_CREDENTIALS`
    - or `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON`
### Important note
The codebase currently uses more than one calendar credential variable name in different modules, so this should be standardized during future cleanup.

## 8. Stripe Integration Fails
### Symptoms
- `/create-payment`returns an error
- Payment intent is not created
- Donation links do not work as expected

### Possible causes
- Missing `STRIPE_SECRET_KEY`
- Invalid Stripe API key
- Invalid donation link configuration

### How to Resolve it
- Set `STRIPE_SECRET_KEY` for payment intent support
- Verify Stripe keys in the environment
- Confirm donation links such as `STRIPE_DEFAULT_LINK` are valid
- Check logs for Stripe wrapper exceptions

## 9. Render Deployment Fails
### Possible causes
- Incorrect build command
- Incorrect start command
- Missing environment variables
- App cannot access database or external APIs

### How to fix
- Use the build command from `render.yaml`
- Use the start command from `render.yaml`
- Confirm all required environment variables are set in Render
- Review Render logs for startup failures

### Expected configuration
```YAML 
buildCommand: pip install --upgrade pip && pip install -r 4B/week7/requirements.txt
startCommand: uvicorn 4B.week7.main:app --host 0.0.0.0 --port $PORT
``` 
## 10. Import or Module Errors
### Symptoms 
- `ModuleNotFoundError`
- Import failures when trying to start the app 

### Possible causes
- Wrong working directory
- Missing dependencies
- Inconsistent package paths

### How to fix
- Run the app from the repository root
- Make sure dependencies are installed
- Confirm the module path matches:
```bash
uvicorn 4B.week7.main:app --reload
```
- Check that the package folders include `__init__.py`

## 12. General debugging checklist

Before asking for help, verify the following:

- Make sure the app starts successfully
- `/health` works
- `/health/db` works
- The required environment variables are set
- Twilio webhook URL is correct
- The database is reachable
- The external API keys are valid

## 13. Stripe Webhook Issues
### Webhook returns 400
- Cause: Missing or invalid Stripe-Signature header
- Fix: Ensure STRIPE_WEBHOOK_SECRET is set correctly

### Stripe library not installed
- Cause: Missing dependency
- Fix: pip install stripe

### Payment events not processed
- Check webhook route is registered in main.py
- Check logs for event_type
---
*Documentation created and maintained by Leena Hussein — Documentation Lead, Group 4*
