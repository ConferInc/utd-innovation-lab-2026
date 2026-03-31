# Environment Variables 

This document serves as a guide to explain all the environment variables that are required to run the JKYog WhatsApp Bot.

All of these variables must be configured in the render dashboard under the environment tab.

## Requires Variables 

| Variable | Description |
|----------|------------|
| `DATABASE_URL` | PostgreSQL connection string required for database access |
| `TWILIO_ACCOUNT_SID` | Twilio account SID used to send WhatsApp messages |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sender number (e.g. `whatsapp:+14155238886`) |
| `GOOGLE_API_KEY` | Google Gemini API key for intent classification and responses |

## Optional Variables

| Variable | Description |
|----------|------------|
| `LOG_LEVEL` | Logging level (default: INFO) |
| `GEMINI_MODEL` | Model used for AI responses (default: gemini-2.5-flash) |
| `GOOGLE_MAPS_API_KEY` | Enables Google Maps directions |
| `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON` | Path to service account JSON file for calendar access |
| `GOOGLE_CALENDAR_ID` | Calendar ID (default: primary) |
| `STRIPE_DEFAULT_LINK` | Default Stripe donation link |
| `STRIPE_DALLAS_LINK` | Dallas temple donation link |
| `STRIPE_IRVING_LINK` | Irving temple donation link |
| `STRIPE_HOUSTON_LINK` | Houston temple donation link |
| `STRIPE_SECRET_KEY` | Required for creating Stripe payment intents |

---

## Example `.env` File

```env
DATABASE_URL=postgresql://user:password@host:port/db

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

GOOGLE_API_KEY=your_google_api_key
GOOGLE_MAPS_API_KEY=your_maps_key

STRIPE_DEFAULT_LINK=https://buy.stripe.com/test_default
LOG_LEVEL=INFO
```

---

*Documentation created and maintained by Leena Hussein — Documentation Lead, Group 4B.*