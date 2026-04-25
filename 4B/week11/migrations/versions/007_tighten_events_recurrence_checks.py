"""Tighten events recurrence CHECK constraints to weekly/day-based patterns only.

Revision ID: 007
Revises: 006
Create Date: 2026-04-09
"""

from typing import Sequence, Union

from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_events_recurrence_pattern", "events", type_="check")
    op.drop_constraint("ck_events_recurrence_text", "events", type_="check")

    op.create_check_constraint(
        "ck_events_recurrence_pattern",
        "events",
        "recurrence_pattern IS NULL OR recurrence_pattern IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday')",
    )
    op.create_check_constraint(
        "ck_events_recurrence_text",
        "events",
        "recurrence_text IS NULL OR recurrence_text IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_events_recurrence_pattern", "events", type_="check")
    op.drop_constraint("ck_events_recurrence_text", "events", type_="check")

    op.create_check_constraint(
        "ck_events_recurrence_pattern",
        "events",
        "recurrence_pattern IS NULL OR recurrence_pattern IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday', 'monthly', 'annually')",
    )
    op.create_check_constraint(
        "ck_events_recurrence_text",
        "events",
        "recurrence_text IS NULL OR recurrence_text IN "
        "('daily', 'weekdays', 'weekends', "
        "'weekly:monday', 'weekly:tuesday', 'weekly:wednesday', 'weekly:thursday', "
        "'weekly:friday', 'weekly:saturday', 'weekly:sunday', 'monthly', 'annually')",
    )
