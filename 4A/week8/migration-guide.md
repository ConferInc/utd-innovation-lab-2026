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


## Database Failure Recovery Process

### Scenario: Database is Down or Data is Lost

###  Recovery Objectives
- **RTO (Recovery Time Objective)**: ≤ 30 minutes (maximum acceptable downtime)
- **RPO (Recovery Point Objective)**: ≤ 5 minutes (maximum acceptable data loss)

###  Disaster Recovery Architecture (High-Level)
- Primary Database (Production)
- Automated Backups (Hourly/Daily Snapshots)
- Read Replica / Standby Database (Failover ready)
- Backup Storage (Cloud storage like S3)

---

### Step-by-Step Recovery Plan

1. **Detect the Issue**
   - Monitor alerts (DB connection failures, 500 errors)
   - Confirm database is unreachable or corrupted

2. **Switch to Safe Mode**
   - Temporarily disable write operations
   - Serve fallback/static responses if applicable

3. **Failover (if replica available)**
   - Switch to read replica / standby DB
   - Update `DATABASE_URL` to replica endpoint

4. **Check Database Connectivity**
   - Verify `DATABASE_URL`
   - Check network/firewall rules
   - Restart database service if needed

5. **Restore from Backup**
   - Identify latest valid backup (based on RPO ≤ 5 min)
   - Restore database
   ```bash
   pg_restore -d db_name backup_file.dump
   ```

6. **Run Migrations**
   - Apply latest schema changes
   ```bash
   alembic upgrade head
   ```

7. **Validate Data Integrity**
   - Check critical tables (User, Conversation)
   - Validate schema consistency

8. **Reconnect Application**
   - Restart backend services
   - Test API endpoints and webhook flow

9. **Monitor System Stability**
   - Track latency, error rates
   - Confirm Twilio messages are processed correctly

10. **Post-Incident Review**
   - Identify root cause
   - Improve backup/monitoring strategy

| Parameter             | v1     | v2         | Description                |
|-----------------------|--------|------------|----------------------------|
| API_VERSION           | v1     | v2         | Updated webhook version    |
| TWILIO_ACCOUNT_SID    | N/A    | Required   | Twilio account ID          |
| TWILIO_AUTH_TOKEN     | N/A    | Required   | Twilio auth token          |
| TWILIO_PHONE_NUMBER   | N/A    | Required   | WhatsApp sender number     |
| WEBHOOK_URL           | basic  | /v2/webhook/whatsapp | Updated endpoint |
