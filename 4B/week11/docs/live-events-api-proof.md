# Live Events API Proof

This document records live smoke-test results for the Week 8 Events API deployment.

## Test context

- Base URL: `https://jkyog-whatsapp-bot-week4-ffuk.onrender.com`
- Test run date (UTC): `2026-04-22`
- Tester: Cursor agent (live `curl` checks)
- Production DB seed target: Supabase (`postgresql://...@aws-0-us-west-2.pooler.supabase.com:5432/postgres`)

## Results summary

- Scraper run completed against both temple sources:
  - `Wrote 30 events`
  - `parse_rate=73.2%`
  - `deduped=30`
- Seed completed:
  - `Input events: 30`
  - `Inserted: 0`
  - `Updated: 30`
  - `Failed: 0`
- Live endpoint count check:
  - `GET /api/v2/events?limit=100&offset=0` returned `6` rows
  - Computed `upcoming` rows from `start_datetime >= now`: `6`

## Week 10 completion check (Task 4 requirement)

- Requirement: confirm at least `10` upcoming events.
- Current live result: `6` upcoming events.
- Status: **not yet met** (pipeline run succeeded, threshold unmet on live deployment).

## Endpoint smoke status

All five public Events API endpoints returned successful responses (`200 OK`) in earlier smoke checks.

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

## Coordination dependency (Task 5)

- Pending external confirmation: Team 4A/Harshith webhook URL alignment after hardcoded-response removal is not yet captured here.
