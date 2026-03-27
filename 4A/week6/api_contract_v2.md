
---

# API Contract v2.0: JKYog Multi-Channel Platform

**Lead Architect:** Harshith Bharathbhushan  
**Status:** Versioned 
**Effective Date:** March 25, 2026

---

## 1. Purpose
This document serves as the technical "Source of Truth" to facilitate cross-team alignment by:
* **Comparing v1.0 and v2.0 contracts:** Highlighting the shift from Meta-JSON to Twilio-Unified protocols.
* **Testing requests in Postman:** Providing standardized schemas for automated and manual verification.
* **Validating migration assumptions:** Ensuring the backend normalization logic matches UX design requirements.
* **Supporting end-to-end integration:** Defining the exact "handshake" for the Wednesday live demonstration.

---

## 2. Versioning Strategy & Governance
To ensure stability during rapid iteration, we utilize **URL-based Versioning**.

* **Endpoint Pattern:** `https://<domain>/v2/webhook/whatsapp`
* **Strategy:** URL versioning provides high visibility in Twilio’s dashboard and allows for "N-1" side-by-side testing of old and new logic.
* **Deprecation Policy:** v1.0 (Meta-style) will remain active for 30 days after the v2.0 launch to allow for transition testing.
* **Breaking Changes:** Any structural change to fields requires a 72-hour notice and an update to the Migration Guide.

---

## 3. Performance & Operational Constraints (SLAs)
To maintain the "AI Employee" standard for JKYog, the following service levels are enforced:

| Metric | Target (Average) | Max (p95) |
| :--- | :--- | :--- |
| **End-to-End Latency** | 1200ms | 2000ms |
| **KB Search Response** | 400ms | 800ms |
| **Uptime** | 99.5% | N/A |

### 3.1 Rate Limiting
* **Per-User Limit:** 20 requests per minute per unique `From` number.
* **Global Limit:** 100 requests per minute across the `/v2/` namespace.
* **Excessive Traffic:** Returns a `429 Too Many Requests` status code.

---

## 4. Webhook Request Schema (Inbound from Twilio)
**Content-Type:** `application/x-www-form-urlencoded`

| Parameter | Type | Mapping | Description |
| :--- | :--- | :--- | :--- |
| `MessageSid` | String | `message_id` | Unique ID used for message deduplication. |
| `From` | String | `user_id` | Normalized sender number (Stripped of `whatsapp:` prefix). |
| `Body` | String | `text` | The raw user query passed to the intent engine. |

---

## 5. Bot Response Schema (Success)
The response includes metadata to track the **Jaccard overlap scoring** used in Team 4B's `ingestion.py`.

```json
{
  "status": "success",
  "reply_text": "The temple opens at 9 AM.",
  "next_state": "VISITOR_INQUIRY",
  "metadata": {
    "kb_score": 0.88,
    "kb_source": "faqs.json",
    "version": "v2.0"
  }
}
```

---

## 6. Error States & Confidence Thresholds
| Error Code | Status | Logic |
| :--- | :--- | :--- |
| `KB_LOW_CONFIDENCE` | 200 | Jaccard score 0.3–0.5; triggers clarification prompt. |
| `KB_NO_MATCH` | 200 | Score < 0.3; transitions to `ERROR_STATE` (Fallback). |
| `AUTH_FAILED` | 401 | Missing `X-Twilio-Signature` or session validation failure. |

---
