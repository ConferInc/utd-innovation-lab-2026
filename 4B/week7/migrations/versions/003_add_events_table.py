from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_source_site_enum = postgresql.ENUM(
    "radhakrishnatemple",
    "jkyog",
    name="event_source_site",
    create_type=False,
)


def upgrade() -> None:
    event_source_site_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("venue_details", sa.Text(), nullable=True),
        sa.Column("parking_notes", sa.Text(), nullable=True),
        sa.Column("food_info", sa.Text(), nullable=True),
        sa.Column(
            "sponsorship_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_site", event_source_site_enum, nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("recurrence_pattern", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("special_notes", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
        sa.UniqueConstraint("dedup_key", name=op.f("uq_events_dedup_key")),
        sa.UniqueConstraint("source_site", "source_url", name=op.f("uq_events_source_site_source_url")),
    )

    op.create_index(op.f("ix_events_start_datetime"), "events", ["start_datetime"])
    op.create_index(op.f("ix_events_name"), "events", ["name"])
    op.create_index(op.f("ix_events_category"), "events", ["category"])
    op.create_index(op.f("ix_events_is_recurring"), "events", ["is_recurring"])
    op.create_index(op.f("ix_events_dedup_key"), "events", ["dedup_key"])


def downgrade() -> None:
    op.drop_index(op.f("ix_events_dedup_key"), table_name="events")
    op.drop_index(op.f("ix_events_is_recurring"), table_name="events")
    op.drop_index(op.f("ix_events_category"), table_name="events")
    op.drop_index(op.f("ix_events_name"), table_name="events")
    op.drop_index(op.f("ix_events_start_datetime"), table_name="events")
    op.drop_table("events")
    event_source_site_enum.drop(op.get_bind(), checkfirst=True)
