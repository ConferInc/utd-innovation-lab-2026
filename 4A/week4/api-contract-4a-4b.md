# API Contract 4A–4B

## JKYog WhatsApp Bot

**Authors:** Nikita Pal, Harshith Bharathbhushan

This document defines the technical API contract between **Team 4A (Conversational UX Design)** and **Team 4B (Bot Implementation)** for the **JKYog WhatsApp Bot**.

The objective is to provide an exact **request and response structure** so that Team 4B can implement backend logic consistent with Team 4A conversational flows.

---

# 1. WhatsApp Webhook Request Body Schema

When a user sends a message through WhatsApp, the webhook delivers a structured JSON payload to the bot backend.

## Request Schema

```json
{
  "message_id": "wamid.12345",
  "user_id": "+1234567890",
  "timestamp": "2026-03-10T18:30:00Z",
  "message_type": "text",
  "text": "Temple timings",
  "language": "EN",
  "session_id": "abc123"
}
```

## Field Definitions

| Field        | Description                             |
| ------------ | --------------------------------------- |
| message_id   | Unique WhatsApp message identifier      |
| user_id      | Sender phone number                     |
| timestamp    | UTC timestamp of message receipt        |
| message_type | text / button / voice                   |
| text         | User message content                    |
| language     | Active language if known                |
| session_id   | Current conversation session identifier |

---

# 2. Required HTTP Headers

All webhook requests must include required headers for secure and traceable communication.

## Required Headers

```
Content-Type: application/json
Authorization: Bearer <token>
X-Request-ID: unique-request-id
```

## Header Definitions

| Header        | Description                           |
| ------------- | ------------------------------------- |
| Content-Type  | Ensures JSON parsing                  |
| Authorization | Secures incoming webhook requests     |
| X-Request-ID  | Enables request tracing for debugging |

---

# 3. Bot Response JSON Format

The backend returns structured JSON after processing the user request.

## Success Response

```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "language": "EN"
}
```

## Field Definitions

| Field      | Description                  |
| ---------- | ---------------------------- |
| status     | success / error              |
| reply_text | Bot message returned to user |
| next_state | Backend state after response |
| language   | Current active language      |

---

# 4. Error Response Formats and Codes

The backend must return predictable error formats when processing fails.

## Unsupported Language

```json
{
  "status": "error",
  "error_code": "UNSUPPORTED_LANGUAGE",
  "message": "Selected language not supported"
}
```

**HTTP Status:**

```
400 Bad Request
```

---

## Invalid Input

```json
{
  "status": "error",
  "error_code": "INVALID_INPUT",
  "message": "Unable to understand request"
}
```

**HTTP Status:**

```
400 Bad Request
```

---

## Session Expired

```json
{
  "status": "error",
  "error_code": "SESSION_NOT_FOUND",
  "message": "Session expired"
}
```

**HTTP Status:**

```
404 Not Found
```

---

## Internal Processing Failure

```json
{
  "status": "error",
  "error_code": "INTERNAL_ERROR",
  "message": "Unexpected processing failure"
}
```

**HTTP Status:**

```
500 Internal Server Error
```

---

# 5. State Transition Mapping (4A UX Nodes → 4B Backend States)

The backend must align implementation states with Team 4A conversational UX nodes.

| UX Node            | Backend State     |
| ------------------ | ----------------- |
| Language Selection | LANG_SELECT       |
| Visitor Inquiry    | VISITOR_INQUIRY   |
| Temple Directions  | TEMPLE_DIRECTIONS |
| Donation Request   | DONATION_FLOW     |
| Error Recovery     | ERROR_STATE       |

---

# 6. Language State Mapping

Language is handled separately from conversational intent.

| UX Language State | Backend State |
| ----------------- | ------------- |
| English Active    | LANG_EN       |
| Hindi Active      | LANG_HI       |
| Gujarati Active   | LANG_GU       |

---

# 7. Language Switch Event Logging

Whenever a user changes language, the backend records the transition.

## Event Format

```json
{
  "event": "language_switch",
  "source": "EN",
  "target": "HI"
}
```

### Purpose

This supports:

* language usage reporting
* multilingual engagement tracking
* preference analytics for **JKYog board review**

---

# 8. Context Preservation Rules

Language changes must **not reset the active conversation**.

### Example

User asks temple timings in English
User switches to Hindi
Bot continues same intent in Hindi

### Backend Rule

```
intent_state remains unchanged
language_state updates independently
```

---

# 9. Request–Response Example

## Example Interaction

### Request

```json
{
  "message_id": "wamid.67890",
  "user_id": "+1234567890",
  "timestamp": "2026-03-10T18:35:00Z",
  "message_type": "text",
  "text": "Temple timings",
  "language": "EN",
  "session_id": "abc123"
}
```

### Response

```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "language": "EN"
}
```

---

# 10. Implementation Notes

Team 4B should treat:

* **language** as the **presentation layer**
* **state** as the **conversation logic layer**

This separation ensures **stable multilingual conversation flow**.

---

# 11. Summary

This API contract ensures:

* exact payload compatibility
* predictable response structure
* stable state transitions
* multilingual support alignment between **UX and backend**
