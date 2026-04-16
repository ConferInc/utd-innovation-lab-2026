# Live Events API Proof

This document records live smoke-test results for the Week 8 Events API deployment.

## Test context

- Base URL: `https://jkyog-whatsapp-bot-week4-ffuk.onrender.com`
- Test run date (UTC): `2026-04-16`
- Tester: Cursor agent (live `curl` checks)

## Results summary

All five public Events API endpoints returned successful responses (`200 OK`).

| Endpoint | Status | Result |
|---|---:|---|
| `GET /api/v2/events` | 200 | Returned event list payload with `events`, `limit`, `offset` |
| `GET /api/v2/events/today` | 200 | Returned JSON payload (`{"events":[]}` at test time) |
| `GET /api/v2/events/recurring` | 200 | Returned JSON payload (`{"events":[]}` at test time) |
| `GET /api/v2/events/search?q=krishna` | 200 | Returned filtered event records and echoed query |
| `GET /api/v2/events/3` | 200 | Returned event detail object for `id=3` |

## Raw HTTP evidence (captured)

### 1) `GET /api/v2/events`

- Status line: `HTTP/1.1 200 OK`
- Content-Type: `application/json`

### 2) `GET /api/v2/events/today`

- Status line: `HTTP/1.1 200 OK`
- Body sample: `{"events":[]}`

### 3) `GET /api/v2/events/recurring`

- Status line: `HTTP/1.1 200 OK`
- Body sample: `{"events":[]}`

### 4) `GET /api/v2/events/search?q=krishna`

- Status line: `HTTP/1.1 200 OK`
- Body contained `q: "krishna"` and matching event objects

### 5) `GET /api/v2/events/3`

- Status line: `HTTP/1.1 200 OK`
- Body contained event object with `id: 3` (`Bhakti Kirtan Retreat 2026`)

## Negative-path check

- Endpoint: `GET /api/v2/events/999999`
- Status: `HTTP/1.1 404 Not Found`
- Body: `{"detail":"Event not found"}`

This confirms expected not-found behavior for invalid event IDs.
