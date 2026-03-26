# Render Deployment Guide 

This document serves as a guide on how to deploy the JKYog WhatsApp Bot on Render. 

## 1. Overview 
The bot for week 6 is currently deployed as a Python web service on Render. The appllication uses FastAPI as the backend framework and Univcorn as the ASGI server. 

The deployment uses the following tools and services:
- Render Web Service 
- Python 3.11
- `4B/week6/requirments.txt` for dependencies 
- `4B.week6.main:app` as the application entrypoint

## 2. Render Configuration

This project includes a `render.yaml` file with the setup below:

```yaml
services:
  - type: web
    name: jkyog-whatsapp-bot-week6
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r 4B/week6/requirements.txt
    startCommand: |
      uvicorn 4B.week6.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```
## 3. Prerequisites

Before deploying, ensure you have the following:
- A GitHup repository containing the project
- A Render account 
- A PostgreSQL database
- Twilio WhatsApp sandbox access 
- The require environments ready 

Optional integrations may also require the following: 
- Google API/Gemini key 
- Google Maps API key
- Google Calendar credentials 
- Stripe keys or donation links 

## 4. Creating the Web Service

To create the Web service follow the steps below:

**Step 1: Push the repository to Github**

Make sure the latest week 6 code is pushed to GitHub in the correct branch. 

**Step 2: Log in to Render**

Go to the Render dashboard and create a new **Web Service**.

**Step 3: Connect the GitHub repository**

Authorize Render to access the repository and select the project repository. 

**Step 4: Confirm service settings**

Render should use the configuration from `render.yaml` is detected. If the values are entered manually, use the same. bild and start commands shown below. 

## 5. Build and Start Commands 
The following commands ensure Render installs the right dependencies and starts the Week 6 FastAPI application.
### Build Command
```bash
pip install --upgrade pip
pip install -r 4B/week6/requirements.txt
```
### Start Command
```bash
uvicorn 4B.week6.main:app --host 0.0.0.0 --port $PORT
```

## 6. Required Environment Variables
Set the following variables in the Render dashboard under the **Environment** tab. 

### Rquired Variables for Core App Functionality 
| Variable               | Purpose                                               |
| ---------------------- | ----------------------------------------------------- |
| `DATABASE_URL`         | PostgreSQL connection string used by the app database |
| `TWILIO_ACCOUNT_SID`   | Twilio account SID                                    |
| `TWILIO_AUTH_TOKEN`    | Twilio authentication token                           |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sender number                         |
| `GOOGLE_API_KEY`       | Used for Gemini-powered bot responses                 |

### Optional but Recommended Variables
| Variable | Purpose |
|----------|--------|
| `LOG_LEVEL` | Logging level (default: INFO) |
| `GEMINI_MODEL` | Model used for AI responses |
| `GOOGLE_MAPS_API_KEY` | Enables Google Maps directions and geocoding |
| `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON` | Path to Google Calendar service account JSON file |
| `GOOGLE_CALENDAR_ID` | Google Calendar ID (default: primary) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Alternative credential path used by Calendar wrapper |
| `STRIPE_SECRET_KEY` | Enables Stripe payment intents |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key for frontend usage |
| `STRIPE_DEFAULT_LINK` | Default Stripe donation link |
| `STRIPE_DALLAS_LINK` | Dallas temple donation link |
| `STRIPE_IRVING_LINK` | Irving temple donation link |
| `STRIPE_HOUSTON_LINK` | Houston temple donation link |

## 7. Database Setup
The application initializes the databas during the startup. 
### What to do?
- Create a PostgreSQL database on Render or Supabase 
- Copy the database connection string
- Set it as `DATABASE_URL` in Render 
### How to Verify
After deployment, check the following: 
```bash
GET /health 
GET /health/db

```
The expected results are as followed:
- `/health` returns a basic success response 
- `/health/db` confirms database health or returns degraded/error status 

## 8. Twilio Webhook Setup
After Render deployment is a success, connect Twilio to the live service. 

### Webhook URL

```bash
https://<your-render-service>.onrender.com/webhook/whatsapp
```
### What this Endpoint Does 
- Recieves incoming WhatsApp messages 
- Verifies the Twilio request signature 
- Authenticates the user
- Starts or resumes a session
- Classifies intent 
- Generates a response
- Sends a WhatsApp reply 

**Important:** The deployment public URL must match what Twilio calls, because signature validation depends on the request URL. 

## 9. Health Checks and Test Endpoints 
After deployment, test the following endpoints:
### Root endpoint
``` 
GET /
```

**Expected Response:**
```JSON
{"message": "JKYog WhatsApp Bot is running"}
```

### Health Endpoint
```
GET /health
```
**Expected Response:**
```JSON
{"status": "ok"}
```

### Database Health Endpoint
```
GET /health/db
```
Use the above to confirm database connectivity. 

### Additional Test Endpoints 
Below are some additional points that help verify integrations.
```
GET /maps
GET /calendar
POST /create-payment
```

## 10. Common Deployment Issues
### Issue 1: App Fails During Startup
**Possible Causes**

- Missing `DATABASE_URL`
- Dependency installation failure
- Invalid startup path 

**How to Resolve it**
- Verify environment variables
- Confirm `requirements.txt` path is correct
- Confirm start command is `unicorn 4B.week6.main:app --host 0.0.0.0 --port $PORT`

### Issue 2: Database Health Check Fails
**Possible Causes**
- Bad `DATABASE_URL`
- Database not running 
- Database access blocked

**How to Resolve it**
- Recheck the database credentials
- Confirm the database service is live
- test `/health/db`

### Issue 3: WhatsApp bot Does not Reply
**Possible Causes**
- Wrong Twilio webhook URL
- Missing Twilio credentials
- Invalid signature validation
- Background task error

**How to Resolve it**
- Verify the webhook URL in Twilio sandbox
- Verify `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_WHATSAPP_FROM`
- Check the render logs for webhook and send-message errors

### Issue 4: Maps, Calendar, or Stripe Endpoints Fail
**Possible Causes**
- Missing API keys
- Bad credentials
- Optional integration is not configured 

**How to Resolve it**
- Set the right environment variables
- Verify the wrapper configuration 
- Check the endpoint logs in Render

## 11. Deployment Checklist
Before marking the deployment complete, the following must be verified:
- The repository is connected to Render
- The build completes successfully 
- The app starts successfully
- `DARABASE_URL` is set
- Twilio variables are set
- `/health` works
- `/health/db` works
- The Twilio sandbox points to the deployed webhook URL
- The optional ontegrations are configured if needed




