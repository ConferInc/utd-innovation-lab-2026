# Mock Server Setup

This folder contains the mock configuration used for offline Week 5 integration testing.

## Purpose

The mock setup allows Group 4B to test integration behavior without depending on:

- Team 4A live endpoints
- Twilio live processing
- Stripe live responses
- Google Maps API availability
- Google Calendar API availability

## Files

- `mock-server-config.json` — mock route and response definitions for offline testing

## Mocked Routes

### `/mock/webhook/whatsapp`
Simulates a successful WhatsApp webhook response.

### `/mock/create-payment`
Simulates donation/payment link behavior.

### `/mock/maps`
Simulates a directions response from Google Maps.

### `/mock/calendar`
Simulates a calendar/event lookup response.

## Base URL

Use the following base URL for local mock testing:

`http://localhost:3001`

## Example Environment Variables

```env
USE_MOCK_SERVER=true
MOCK_SERVER_BASE_URL=http://localhost:3001