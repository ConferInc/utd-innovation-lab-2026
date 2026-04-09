"""add requester linkage fields to escalations

Revision ID: 005
Revises: 004
Create Date: 2026-04-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "escalations",
        sa.Column("requester_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "escalations",
        sa.Column("requester_session_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_escalations_requester_user_id_users",
        "escalations",
        "users",
        ["requester_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_escalations_requester_session_id_session_state",
        "escalations",
        "session_state",
        ["requester_session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_escalations_requester_user_id",
        "escalations",
        ["requester_user_id"],
    )
    op.create_index(
        "ix_escalations_requester_session_id",
        "escalations",
        ["requester_session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_escalations_requester_session_id", table_name="escalations")
    op.drop_index("ix_escalations_requester_user_id", table_name="escalations")

    op.drop_constraint(
        "fk_escalations_requester_session_id_session_state",
        "escalations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_escalations_requester_user_id_users",
        "escalations",
        type_="foreignkey",
    )

    op.drop_column("escalations", "requester_session_id")
    op.drop_column("escalations", "requester_user_id")
