# Escalations Database Schema

Owner: Chakradhar Gummakonda
Branch: feature/week8-chakradhar-schema-alignment

---

## Table: escalations

Records bot-to-human handoff / escalation requests.

#| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| ticket_id | UUID | No | uuid4() | Primary key |
| success | Boolean | No | true | Operation success status |
| queue_status | String | No | 'queued' | One of: queued, assigned, resolved |
| assigned_volunteer | String | Yes | NULL | Who resolved it (volunteer name / agent ID) |
| next_state | String | No | 'WAITING_FOR_VOLUNTEER' | Bot orchestrator state directive |
| message_for_user | String | No | 'I'm connecting...'| Human-readable message to send |
| priority | String | No | 'medium' | One of: low, medium, high, critical |
| errors | JSONB | No | '[]' | List of errors |

### Constraints

| Constraint | Type | Definition |
|------------|------|------------|
| pk_escalations | Primary Key | ticket_id |
| fk_escalations_user_id_users | Foreign Key | user_id → users.id ON DELETE CASCADE |
| fk_escalations_session_id_session_state | Foreign Key | session_id → session_state.id ON DELETE SET NULL |
| ck_escalations_valid_escalation_status | Check | queue_status IN ('queued', 'assigned', 'resolved') |

### Indexes

| Index | Column(s) |
|-------|-----------|
| ix_escalations_user_id | user_id |
| ix_escalations_session_id | session_id |
| ix_escalations_status | queue_status |
| ix_escalations_created_at | created_at |

---

## API Response Format (Aligned with Team 4A)

The POST/GET escalation endpoints now return the response shape expected by
Chanakya's escalation flow (see 4A/week6/escalation-flow-update.md):


json
{
  "success": true,
  "ticket_id": "550e8400-e29b-41d4-a716-446655440001",
  "queue_status": "queued",
  "assigned_volunteer": null,
  "next_state": "WAITING_FOR_VOLUNTEER",
  "message_for_user": "I'm connecting you to a human volunteer now. Please hold on.",
  "priority": "high",
  "errors": []
}


### Status Mapping

| Internal Status | queue_status | next_state |
|---|---|---|
| Mapping not needed | queued | WAITING_FOR_VOLUNTEER |
| Mapping not needed | assigned | ACTIVE_HANDOFF |
| Mapping not needed | resolved | RESOLVED |

---

## Migration

File: migrations/versions/002_add_escalations_table.py (original table)
File: migrations/versions/004_expand_events_schema.py (adds priority column)

alembic upgrade head is required

---

## SQLAlchemy Model

Defined in database/schema.py as class Escalation(Base).

### No Relationships

As per exact schema alignment, this table operates independently with no foreign keys to Users or Sessions.

---

## Database Helper Functions

Defined in database/state_tracking.py:

| Function | Purpose |
|----------|---------|
| create_escalation(db, priority) | Insert a new escalation ticket purely matching the exact fields. |
| update_escalation_status(db, escalation_id, new_status, resolved_by, note) | Transition status. |
| get_escalations_by_status(db, status) | Query all escalations. |
| get_escalation_by_id(db, escalation_id) | Fetch a single escalation by primary key. |

---



## Health Check Integration

database/models.py includes _execute_escalations_probe() which runs SELECT 1 FROM escalations LIMIT 1. The /health/db endpoint reports:

- "tables": {"escalations": "ok"} when the table is reachable
- "tables": {"escalations": "unreachable"} with "status": "degraded" otherwise

---

## Stress Tests

| Script | What it tests |
|--------|---------------|
| stress_test/stress_test_escalations.py | Direct DB CRUD: serial creates, concurrent creates, status transitions, query by user |
| stress_test/stress_test_db_health_v2.py | HTTP /health/db with Phase 7 escalation-table probe |

---

*Schema updated for Week 8-9 sprint — Chakradhar Gummakonda*
