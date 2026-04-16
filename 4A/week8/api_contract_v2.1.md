# JKYog Platform: Technical Governance & API v2.1
**Lead Architects:** Harshith Bharathbhushan & Nikita Pal  
**Date:** April 9, 2026  

---

## 🧭 Overview

This document defines the **Events API Contract v2.1** and resolves system-level inconsistencies to enable temple-aware event discovery in the WhatsApp bot.

The system is built on top of a structured **Events API and database layer**, which aggregates and normalizes data sourced from temple and JKYog websites.

This API acts as a:

- Data normalization layer  
- Aggregation layer across multiple sources  
- Contract between data ingestion, backend services, and response systems

---

## 🎯 Objective

- Align scraped data with backend consumption  
- Standardize terminology across teams  
- Provide a scalable API design  
- Support real-world user queries  

---

## 🔄 Data Sources

### Temple Website (radhakrishnatemple.net)
- Event pages (parking, food, sponsorship)

### JKYog Events (jkyog.org/upcoming_events)
- Calendar-style listings

### Recurring Programs
- Darshan  
- Aarti  
- Satsang  
- Bhajans  
- Mahaprasad  

---

## 🔗 Data Flow

Website HTML  
↓  
Scraper (Team 4B)  
↓  
Normalized Data  
↓  
Events API  
↓  
Backend (Team 4A)  
↓  
WhatsApp Bot  

---

## 1. Master Shared Vocabulary Table

This table is the "Source of Truth" for all documentation across Team 4A and Team 4B.

### Data & Engineering Domain

| Term | Definition | Owner |
|------|------------|-------|
| Raw Event | HTML-derived data scraped from JKYog/RKT websites. | 4B (Scraper) |
| Normalized Event | Cleaned + structured event object ready for the API. | 4B → 4A |
| JSON Payload | Data format extracted from a request (e.g., await request.json()). | Both |
| Metadata | Additional info (like kb_score) attached to responses. | 4B |
| PII | Personally Identifiable Information. | Security |
| Normalization | Cleaning phone formats for DB consistency. | 4B |
| Source URL | Original scraped webpage. | 4B |

### Security & Infrastructure Domain

| Term | Definition | Owner |
|------|------------|-------|
| X-Twilio-Signature | HMAC header for webhook validation. | 4B |
| X-Session-Token | Header for tracking user sessions. | 4B |
| Bearer Token | Credential for outbound API calls. | 4B |
| Service Wrapper | Abstraction layer for external APIs. | 4B |
| Base Wrapper | Standard error-handling template. | 4B |
| Webhook | Entry point for Twilio requests. | 4B |
| Health Check | Endpoint to verify system health. | DevOps |

### Logic & UX Domain

| Term | Definition | Owner |
|------|------------|-------|
| Jaccard Score | Similarity metric for matching queries. | 4B |
| Intent / Entity | User goal and parameters. | 4A |
| Event Instance | Single occurrence of an event. | Both |
| Recurring Program | Fixed schedule events. | 4A |
| No Result Scenario | Fallback when no match is found. | Both |
| Escalation | Transfer to human support. | Both |
| Session Context | Temporary user state. | 4A |

---

## ⚠️ Tech Debt Resolution

### Fixes Implemented

## Issues Identified
- TwiML vs JSON inconsistency  
- API version mismatch (`/events` vs `/v2/events`)  
- Authentication ambiguity  
- Schema mismatch between data and backend  

## Fixes Applied
- Standardized all responses to **JSON**  
- Unified API structure → `/api/v2/events`  
- Adopted session-based authentication  
- Fully aligned with canonical schema 

---

## 2. Canonical Event Schema

```json
"id": "integer",
  "name": "string",
  "subtitle": "string | null",
  "category": "festival | retreat | satsang | youth | class | workshop | special_event | other",
  "event_type": "in_person | online | hybrid | unknown",
  "is_recurring": "boolean",
  "recurrence_text": "string | null",

  "start_datetime": "ISO-8601 string | null",
  "end_datetime": "ISO-8601 string | null",
  "timezone": "string | null",

  "location_name": "string | null",
  "address": "string | null",
  "city": "string | null",
  "state": "string | null",
  "postal_code": "string | null",
  "country": "string | null",

  "description": "string | null",

  "registration_required": "boolean | null",
  "registration_status": "open | closed | unknown",
  "registration_url": "string | null",

  "contact_email": "string | null",
  "contact_phone": "string | null",

  "parking_notes": "string | null",
  "transportation_notes": "string | null",
  "food_info": "string | null",

  "price": {
    "amount": "number | null",
    "notes": "string | null"
  },

  "sponsorship_tiers": [
    {
      "tier_name": "string",
      "price": "number | null",
      "description": "string | null"
    }
  ],

  "source_url": "string",
  "source_site": "jkyog | radhakrishnatemple",
  "source_page_type": "event_detail | upcoming_events | sponsorship_page | logistics_page",

  "scraped_at": "ISO-8601 string",
  "source_confidence": "high | medium | low",
  "notes": "string | null"
}
```

