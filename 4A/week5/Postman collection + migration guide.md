# Week 5 Postman Collection and Migration Guide

## JKYog WhatsApp Bot API Contract Support Document

**Authors:** Nikita Pal, Harshith Bharathbhushan

---

# 1. Version Control Summary

## API Contract Versions

* **v1.0** → Meta-style JSON contract (Week 4 baseline)
* **v2.0** → Twilio-aligned unified contract (Week 5 update)

---

# 2. Breaking Changes from v1.0 to v2.0

| v1.0 (Meta)                 | v2.0 (Twilio Unified)            | Impact                        |
| --------------------------- | -------------------------------- | ----------------------------- |
| `message_id` from Meta `id` | `message_id` from `MessageSid`   | Source field changed          |
| `user_id` from Meta `from`  | `user_id` from normalized `From` | Twilio normalization required |
| `text.body`                 | `Body` → `text`                  | Flat field mapping introduced |
| JSON webhook payload        | form-encoded payload             | Parsing layer required        |

---

# 3. Migration Guide

**Target Audience:** Team 4B (Backend Implementation)
**Revision:** 2.0 (Post-Sync)
**Objective:** Align backend request parsing and response metadata with the finalized Twilio gateway and Knowledge Base (KB) requirements.

## 1. Protocol Shift: Request Parsing
Twilio delivers webhooks as `application/x-www-form-urlencoded`. The backend must be configured to parse form-data instead of raw JSON.

### Parameter Mapping
| Previous Meta Field | New Twilio Parameter | Required Action |
| :--- | :--- | :--- |
| `user_id` | `From` | **Normalize:** Strip `whatsapp:` and `+` (e.g., `19725550123`). |
| `text` | `Body` | Map to intent engine for KB search. |
| `message_id` | `MessageSid` | Store for unique message deduplication. |
| `user_name` | `ProfileName` | Capture for personalized greeting logic. |



## 2. Response Requirements (KB Metadata)
While the inbound request is form-encoded, the **Outbound Response** from the backend must be a JSON object that includes telemetry for our analytics layer.

### New Metadata Fields
When a Knowledge Base search is performed using Jaccard overlap scoring:
$$\text{Jaccard Score} = \frac{|q \cap d|}{|q \cup d|}$$
The following fields must be included in the `metadata` object:
* **`kb_score`**: The numerical result of the Jaccard calculation.
* **`kb_source`**: The file queried (e.g., `faqs.json`).
* **`kb_id`**: The unique identifier of the matched FAQ or event.

## 3. State & Error Logic
The backend is the "Source of Truth" for session state.
* **`ERROR_STATE`**: If a KB search returns a confidence score < 0.3, the `next_state` must be set to `ERROR_STATE` to trigger fallback scripts.
* **`X-Session-Token`**: This header must be used to track the `User` and `Conversation` objects in the database, as Twilio requests are stateless.
---

# 4. Postman Collection Examples

## Request A — Twilio Format (Current Unified Flow)

```http
POST /webhook/whatsapp
Content-Type: application/x-www-form-urlencoded

MessageSid=SM12345&From=whatsapp%3A%2B19725550123&Body=Temple+timings&ProfileName=John
```

## Request B — Legacy Meta v1.0 Reference

```json
{
  "message_id": "wamid.12345",
  "user_id": "+19725550123",
  "text": "Temple timings",
  "language": "EN"
}
```

---

# 5. Expected Success Response

```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "session_token": "abc-123-session-xyz"
}
```

---

# 6. Expected Error Response

```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "session_token": "abc-123-session-xyz",
  "metadata": {
    "kb_score": 0.85, 
    "kb_source": "faqs.json"
  }
}
```

---

# 7. Purpose

This document helps both teams:

* compare v1.0 and v2.0 contracts
* test requests in Postman
* validate migration assumptions
* support end-to-end integration
