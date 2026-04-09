"""
Alembic migration 004 - Expand events table for canonical schema alignment.

Adds new columns required by the canonical event schema,
renames fields for consistency for escalations.

Revision: 004
Down revision: 003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Events table: Add new columns ---
    op.add_column("events", sa.Column("subtitle", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("event_type", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("recurrence_text", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("timezone", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("address", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("city", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("state", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("postal_code", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("country", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("registration_required", sa.Boolean(), nullable=True))
    op.add_column("events", sa.Column("registration_status", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("registration_url", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("contact_email", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("contact_phone", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("transportation_notes", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("source_page_type", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("source_confidence", sa.Text(), nullable=True))
    op.add_column(
        "events",
        sa.Column(
            "price",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    # --- Events table: Rename columns ---
    # location -> location_name
    op.alter_column("events", "location", new_column_name="location_name")
    # special_notes -> notes
    op.alter_column("events", "special_notes", new_column_name="notes")
    # sponsorship_data -> sponsorship_tiers
    op.alter_column("events", "sponsorship_data", new_column_name="sponsorship_tiers")

    # --- Events table: Drop venue_details (absorbed into structured address fields) ---
    op.drop_column("events", "venue_details")

    op.create_check_constraint(
        "ck_events_recurrence_pattern",
        "events",
        "recurrence_pattern IS NULL OR recurrence_pattern IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday', 'monthly', 'annually')",
    )

    # --- Escalations table: Drop old columns not in the exact schema ---
    op.drop_constraint("fk_escalations_user_id_users", "escalations", type_="foreignkey")
    op.drop_constraint("fk_escalations_session_id_session_state", "escalations", type_="foreignkey")
    op.drop_column("escalations", "user_id")
    op.drop_column("escalations", "session_id")
    op.drop_column("escalations", "reason")
    op.drop_column("escalations", "context")
    op.drop_column("escalations", "created_at")
    op.drop_column("escalations", "resolved_at")

    # --- Escalations table: Rename matched columns ---
    op.alter_column("escalations", "id", new_column_name="ticket_id")
    op.alter_column("escalations", "status", new_column_name="queue_status")
    op.alter_column("escalations", "resolved_by", new_column_name="assigned_volunteer")

    # --- Escalations table: Add exact schema columns ---
    op.add_column("escalations", sa.Column("success", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("escalations", sa.Column("next_state", sa.String(), nullable=False, server_default="WAITING_FOR_VOLUNTEER"))
    op.add_column("escalations", sa.Column("message_for_user", sa.String(), nullable=False, server_default="I'm connecting you to a human volunteer now. Please hold on."))
    op.add_column("escalations", sa.Column("priority", sa.String(), nullable=False, server_default="medium"))
    op.add_column(
        "escalations",
        sa.Column(
            "errors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.create_check_constraint(
        "ck_escalations_queue_status",
        "escalations",
        "queue_status IN ('queued', 'assigned', 'resolved')",
    )
    op.create_check_constraint(
        "ck_escalations_priority",
        "escalations",
        "priority IN ('low', 'medium', 'high', 'critical')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_escalations_priority", "escalations", type_="check")
    op.drop_constraint("ck_escalations_queue_status", "escalations", type_="check")

    # --- Escalations: Drop exact schema columns ---
    op.drop_column("escalations", "errors")
    op.drop_column("escalations", "priority")
    op.drop_column("escalations", "message_for_user")
    op.drop_column("escalations", "next_state")
    op.drop_column("escalations", "success")

    # --- Escalations: Reverse renames ---
    op.alter_column("escalations", "assigned_volunteer", new_column_name="resolved_by")
    op.alter_column("escalations", "queue_status", new_column_name="status")
    op.alter_column("escalations", "ticket_id", new_column_name="id")

    # --- Escalations: Restore old columns ---
    op.add_column("escalations", sa.Column("resolved_at", sa.DateTime(), nullable=True))
    op.add_column("escalations", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("escalations", sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("escalations", sa.Column("reason", sa.Text(), nullable=True))
    op.add_column("escalations", sa.Column("session_id", sa.String(36), nullable=True))
    op.add_column("escalations", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_foreign_key("fk_escalations_session_id_session_state", "escalations", "session_state", ["session_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_escalations_user_id_users", "escalations", "users", ["user_id"], ["id"], ondelete="CASCADE")

    # --- Events: Restore venue_details ---
    op.add_column("events", sa.Column("venue_details", sa.Text(), nullable=True))
    op.drop_constraint("ck_events_recurrence_pattern", "events", type_="check")

    # --- Events: Reverse renames ---
    op.alter_column("events", "sponsorship_tiers", new_column_name="sponsorship_data")
    op.alter_column("events", "notes", new_column_name="special_notes")
    op.alter_column("events", "location_name", new_column_name="location")

    # --- Events: Drop new columns ---
    op.drop_column("events", "price")
    op.drop_column("events", "source_confidence")
    op.drop_column("events", "source_page_type")
    op.drop_column("events", "transportation_notes")
    op.drop_column("events", "contact_phone")
    op.drop_column("events", "contact_email")
    op.drop_column("events", "registration_url")
    op.drop_column("events", "registration_status")
    op.drop_column("events", "registration_required")
    op.drop_column("events", "country")
    op.drop_column("events", "postal_code")
    op.drop_column("events", "state")
    op.drop_column("events", "city")
    op.drop_column("events", "address")
    op.drop_column("events", "timezone")
    op.drop_column("events", "recurrence_text")
    op.drop_column("events", "event_type")
    op.drop_column("events", "subtitle")
