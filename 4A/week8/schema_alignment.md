# Schema Alignment — Week 8 API Integration

**Owner:** Chanakya Alluri  
**Project:** JKYog / Radha Krishna Temple bot integration  
**Date:** 2026-04-09  
**Related work:** Week 7 Event Data Model & Response Templates, Week 8 Response Builder & API Integration

---

## Purpose

This document records the final schema alignment between Team 4A response formatting and Team 4B event API integration before implementation of:

- `response_builder.py`
- `api_client.py`

The purpose of this alignment is to prevent response-building failures caused by mismatched field names, incompatible ID types, or inconsistent enum values.

---

## Agreed Schema Alignment

The following items were identified as critical schema mismatches and have now been aligned.

### 1) Sponsorship field names

**Final agreed structure**

```json
"sponsorship_tiers": [
  {
    "tier_name": "string",
    "price": "number | null",
    "description": "string | null"
  }
]
```

**Agreed decision**
- The canonical sponsorship field is `sponsorship_tiers`
- Each sponsorship entry uses:
  - `tier_name`
  - `price`
  - `description`

**Implementation impact**
- `response_builder.py` should read sponsorship data only from `sponsorship_tiers`
- No alternate field names such as `sponsorship_data`, `price_usd`, or `price_inr` should be assumed in the final integration layer

---

### 2) Event ID type

**Final agreed type**

```json
"id": "integer"
```

**Agreed decision**
- Event identifiers are treated as integer IDs
- Event detail lookup should use the integer event ID returned by Team 4B’s API and database layer

**Implementation impact**
- `api_client.py` should call the single-event endpoint using an integer ID
- `response_builder.py` should treat event IDs as integers in session context, follow-up selection, and event-detail resolution
- Slug-style string IDs are not part of the final aligned contract

---

### 3) source_site enum values

**Final agreed enum**

```json
"source_site": "jkyog | radhakrishnatemple"
```

**Agreed decision**
- The normalized source enum values are:
  - `jkyog`
  - `radhakrishnatemple`

**Implementation impact**
- `response_builder.py` and any mapping logic must not expect domain-name style values such as:
  - `jkyog.org`
  - `radhakrishnatemple.net`
- Any source display logic should map from the normalized enum values only

---

## Final Aligned Event Fields

The aligned event model used for response formatting and API integration is:

- `id`
- `name`
- `subtitle`
- `category`
- `event_type`
- `is_recurring`
- `recurrence_text`
- `start_datetime`
- `end_datetime`
- `timezone`
- `location_name`
- `address`
- `city`
- `state`
- `postal_code`
- `country`
- `description`
- `registration_required`
- `registration_status`
- `registration_url`
- `contact_email`
- `contact_phone`
- `parking_notes`
- `transportation_notes`
- `food_info`
- `price`
- `sponsorship_tiers`
- `source_url`
- `source_site`
- `source_page_type`
- `scraped_at`
- `source_confidence`
- `notes`

### Simplified nested fields

#### `price`
- `amount`
- `notes`

#### `sponsorship_tiers`
- `tier_name`
- `price`
- `description`

---

## Response Builder Constraints

The aligned schema above must be used together with the following response rules:

- Messages must remain within the WhatsApp 4096-character limit
- Missing values must never be fabricated
- When a field is unavailable, the response should say: `Not listed on the event page`
- The response builder must support:
  - event list
  - single event detail
  - no-results
  - sponsorship tiers
  - logistics / parking

---

## Integration Note

This alignment should be treated as the source of truth for:

- field access in `response_builder.py`
- response parsing in `api_client.py`
- any conversion logic between Team 4B API payloads and Week 7 response templates

Any future schema changes from Team 4B must be updated here before being applied in code.

---

## Status

**Resolved and aligned for implementation.**
