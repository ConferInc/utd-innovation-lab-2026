# Escalations API — Team 4B Week 8 (Chanakya contract)

HTTP endpoints for **bot-to-human escalation** tickets. Rows live in the `escalations` table ([`database/schema.py`](database/schema.py): `ticket_id`, `success`, `queue_status`, `assigned_volunteer`, `next_state`, `message_for_user`, `priority`, `errors`, optional `requester_user_id` / `requester_session_id`).

**Authentication:** Every route requires:

`Authorization: Bearer <ESCALATIONS_API_TOKEN>`

Without a valid token the API returns **401**. (Team 4A: events under `/api/v2/events` stay public; escalations do not.)

The response body for create/get/resolve matches the Pydantic model **`EscalationResponse`** in [`events/schemas/event_payload.py`](events/schemas/event_payload.py).

Interactive OpenAPI: **`/docs`** when the app is running.

---

## Base URL

- Deployed: `https://<your-service>.onrender.com`
- Local: `http://127.0.0.1:8000`

Export a token for curl examples:

```bash
export ESCALATIONS_API_TOKEN="your-secret-token"
```

---

## POST /escalations

Create a ticket. Returns **`201 Created`** with an **EscalationResponse** JSON object.

### Request body (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `priority` | string | No | `low` \| `medium` \| `high` \| `critical` (default `medium`) |
| `queue_status` | string | No | `queued` \| `assigned` \| `resolved` (default `queued`) |
| `assigned_volunteer` | string or null | No | Volunteer identifier when known |
| `next_state` | string or null | No | If omitted, derived from `queue_status` |
| `message_for_user` | string or null | No | User-facing message (default server string if empty) |
| `success` | boolean | No | Default `true` |
| `errors` | string[] | No | Initial error strings (default `[]`) |
| `requester_user_id` | UUID or null | No | Optional link to `users.id` |
| `requester_session_id` | UUID or null | No | Optional `session_state.id`; must exist; if `requester_user_id` is set it must match the session’s user; if only session is set, `requester_user_id` on the row is taken from the session |

### Success — `201 Created` (EscalationResponse)

```json
{
  "success": true,
  "ticket_id": "<uuid>",
  "queue_status": "queued",
  "assigned_volunteer": null,
  "next_state": "WAITING_FOR_VOLUNTEER",
  "message_for_user": "I'm connecting you to a human volunteer now. Please hold on.",
  "priority": "medium",
  "errors": []
}
```

### Session integration

If `requester_session_id` is valid, the API merges into that session’s `state`:

- `last_escalation_ticket_id`
- `last_escalation_queue_status`
- `last_escalation_at` (ISO 8601)

### Example (curl)

```bash
curl -s -X POST "http://127.0.0.1:8000/escalations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ESCALATIONS_API_TOKEN}" \
  -d '{
    "priority": "medium",
    "queue_status": "queued",
    "message_for_user": "Connecting you to a volunteer.",
    "errors": []
  }'
```

### Errors

| Status | When |
|--------|------|
| `401` | Missing/wrong Bearer token |
| `422` | Validation error (invalid enum, bad UUID, etc.) |
| `400` | Invalid `queue_status`/`priority`, or session/user mismatch |

---

## GET /escalations/{ticket_id}

Fetch one ticket by **`ticket_id`** (primary key UUID).

### Success — `200 OK`

Same **EscalationResponse** shape as POST.

### Example (curl)

```bash
TICKET="550e8400-e29b-41d4-a716-446655440000"
curl -s "http://127.0.0.1:8000/escalations/${TICKET}" \
  -H "Authorization: Bearer ${ESCALATIONS_API_TOKEN}"
```

### Errors

| Status | When |
|--------|------|
| `401` | Missing/wrong Bearer |
| `404` | Unknown `ticket_id` |

---

## PUT /escalations/{ticket_id}/resolve

Sets **`queue_status`** to **`resolved`** and updates `next_state` accordingly. **Idempotent:** if already `resolved`, returns the current row.

### Request body (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assigned_volunteer` | string or null | No | Set when resolving with an assignee |
| `error_note` | string or null | No | If non-empty, appended to the ticket’s `errors` list |

### Success — `200 OK`

**EscalationResponse** for the updated row.

### Example (curl)

```bash
TICKET="550e8400-e29b-41d4-a716-446655440000"
curl -s -X PUT "http://127.0.0.1:8000/escalations/${TICKET}/resolve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ESCALATIONS_API_TOKEN}" \
  -d '{"assigned_volunteer": "volunteer_jane@example.com", "error_note": ""}'
```

### Errors

| Status | When |
|--------|------|
| `401` | Missing/wrong Bearer |
| `404` | Unknown `ticket_id` |
| `400` | Invalid transition / validation from `state_tracking` |

---

## Related docs

- [docs/api-security.md](docs/api-security.md) — which routes need auth
- [docs/render-deployment.md](docs/render-deployment.md) — set `ESCALATIONS_API_TOKEN` on Render
- **GET `/health/db`** — database health

---

*Week 8 — aligned with Team 4A escalation flow fields; implemented in [`api/escalations.py`](api/escalations.py) and [`database/state_tracking.py`](database/state_tracking.py).*
