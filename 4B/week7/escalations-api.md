# Escalations API — Team 4B Week 6

HTTP endpoints for **bot-to-human escalation** tickets. The service stores rows in the `escalations` table (see Alembic migration `002_add_escalations_table.py` and `database/schema.py`).

Interactive OpenAPI documentation is available at **`/docs`** when the FastAPI app is running.

---

## Base URL

Use your deployed host, for example:

`https://<your-service>.onrender.com`

Local:

`http://127.0.0.1:8000`

All paths below are relative to that base.

---

## POST /escalations

Create a new escalation ticket.

### Request body (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string (UUID) | Yes | Existing user id in `users` table |
| `reason` | string | Yes | Non-empty after trim |
| `context` | object | No | Defaults to `{}`; arbitrary JSON for bot/agent context |
| `session_id` | string (UUID) or null | No | If set, must be a `session_state.id` that belongs to `user_id` |

### Success — `201 Created`

```json
{
  "id": "<uuid>",
  "status": "pending",
  "user_id": "<uuid>",
  "session_id": "<uuid or null>",
  "created_at": "2026-03-23T12:00:00Z"
}
```

### Errors

| Status | When |
|--------|------|
| `422` | Invalid JSON, missing required fields, empty `reason`, invalid UUID |
| `400` | Unknown `user_id`, or `session_id` missing / not owned by `user_id` (message in `detail`) |

### Session integration

If `session_id` is provided and valid, the API updates that session’s JSON `state` with:

- `last_escalation_id`
- `last_escalation_status`
- `last_escalation_at` (ISO 8601 timestamp)

### Example (curl)

```bash
curl -s -X POST "http://127.0.0.1:8000/escalations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "User requested volunteer",
    "context": {"intent": "human_help", "confidence": 0.4},
    "session_id": null
  }'
```

---

## GET /escalations/{id}

Fetch one escalation by primary key.

### Path parameter

- `id` — UUID of the escalation

### Success — `200 OK`

```json
{
  "id": "<uuid>",
  "user_id": "<uuid>",
  "session_id": "<uuid or null>",
  "reason": "…",
  "context": {},
  "status": "pending | in_progress | resolved",
  "created_at": "2026-03-23T12:00:00Z",
  "resolved_at": "<iso or null>",
  "resolved_by": "<string or null>"
}
```

Date-time fields use ISO 8601 with a `Z` suffix (stored as UTC in the database).

### Errors

| Status | When |
|--------|------|
| `422` | `id` is not a valid UUID |
| `404` | No row with that id |

### Example (curl)

```bash
curl -s "http://127.0.0.1:8000/escalations/550e8400-e29b-41d4-a716-446655440001"
```

---

## PUT /escalations/{id}/resolve

Mark an escalation as **resolved** and record who resolved it. Optional **notes** are appended to `context.status_notes` (see `update_escalation_status` in `database/state_tracking.py`).

### Path parameter

- `id` — UUID of the escalation

### Request body (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resolved_by` | string | Yes | Non-empty after trim (e.g. volunteer id or email) |
| `notes` | string or null | No | If non-empty after trim, stored in context |

### Success — `200 OK`

Same shape as **GET** response for the updated row.

**Idempotent:** If the escalation is already `resolved`, the handler returns the current row without changing timestamps again.

### Errors

| Status | When |
|--------|------|
| `422` | Invalid UUID, missing/empty `resolved_by` |
| `404` | Escalation not found |
| `400` | Rare: invalid internal status transition (`detail` from server) |

### Example (curl)

```bash
curl -s -X PUT "http://127.0.0.1:8000/escalations/550e8400-e29b-41d4-a716-446655440001/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "resolved_by": "volunteer_jane@example.com",
    "notes": "Called user; issue closed."
  }'
```

---

## Rules and notes

1. **`session_id` and `user_id`:** When `session_id` is sent on create, it must reference an existing session row whose `user_id` matches the request’s `user_id`. Otherwise the API returns **400**.
2. **OpenAPI:** Use **`/docs`** to try requests and see exact schemas.
3. **Related:** Database health including escalations table probe: **GET `/health/db`**.

---

*API implemented for Week 6 — Rohan Kothapalli (escalation endpoints); Chakradhar Gummakonda (schema / DB layer).*
