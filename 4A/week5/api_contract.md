
---

# API Contract v2.0: JKYog WhatsApp Bot (Twilio & KB Integrated)

**Lead Architects:** Harshith Bharathbhushan, Nikita Pal   
**Branch:** `feature/week5-api-contract-v2`

---

## 1. Webhook Request Schema (Inbound from Twilio)

Team 4B uses the Twilio WhatsApp Gateway. Requests are received as `application/x-www-form-urlencoded`.

### Request Format
**Content-Type:** `application/x-www-form-urlencoded`

| Twilio Parameter | Data Type | Internal Mapping | Description |
| :--- | :--- | :--- | :--- |
| `MessageSid` | String | `message_id` | Unique identifier from Twilio |
| `From` | String | `user_id` | Sender number (Normalized to bare digits) |
| `Body` | String | `text` | Incoming user message (Intent trigger) |
| `ProfileName` | String | `user_name` | WhatsApp profile display name |

### Normalization Rule
Team 4B backend strips the `whatsapp:` prefix and the leading `+` sign.
* **Example:** `whatsapp:+19725550123` $\rightarrow$ `19725550123`

---

## 2. Unified Internal JSON Schema
After ingestion, the backend converts the Twilio payload into a standardized JSON object for state processing.

```json
{
  "message_id": "SM12345",
  "user_id": "19725550123",
  "user_name": "John Doe",
  "text": "Temple timings",
  "timestamp": "2026-03-18T18:30:00Z",
  "language": "EN",
  "session_token": "abc123-uuid",
  "channel": "whatsapp"
}
```

---

## 3. Required HTTP Headers

| Header | Value | Description |
| :--- | :--- | :--- |
| `Content-Type` | `application/x-www-form-urlencoded` | Required for Twilio payload parsing |
| `X-Session-Token` | `uuid-string` | Maintains active DB-backed session |
| `Authorization` | `Bearer <token>` | Endpoint protection |

---

## 4. Bot Response & Reply Mechanism
This architecture uses **Async REST**. The backend returns a 200 OK acknowledgment, then calls the Twilio REST API separately to deliver the message.

### Success Response (Internal JSON)
The response includes a `metadata` object to track Knowledge Base (KB) performance for analytics.

```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "session_token": "hashed_token_xyz",
  "metadata": {
    "kb_source": "faqs.json",
    "kb_score": 0.88,
    "kb_id": "faq_timings_01"
  }
}
```

---

## 5. State & Session Management
Team 4B maintains state persistence using a relational database (SQLAlchemy). Twilio is treated as a stateless transport layer.

### State Mapping
| UX Node (Team 4A) | Backend State (Team 4B) |
| :--- | :--- |
| Language Selection | `LANG_SELECT` |
| Visitor Inquiry | `VISITOR_INQUIRY` |
| Temple Directions | `TEMPLE_DIRECTIONS` |
| Donation Request | `DONATION_FLOW` |
| **Error Recovery** | **`ERROR_STATE`** |

---

## 6. Error Handling & KB Confidence Scores
Based on Jaccard overlap scoring, the backend must return specific status codes to trigger fallback logic.

| Code | Status | Scenario |
| :--- | :--- | :--- |
| **200** | `ignored` | Non-message event (e.g., delivery receipt) |
| **200** | `KB_LOW_CONFIDENCE` | Score 0.3–0.5; bot asks for clarification |
| **200** | `KB_NO_MATCH` | Score < 0.3; transitions to `ERROR_STATE` |
| **400** | `INVALID_INPUT` | Malformed Twilio payload |
| **401** | `AUTH_FAILED` | Session or phone validation failure |
| **500** | `INTERNAL_ERROR` | Backend, KB search, or DB failure |

---

## 7. Language & Context Preservation
* **Rule:** A language change (e.g., English to Hindi) must **not** reset the intent state or clear the `SessionState.state` object.
* **Example:** A user switching languages while entering a donation amount stays in the `DONATION_FLOW` state.

---

## 8. Request–Response Example (The Handshake)

### Inbound (Twilio Form-Data)
```http
POST /webhook/whatsapp
Content-Type: application/x-www-form-urlencoded

MessageSid=SM67890&From=whatsapp%3A%2B19725550123&Body=Temple+timings
```

### Outbound (JSON Acknowledgment)
```json
{
  "status": "success",
  "reply_text": "Temple opens at 9 AM and closes at 7 PM",
  "next_state": "VISITOR_INQUIRY",
  "session_token": "abc-123-session-xyz",
  "metadata": {
    "kb_source": "faqs.json",
    "kb_score": 0.95,
    "kb_id": "faq_01"
  }
}
```

---

## 9. Summary
This contract version ensures 100% compatibility with:
* **Twilio's** form-encoded webhook protocol.
* **Team 4B's** async REST and DB-backed session logic.
* **Team 4A's** Analytics Spec (via KB metadata tracking).
* **Multilingual continuity** (via presentation-layer language handling).

---
