"""add escalations table

Revision ID: 002
Revises: 001
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "escalations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_escalations_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["session_state.id"],
            name=op.f("fk_escalations_session_id_session_state"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_escalations")),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name=op.f("ck_escalations_valid_escalation_status"),
        ),
    )
    op.create_index(op.f("ix_escalations_user_id"), "escalations", ["user_id"])
    op.create_index(op.f("ix_escalations_session_id"), "escalations", ["session_id"])
    op.create_index(op.f("ix_escalations_status"), "escalations", ["status"])
    op.create_index(op.f("ix_escalations_created_at"), "escalations", ["created_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_escalations_created_at"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_status"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_session_id"), table_name="escalations")
    op.drop_index(op.f("ix_escalations_user_id"), table_name="escalations")
    op.drop_table("escalations")