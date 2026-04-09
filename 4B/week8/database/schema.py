"""
SQLAlchemy ORM models for the JKYog WhatsApp Bot.

Supports both PostgreSQL (production) and SQLite (local dev) via portable
column types that automatically switch between JSONB/UUID and JSON/String.
"""
from __future__ import annotations

import enum
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    types,
)
from sqlalchemy.orm import relationship, validates

from .models import Base, IS_SQLITE

try:
    from events.schemas.recurrence import (
        recurrence_check_clause_for_column,
        validate_recurrence_value,
    )
except ImportError:
    from ..events.schemas.recurrence import (
        recurrence_check_clause_for_column,
        validate_recurrence_value,
    )

# ---------------------------------------------------------------------------
# Portable column types — work on both PostgreSQL and SQLite
# ---------------------------------------------------------------------------

if not IS_SQLITE:
    from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


class PortableJSON(types.TypeDecorator):
    """JSONB on PostgreSQL, TEXT with JSON serialization on SQLite."""
    impl = types.Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(types.Text())

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            if isinstance(value, str):
                return json.loads(value)
        return value


class PortableUUID(types.TypeDecorator):
    """UUID on PostgreSQL, String(36) on SQLite."""
    impl = types.String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(types.String(36))

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == "postgresql":
                return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))
        return value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    """Return current UTC time as naive datetime for DB timestamp columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------

class User(Base):
    """WhatsApp user profile and preferences."""
    __tablename__ = "users"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(PortableJSON(), default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation session metadata for a user."""
    __tablename__ = "conversations"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Inbound or outbound message in a conversation."""
    __tablename__ = "messages"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PortableUUID(), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class SessionState(Base):
    """Ephemeral session state tracked across bot interactions."""
    __tablename__ = "session_state"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(PortableJSON(), default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")


class Escalation(Base):
    """Human handoff request and resolution tracking."""
    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint("queue_status IN ('queued', 'assigned', 'resolved')", name="ck_escalations_queue_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name="ck_escalations_priority"),
    )

    ticket_id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    success = Column(Boolean, nullable=False, default=True)
    queue_status = Column(String, nullable=False, default="queued", index=True)
    assigned_volunteer = Column(String, nullable=True)
    next_state = Column(String, nullable=False, default="WAITING_FOR_VOLUNTEER")
    message_for_user = Column(String, nullable=False, default="I'm connecting you to a human volunteer now. Please hold on.")
    priority = Column(String, nullable=False, default="medium")
    errors = Column(PortableJSON(), default=list, nullable=False)
    requester_user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    requester_session_id = Column(PortableUUID(), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Event models
# ---------------------------------------------------------------------------

class EventSourceSite(str, enum.Enum):
    """Supported upstream sites used for event scraping."""
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"


class Event(Base):
    """Normalized event record scraped from temple-related sources.

    Schema aligned with Team 4A (Chanakya) canonical event JSON —
    see docs/schema-decisions.md for the cross-team field agreement.
    """
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
        CheckConstraint(
            recurrence_check_clause_for_column("recurrence_pattern"),
            name="ck_events_recurrence_pattern",
        ),
        CheckConstraint(
            recurrence_check_clause_for_column("recurrence_text"),
            name="ck_events_recurrence_text",
        ),
    )

    # --- Identity ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    subtitle = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # --- Categorization ---
    category = Column(Text, nullable=True, index=True)
    event_type = Column(Text, nullable=True)          # in_person | online | hybrid | unknown

    # --- Recurrence ---
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)   # machine-readable (duplicate of recurrence_text for legacy/DB)
    recurrence_text = Column(Text, nullable=True)       # machine-readable: daily, weekdays, weekly:sunday, etc.

    # --- Date / Time ---
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    timezone = Column(Text, nullable=True)              # CST, CDT, etc.

    # --- Location (structured) ---
    location_name = Column(Text, nullable=True)         # venue / temple name
    address = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    state = Column(Text, nullable=True)
    postal_code = Column(Text, nullable=True)
    country = Column(Text, nullable=True)

    # --- Registration ---
    registration_required = Column(Boolean, nullable=True)
    registration_status = Column(Text, nullable=True)   # open | closed | unknown
    registration_url = Column(Text, nullable=True)

    # --- Contact ---
    contact_email = Column(Text, nullable=True)
    contact_phone = Column(Text, nullable=True)

    # --- Logistics ---
    parking_notes = Column(Text, nullable=True)
    transportation_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)

    # --- Pricing & Sponsorship (JSONB) ---
    price = Column(PortableJSON(), default=dict, nullable=False)             # {amount, notes}
    sponsorship_tiers = Column(PortableJSON(), default=list, nullable=False) # [{tier_name, price, description}]

    # --- Source metadata ---
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    source_page_type = Column(Text, nullable=True)    # event_detail | upcoming_events | sponsorship_page | logistics_page
    image_url = Column(Text, nullable=True)

    # --- Scraping metadata ---
    scraped_at = Column(DateTime, default=_now, nullable=False)
    source_confidence = Column(Text, nullable=True)   # high | medium | low

    # --- Notes ---
    notes = Column(Text, nullable=True)

    # --- Timestamps ---
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    # --- Deduplication ---
    dedup_key = Column(String(64), nullable=False, index=True)

    @validates("recurrence_pattern", "recurrence_text")
    def _validate_recurrence_columns(self, key: str, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return validate_recurrence_value(value)
        return validate_recurrence_value(str(value))
