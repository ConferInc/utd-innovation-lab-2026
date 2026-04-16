# 📄 4A/week6/migration-guide.md

# Migration Guide (Week 5 → Week 8)

## 📌 Objective

Successfully migrate the backend ingestion layer from **Meta-native JSON** to the **Twilio WhatsApp Unified Protocol**, while ensuring reliability, monitoring, and recovery mechanisms are in place.

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

### 🔹 After (Week 8 - Twilio WhatsApp Format)

```http
POST /v2/webhook/whatsapp
Content-Type: application/x-www-form-urlencoded

MessageSid=SM67890&From=whatsapp%3A%2B19725550123&Body=Temple+timings&ProfileName=Devotee
```

### ✅ Key Changes

* Payload changed from **JSON → form-urlencoded**
* Introduced Twilio standard fields:

  * `MessageSid` → unique message ID
  * `From` → WhatsApp user number
  * `Body` → message content
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

### 🔹 After (Week 8 - Twilio TwiML)

```xml
<Response>
    <Message>Temple is open from 6 AM to 8 PM</Message>
</Response>
```

### ✅ Key Changes

* Response format changed to **TwiML (XML)**
* Required for Twilio WhatsApp replies

---

## 🔄 Session Handling Update

### 🔹 Before (Week 5)

```json
{
  "session_id": "abc123",
  "message": "Temple timings"
}
```

### 🔹 After (Week 8)

```json
{
  "session_id": "whatsapp:+19725550123",
  "channel": "whatsapp",
  "message": "Temple timings"
}
```

### ✅ Key Changes

* Phone number used as session identifier
* Added channel awareness (`whatsapp`)

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

# 🗄️ Database Failure Recovery Process

## 🚨 Scenario

Database is down or data is lost.

## 📊 Recovery Objectives

* **RTO (Recovery Time Objective):** ≤ 30 minutes
* **RPO (Recovery Point Objective):** ≤ 5 minutes

## 🏗️ Disaster Recovery Architecture

* Primary database (production)
* Automated backups (hourly/daily snapshots)
* Read replica / standby database
* Cloud backup storage (e.g., S3)

---

## 🔁 Step-by-Step Recovery Plan

1. **Detect the Issue**

   * Monitor alerts (DB failures, 500 errors)

2. **Switch to Safe Mode**

   * Disable write operations
   * Serve fallback responses

3. **Failover**

   * Switch to replica database
   * Update `DATABASE_URL`

4. **Check Connectivity**

   * Verify database connection
   * Restart DB if required

5. **Restore from Backup**

```bash
pg_restore -d db_name backup_file.dump
```

6. **Run Migrations**

```bash
alembic upgrade head
```

7. **Validate Data**

   * Check User and Conversation tables

8. **Reconnect Application**

   * Restart backend services
   * Test APIs and webhook flow

9. **Monitor Stability**

   * Track latency and error rates

10. **Post-Incident Review**

* Identify root cause
* Improve monitoring and backup strategy

---

# 🤖 Bot Layer Reliability & Recovery Process

In case the backend API or database is unavailable, the bot maintains availability using **graceful degradation**.

**RTO:** ≤ 30 minutes
**RPO:** ≤ 5 minutes

---

## 🔌 Circuit Breaking

* `api_client.py` uses a **30-second timeout**
* Raises `APIConnectionError` if backend fails

---

## 🛡️ Internal Safe Mode

* `main.py` catches all API errors
* Prevents crashes
* Triggers fallback response builder

---

## 📚 Local Knowledge Activation

For recurring schedule queries:

* Bypass API calls
* Use `recurring_handler.py`
* Ensures temple timings remain available

---

## ⚠️ Static Fallback

If search fails:

```
"I’m having trouble reaching the temple records right now, but you can usually find our daily schedule at [URL]."
```

---

## ❤️ Health Monitoring

* `/health` endpoint exposed
* Enables uptime tracking independent of backend

---

## ✅ Summary

This migration:

* Transitions system to **Twilio WhatsApp protocol**
* Improves **scalability and real-world integration**
* Adds **resilience via database recovery and bot fallback mechanisms**
* Ensures system remains functional even during failures

---
