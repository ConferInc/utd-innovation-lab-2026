⚠️ This document is superseded by 4A/week8/api_contract_v2.1.md. Field names and auth mechanisms below are historical.
# 📄 File: 4A/week6/migration-guide.md

This document provides the literal "Before and After" code and data structures.
# Migration Guide (Week 5 → Week 6)

**Objective**: Successfully migrate the backend ingestion layer from Meta-native JSON to the Twilio Unified Protocol.
1. **Payload Transformation**
The primary breaking change is the shift in Content-Type and key naming conventions.
---

## 🔄 Incoming Message Webhook

### 🔹 Before (Week 5)

```json
POST /api/message
Content-Type: application/json

{
  "user_id": "123",
  "message": "Temple timings"
}
```

---

### 🔹 After (Week 6 - Twilio WhatsApp Format)

```http
POST /v2/webhook/whatsapp
Content-Type: application/x-www-form-urlencoded

MessageSid=SM67890&From=whatsapp%3A%2B19725550123&Body=Temple+timings&ProfileName=Devotee
```

### ✅ Key Changes

* Payload changed from JSON → `x-www-form-urlencoded`
* Uses Twilio fields:

  * `MessageSid` → unique message ID
  * `From` → user WhatsApp number
  * `Body` → user message
  * `ProfileName` → sender name
* Endpoint updated to `/v2/webhook/whatsapp`

---

## 🔄 Bot Response Format

### 🔹 Before (Week 5)

```json
{
  "reply": "Temple is open from 6 AM to 8 PM"
}
```

---

### 🔹 After (Week 6 - Twilio TwiML)

```xml
<Response>
    <Message>Temple is open from 6 AM to 8 PM</Message>
</Response>
```

### ✅ Key Changes

* Response format changed to **TwiML (XML)**
* Required by Twilio for WhatsApp replies

---

## 🔄 Session Handling Update

### Before (Week 5)

```json
{
  "session_id": "abc123",
  "message": "Temple timings"
}
```

### After (Week 6)

```json
{
  "session_id": "whatsapp:+19725550123",
  "channel": "whatsapp",
  "message": "Temple timings"
}
```

### ✅ Key Changes

* Phone number used as session identifier
* Channel awareness added

---

## ⚙️ Environment Variable Changes

| Variable Name       | Week 5 | Week 6               | Description             |
| ------------------- | ------ | -------------------- | ----------------------- |
| API_VERSION         | v1     | v2                   | Updated webhook version |
| TWILIO_ACCOUNT_SID  | N/A    | Required             | Twilio account ID       |
| TWILIO_AUTH_TOKEN   | N/A    | Required             | Twilio auth token       |
| TWILIO_PHONE_NUMBER | N/A    | Required             | WhatsApp sender number  |
| WEBHOOK_URL         | basic  | /v2/webhook/whatsapp | Updated endpoint        |

---





