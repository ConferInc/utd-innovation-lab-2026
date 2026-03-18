# Authentication & Security Layer — Week 5

## Overview

This module implements the security layer for the Team 4B WhatsApp bot.  
Its purpose is to ensure that webhook requests received by the bot are legitimate and originate from Twilio's infrastructure.

Webhook endpoints are publicly exposed, which means malicious actors could attempt to send fake requests.  
To prevent this, Twilio provides a request signature mechanism that allows the server to verify the authenticity of every incoming webhook.

## Twilio Webhook Signature Verification

Each request sent by Twilio includes a header:

`X-Twilio-Signature`

This signature is generated using:
- the webhook URL
- request parameters
- the Twilio Auth Token

The bot recomputes this signature and compares it with the header value.

If the signatures match, the request is valid.  
If they do not match, the request is rejected with:

`HTTP 401 Unauthorized`

## Middleware Security Layer

A middleware layer (`TwilioAuthMiddleware`) is added to the FastAPI application.

This middleware:
- intercepts incoming webhook requests
- verifies the Twilio signature
- blocks unauthorized requests before they reach the bot logic

## Internal API Authentication

For backend service-to-service communication, protected endpoints require:

`Authorization: Bearer <internal_api_token>`

## Security Benefits

This approach:
- prevents spoofed webhook requests
- ensures only Twilio can trigger bot actions
- protects internal APIs from unauthorized access
- keeps auth logic centralized and reusable