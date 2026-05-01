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

### Issues Identified
- TwiML vs JSON inconsistency  
- API version mismatch (`/events` vs `/v2/events`)  
- Authentication ambiguity  
- Schema mismatch between data and backend  

### Fixes Applied
- Standardized all responses to **JSON**  
- Unified API structure → `/api/v2/events`  
- Adopted session-based authentication  
- Fully aligned with canonical schema

---

## 2. Canonical Event Schema

[Rosetta Stone](./week7_final_event_data_model_response_templates_aligned_final.md)

---

## 3. Events API Contract v2.1

### Base URL
`/api/v2/events`

### GET /events

```http
GET /api/v2/events?date=2026-04-05
```

```json
{
  "events": [],
  "count": 0
}
```

---

### GET /events/today

```http
GET /api/v2/events/today
```

```json
{
  "date": "YYYY-MM-DD",
  "events": []
}
```

---

### GET /events/{id}

```http
GET /api/v2/events/101
```

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

```http
GET /api/v2/events/search?q=holi
```

```json
{
  "results": []
}
```

---

### GET /events/recurring

```http
GET /api/v2/events/recurring
```

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

### Integration

- Response Builder → calls Events API  
- Entity Extractor → sends filters  
- Session Manager → stores context  
- Escalation → triggered when needed

---

## 4. System Reliability & Recovery Plan (Updated)

### Reliability Metrics

- Burst Capacity: Verified for 50-request spikes  
- Concurrency: Validated for 10 simultaneous users  
- SLA (Search): Target < 800ms | Max (p95) 1200ms

---

### Database Failure Recovery Process

**1. Detection**
- `503 Service Unavailable`  
- `DB Connection Refused`

**2. Graceful Degradation**
> I could not retrieve event info right now. Please try again soon.

**3. Failover Strategy**
- Update DATABASE_URL to replica

**4. Point-in-Time Recovery**

```bash
pg_restore -d jkyog_prod backup_file.dump
```

---

## 5. Post-Recovery Validation

### Migration Check

```bash
alembic upgrade head
```

### Validate API Health

```http
GET /api/v2/events/today
```

---

## 6. Architectural Note: Hybrid Response Pattern (Updated)

### Internal Communication
- JSON payloads

### External Communication
- JSON → TwiML via main.py

### Final Flow

```text
Internal Services → JSON → Response Builder → main.py → TwiML → WhatsApp
```

---

## 🎯 Final Summary

- What’s happening tonight?  
- When is Hanuman Jayanti?  
- Is there parking for Ram Navami?

---

## 📌 Superseding Note

Overrides:
- System reliability  
- Error handling  
- TwiML vs JSON architecture  

Ensures consistency across:
- API contract  
- Backend implementation  
- WhatsApp delivery layer
