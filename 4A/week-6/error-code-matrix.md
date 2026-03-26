# 4A/week6/error-code-matrix.md

# 2) Error-Code Matrix

## 2.1 Scenario Mapping Table

| Error Scenario | HTTP Status | Retry? | User-Facing Message | Internal Log Level | Notes |
|---|---:|---|---|---|---|
| Missing required field | 400 | No | “I’m having trouble transferring your request right now. Please try again in a moment.” | ERROR | Log validation details, never raw secrets |
| Malformed JSON / invalid timestamp | 400 | No | “Something went wrong while processing your request.” | ERROR | Caller bug or payload construction issue |
| Missing/invalid bearer token | 401 | No | “I’m unable to connect you to a human right now.” | CRITICAL | Needs configuration or secret fix |
| Authenticated but unauthorized caller | 403 | No | “This request could not be completed right now.” | CRITICAL | Security-sensitive |
| Duplicate escalation already open | 409 | No automatic create retry | “You’re already being connected to a human volunteer.” | WARN | Reconcile by fetching existing ticket |
| Invalid business rule / unsupported channel | 422 | No | “I couldn’t complete the transfer because the request format was not accepted.” | ERROR | Validation beyond syntax |
| Rate limit exceeded | 429 | Yes | “There’s a short delay connecting you to a human. Please hold on.” | WARN | Respect `Retry-After` if present |
| Unexpected internal exception | 500 | Yes | “The handoff service is temporarily having trouble. I’ll try again.” | ERROR | Retry with backoff |
| Downstream malformed response | 502 | Yes | “I’m having trouble reaching the support system. Retrying now.” | ERROR | Treat as transient |
| Service temporarily unavailable | 503 | Yes | “The support system is temporarily unavailable. I’ll try again shortly.” | ERROR | Retry with backoff |
| Downstream timeout | 504 | Yes | “The connection is taking longer than expected. I’m retrying now.” | WARN | Retry with backoff |
| Ticket not found during poll/update | 404 | Usually no | “I couldn’t find your support request right now.” | ERROR | Reconcile state before retry |
| Volunteer queue full / no volunteer capacity | 503 | Conditional | “All volunteers are currently busy. Please wait while I continue trying.” | WARN | Can retry or keep waiting queue state |
| Notification service failure after ticket creation | 502 or 503 | Partial retry | “Your request has been created, but updates may be delayed.” | WARN | Do not recreate ticket |

---

## 2.2 Logging Guidance

### `WARN`
Use when:
- transient operational issue expected to recover
- rate limit or timeout occurs
- duplicate escalation is safely detected
- no volunteer currently available but system is still functioning

### `ERROR`
Use when:
- request fails due to validation or downstream dependency issue
- retry is needed because an infrastructure issue occurred
- ticket lifecycle becomes inconsistent but not security-critical

### `CRITICAL`
Use when:
- authentication/authorization misconfiguration exists
- security or environment boundary is violated
- escalation service cannot be trusted to operate safely until intervention

---
