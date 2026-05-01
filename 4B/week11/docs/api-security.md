# API security (Team 4A / integrators)

This page summarizes **which HTTP routes expect credentials** and which are intentionally public. Team 4A can use it to decide whether to send `Authorization` or other headers.

## Public, read-only: `/api/v2/events`

All event list and detail endpoints are **unauthenticated GET** handlers. They are **read-only** and safe to call from backend services or tools without a Bearer token.

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v2/events` | None |
| GET | `/api/v2/events/today` | None |
| GET | `/api/v2/events/recurring` | None |
| GET | `/api/v2/events/search?q=...` | None |
| GET | `/api/v2/events/{event_id}` | None |

**Team 4A:** Do **not** send `Authorization` for these calls unless you are routing through a proxy that adds its own policy. Extra headers are ignored for auth purposes.

## Protected: `/escalations`

The escalations router requires a valid **Bearer** token on every request. The server compares the token to the `ESCALATIONS_API_TOKEN` environment variable using constant-time comparison.

- **Header:** `Authorization: Bearer <token>`  
- **Env (server):** `ESCALATIONS_API_TOKEN` must be set; if it is missing, the API responds **401**.

**Routes:** `POST /escalations`, `GET /escalations/{ticket_id}`, `PUT /escalations/{ticket_id}/resolve`. JSON request/response shapes are documented in [`escalations-api.md`](../escalations-api.md) (resolve body uses `assigned_volunteer` and optional `error_note`).

## Stripe webhook: `/stripe/webhook`

`POST /stripe/webhook` is **not** protected by a shared Bearer token. Stripe signs the payload; the app verifies **`Stripe-Signature`** using your Stripe webhook secret (see Stripe integration configuration and environment variables).

**Team 4A:** Do not send a generic Bearer token expecting it to authorize Stripe webhooks; only Stripe’s signing scheme applies.

## WhatsApp webhook

`POST /webhook/whatsapp` uses **Twilio request validation** (signature / URL alignment as configured). This is separate from the events API and from escalations Bearer auth. For env names and deployment URLs, see [environment-variables.md](environment-variables.md) and [render-deployment.md](render-deployment.md).

## Quick reference

| Area | Send auth? |
|------|------------|
| `/api/v2/events/*` | No |
| `/escalations/*` | Yes — `Authorization: Bearer …` |
| `/stripe/webhook` | Stripe’s `Stripe-Signature` only |
| `/webhook/whatsapp` | Twilio-validated request (platform-managed) |

## If events become user-specific later

Current events endpoints are intentionally public because responses are read-only and do not include user-specific or sensitive data.

If the product later adds personalized data (for example saved events, user-specific recommendations, or private attendance metadata), the API should change as follows:

1. Require caller authentication on affected routes (JWT/session token or service-to-service auth).
2. Introduce authorization checks so callers can only access data they are allowed to see.
3. Split public catalog routes from private user routes (for example `/api/v2/events` stays public while `/api/v2/users/{id}/events` is protected).
4. Add audit-friendly logging for access to private endpoints and tighten rate limits.
5. Update Team 4A client guidance to send auth headers only on protected routes.
