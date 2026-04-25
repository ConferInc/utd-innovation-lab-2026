"""Add CHECK constraint on events.recurrence_text (parity with recurrence_pattern).

Revision ID: 006
Revises: 005
Create Date: 2026-04-09
"""

from typing import Sequence, Union

from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_events_recurrence_text",
        "events",
        "recurrence_text IS NULL OR recurrence_text IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday', 'monthly', 'annually')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_events_recurrence_text", "events", type_="check")
