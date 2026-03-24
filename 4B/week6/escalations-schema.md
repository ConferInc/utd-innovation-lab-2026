# Escalations Database Schema

Owner: Chakradhar Gummakonda
Branch: `feature/week6-chakradhar-escalations-db`

---

## Table: `escalations`

Records bot-to-human handoff / escalation requests.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | No | `uuid4()` | Primary key |
| `user_id` | UUID | No | — | FK → `users.id` (CASCADE) |
| `session_id` | UUID | Yes | `NULL` | FK → `session_state.id` (SET NULL) |
| `reason` | Text | No | — | Human-readable escalation reason |
| `context` | JSONB | No | `'{}'` | Flexible metadata (see Context Payload below) |
| `status` | String | No | `'pending'` | One of: `pending`, `in_progress`, `resolved` |
| `created_at` | DateTime | No | UTC now | When the escalation was created |
| `resolved_at` | DateTime | Yes | `NULL` | When the escalation was resolved |
| `resolved_by` | String | Yes | `NULL` | Who resolved it (volunteer name / agent ID) |

### Constraints

| Constraint | Type | Definition |
|------------|------|------------|
| `pk_escalations` | Primary Key | `id` |
| `fk_escalations_user_id_users` | Foreign Key | `user_id` → `users.id` ON DELETE CASCADE |
| `fk_escalations_session_id_session_state` | Foreign Key | `session_id` → `session_state.id` ON DELETE SET NULL |
| `ck_escalations_valid_escalation_status` | Check | `status IN ('pending', 'in_progress', 'resolved')` |

### Indexes

| Index | Column(s) |
|-------|-----------|
| `ix_escalations_user_id` | `user_id` |
| `ix_escalations_session_id` | `session_id` |
| `ix_escalations_status` | `status` |
| `ix_escalations_created_at` | `created_at` |

---

## Migration

File: `migrations/versions/002_add_escalations_table.py`
Revision: `002` (depends on `001`)

Creates the `escalations` table with all columns, constraints, and indexes listed above. The `downgrade()` function drops indexes first, then the table.

---

## SQLAlchemy Model

Defined in `database/schema.py` as `class Escalation(Base)`.

### Relationships

- `Escalation.user` → `User` (back_populates `escalations`)
- `Escalation.session` → `SessionState` (back_populates `escalations`)
- `User.escalations` → list of `Escalation` (cascade `all, delete-orphan`)
- `SessionState.escalations` → list of `Escalation`

---

## Database Helper Functions

Defined in `database/state_tracking.py`:

| Function | Purpose |
|----------|---------|
| `create_escalation(db, user_id, reason, context, session_id)` | Insert a new escalation. Validates user exists and session belongs to user. |
| `update_escalation_status(db, escalation_id, new_status, resolved_by, note)` | Transition status. Sets `resolved_at`/`resolved_by` on resolve; clears on un-resolve. Appends notes to `context.status_notes`. |
| `get_escalations_by_user(db, user_id, status)` | Query all escalations for a user, optional status filter. |
| `get_escalation_by_id(db, escalation_id)` | Fetch a single escalation by primary key. |

---

## Context Payload Convention

The `context` JSONB column stores flexible metadata aligned with Chanakya's escalation flow. Recommended keys:

```json
{
  "trigger_reason": "user_requested_human",
  "last_detected_intent": "donation_request",
  "conversation_summary": "User asked about donation and requested a volunteer.",
  "language": "en",
  "consent_status": true,
  "short_transcript": [
    {"speaker": "user", "text": "I want to talk to a person"},
    {"speaker": "bot", "text": "I can connect you to a volunteer."}
  ],
  "handoff": {
    "channel_from": "whatsapp",
    "channel_to": "human_support",
    "created_at": "2026-03-23T18:30:00Z"
  },
  "status_notes": [],
  "failure_notes": []
}
```

These fields are stored as JSON rather than separate columns because:
- They are flow metadata, not core lifecycle fields.
- Chanakya's handoff spec may evolve without requiring new migrations.
- PostgreSQL JSONB supports efficient querying if needed later.

---

## Health Check Integration

`database/models.py` includes `_execute_escalations_probe()` which runs `SELECT 1 FROM escalations LIMIT 1`. The `/health/db` endpoint reports:

- `"tables": {"escalations": "ok"}` when the table is reachable
- `"tables": {"escalations": "unreachable"}` with `"status": "degraded"` otherwise

---

## Stress Tests

| Script | What it tests |
|--------|---------------|
| `stress_test/stress_test_escalations.py` | Direct DB CRUD: serial creates, concurrent creates, status transitions, query by user |
| `stress_test/stress_test_db_health_v2.py` | HTTP `/health/db` with Phase 7 escalation-table probe |
