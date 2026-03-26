
# 📄 File: 4A/week6/operations-runbook.md

# Operations Runbook

##  Safe Deployment Steps

### 1. Safe Deployment Procedure

* **Staging Test**: Deploy v2.0 code to the staging branch and verify using the Week 6 Postman Collection.
* **Database Migration**: Run migrations to update the Conversation and User tables for v2.0 metadata support.
* **Twilio Switch**: Update the Twilio Sandbox/Webhook URL to point to the `/v2/webhook/whatsapp` endpoint.

### Additional Steps

1. Pull latest code from repository
2. Set environment variables
3. Deploy to staging
4. Validate Twilio webhook flow
5. Gradual production rollout

---

##  Rollback Procedure

### 2. Rollback Plan

If v2.0 results in a **>10% increase in 500 INTERNAL_ERROR codes**:

* **Revert URL**: Immediately point the Twilio Webhook URL back to the stable `/v1/` endpoint.
* **Database**: Revert the last Alembic migration if schema changes caused the issue.
* **Logs Audit**: Check `X-Session-Token` logs to identify session-related failures.

### Standard Rollback Steps

```bash
git checkout <last-stable-tag>
```

1. Redeploy previous version
2. Restart services
3. Validate message flow

---

##  Monitoring Checkpoints

###  Core Metrics to Monitor

* Webhook request success rate
* Twilio message delivery logs
* API latency
* Error rates (4xx / 5xx)

###  Intelligent Monitoring Rules

* **Knowledge Base Confidence**: If `kb_score` averages < 0.4 for 10 consecutive requests, alert the UX team to retrain `faqs.json`.

* **Latency SLA Breach**: Trigger alert if response times exceed **1200ms** (as defined in v2.0 contract).

* **Authentication Failures**: Monitor spikes in `401 AUTH_FAILED`, which may indicate issues with Twilio Signature verification.

* **Webhook Health**: Alert if webhook success rate drops below 95%.

* **Message Delivery Issues**: Monitor Twilio delivery status (failed/undelivered messages).

---

##  Communication Templates

### Planned Deployment

```
Subject: Scheduled Maintenance - JKYog WhatsApp Integration

Hi Team,

JKYog services will be down for scheduled maintenance on [DATE] at [TIME].

This update includes migration from Version v1 to v2 with Twilio WhatsApp integration.

Expected downtime: 5–10 minutes.

Regards,
JKYog Team
```

---

### Incident Message

```
Subject: JKYog Service Disruption Notice

Hi Team,

We are currently experiencing a temporary disruption in JKYog WhatsApp services following the recent upgrade.

Our team is actively working to resolve the issue.

We will share the next update shortly.

Thank you for your patience.

Regards,
JKYog Team
```

---

##  Troubleshooting Quick Reference

###  Troubleshooting Quick-Reference Card

| Error Code         | Potential Cause                              | Immediate Fix                                            |
| ------------------ | -------------------------------------------- | -------------------------------------------------------- |
| 401 Unauthorized   | Missing X-Session-Token or invalid Signature | Check Postman headers and verify TWILIO_AUTH_TOKEN       |
| 400 Bad Request    | Sending JSON to a Form-Encoded endpoint      | Verify Content-Type is application/x-www-form-urlencoded |
| 500 Internal Error | Database timeout or corrupted faqs.json      | Check DATABASE_URL and validate JSON files               |

---

###  Webhook not receiving messages

* Verify Twilio webhook URL
* Check server is publicly accessible
* Validate HTTPS endpoint

---

###  Message received but no reply

* Check TwiML format
* Verify response headers
* Check backend logs

---

###  Invalid Twilio request

* Check Content-Type (`application/x-www-form-urlencoded`)
* Validate parameters

---

###  Delay in WhatsApp messages

* Check Twilio console logs
* Check server response time

---

##  Notes

* Always test using real WhatsApp numbers
* Keep Twilio credentials secure
* Monitor Twilio dashboard during deployment

---

**End of Documents**
