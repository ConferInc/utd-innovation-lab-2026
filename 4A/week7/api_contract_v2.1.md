# JKYog Platform: Technical Governance & API v2.1
**Lead Architects:** Harshith Bharathbhushan & Nikita Pal  
**Date:** April 1, 2026  

---

## 🧭 Overview

This document defines the **Events API Contract v2.1** to enable temple-aware event discovery for the WhatsApp bot.

Since there is **no official API**, all event data is sourced via **web scraping**.  
This API acts as a:

- Normalization layer  
- Aggregation layer  
- Contract between Team 4B (scraper) and Team 4A (backend)  

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

- Standardized JSON responses  
- Unified API version → /api/v2/events  
- Session-based authentication  
- Unified event schema  

---

## 2. Canonical Event Schema

```json
{
  "id": "evt_uuid",
  "name": "Ram Navami Celebration",
  "description": "Special puja and bhajans",
  "category": "festival",
  "start_datetime": "2026-04-05T18:00:00-05:00",
  "end_datetime": "2026-04-05T21:00:00-05:00",
  "is_recurring": false,
  "location": "Radha Krishna Temple, Dallas",
  "parking_notes": "Available",
  "food_info": "Mahaprasad served",
  "sponsorship_tiers": [],
  "source_url": "https://radhakrishnatemple.net/event",
  "source_site": "radhakrishnatemple",
  "scraped_at": "ISO8601"
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
`GET /api/v2/events/evt_001`

**Response:**
```json
{
  "id": "evt_001",
  "name": "Ram Navami Celebration",
  "parking_notes": "Available",
  "food_info": "Dinner served"
}
```

---

### GET /events/search
**Description:** Search events  

**Request:**  
`GET /api/v2/events/search?q=hanuman jayanti`

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

- Normalize scraped HTML  
- Deduplicate events  
- Handle null fields  
- Support multi-day events  

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

### 🔗 Integration

- Response Builder → calls Events API  
- Entity Extractor → sends filters  
- Session Manager → stores context  
- Escalation → triggered when needed  

---

## 4. System Reliability (Stress Testing)

The platform is validated via `stress_test_db_health.py`.

- Concurrency Target: 10 requests  
- Burst Capacity: 50 concurrent  
- Sustained Load: 3 rounds testing  

---

## 🎯 Final Summary

This API enables the bot to answer:

- “What’s happening tonight?”  
- “When is Hanuman Jayanti?”  
- “Is there parking for Ram Navami?”