---

## 3. Events API Contract v2.1

This contract specifies the retrieval logic for the JKYog Knowledge Base events.

### Base URL
`/api/v2/events`

---

### GET /events
**Description:** Fetch all upcoming events  

**Request:**  
`GET /api/v2/events?date=2026-04-05`

**Query Parameters:**
- date (YYYY-MM-DD)
- category
- start_date
- end_date
- limit

**Response:**
```json
{
  "events": [],
  "count": 0
}
```

---

### GET /events/today
**Description:** Returns today's events  

**Request:**  
`GET /api/v2/events/today`

**Response:**
```json
{
  "date": "YYYY-MM-DD",
  "events": []
}
```

---

### GET /events/{id}
**Description:** Fetch event details  

**Request:**  
`GET /api/v2/events/101`

**Response:**
```json
{
  "id": 101,
  "name": "Dallas Holi Mela",
  "parking_notes": "Available",
  "food_info": "Mahaprasad served"
}
```

---

### GET /events/search
**Description:** Search events  

**Request:**  
`GET /api/v2/events/search?q=holi`

**Response:**
```json
{
  "results": []
}
```

---

### GET /events/recurring
**Description:** Fetch recurring programs  

**Request:**  
`GET /api/v2/events/recurring`

**Response:**
```json
{
  "recurring_events": []
}
```

---

### Backend Logic

- Normalize scraped data into canonical schema
- Allow null values for missing fields 
- Deduplicate events using name + date 
- Merge multi-source data 
- Handle recurring events separately

---

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Multi-day events | Included across dates |
| Missing data | Null values |
| Duplicate events | Deduplicated |
| Ambiguous queries | Multiple results |
| No results | Empty response |

---

### ❗ Error Handling

```json
{
  "error": {
    "code": 404,
    "message": "Event not found"
  }
}
```

---

### SLA (Service Level Agreement)

| Endpoint | Response Time |
|----------|--------------|
| /events | < 500 ms |
| /events/today | < 300 ms |
| /events/search | < 800 ms |
| /events/{id} | < 400 ms |

---

###  Integration

- Response Builder → calls Events API  
- Entity Extractor → sends filters  
- Session Manager → stores context  
- Escalation → triggered when needed  

---
---

## 4. System Reliability & Recovery Plan (Updated)

This section supersedes the earlier reliability notes and reflects the **final validated system behavior** aligned with production readiness and ITM disaster recovery standards.

### Reliability Metrics
- Burst Capacity: Verified for 50-request spikes  
- Concurrency: Validated for 10 simultaneous users  
- SLA (Search): Target < 800ms | Max (p95) 1200ms  

---

### Database Failure Recovery Process

**1. Detection**  
- Automated triggers detect:
  - `503 Service Unavailable`  
  - `DB Connection Refused`  

**2. Graceful Degradation**  
- Bot layer handles API failures and returns fallback response:  
  > "I could not retrieve event info right now. Please try again soon."

**3. Failover Strategy**  
- Update `DATABASE_URL` to:
  - Read Replica  
  - Standby instance  

**4. Point-in-Time Recovery**  
- Restore from latest snapshot:
```bash
  pg_restore -d jkyog_prod backup_file.dump

## 5. Post-Recovery Validation
 
After recovery, the system must be validated to ensure full operational integrity.
 
### Migration Check
```bash
alembic upgrade head

```http
GET /api/v2/events/today

## 6. Architectural Note: Hybrid Response Pattern (Updated)

This section supersedes earlier TwiML vs JSON discussions and defines the **final agreed architecture**.

---

### Internal Communication

All internal services communicate using **JSON payloads**, which supports:

- Structured event data  
- Flexible response building  
- Easier debugging and scalability  

---

### External Communication (Twilio)

The system entry point (`main.py`) performs the final transformation:

- Converts JSON responses → TwiML (XML)  
- Ensures compatibility with Twilio’s WhatsApp protocol  

---

### Final Flow

```text id="kqsm0u"
Internal Services → JSON → Response Builder → main.py → TwiML → WhatsApp
---

## 🎯 Final Summary

This API enables the bot to answer:

- “What’s happening tonight?”  
- “When is Hanuman Jayanti?”  
- “Is there parking for Ram Navami?”

## 📌 Superseding Note

The above sections represent the **final, production-aligned updates** and override earlier assumptions regarding:

- System reliability  
- Error handling  
- TwiML vs JSON architecture  

This ensures consistency across:

- API contract  
- Backend implementation  
- WhatsApp delivery layer  
