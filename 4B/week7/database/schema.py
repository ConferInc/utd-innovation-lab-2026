from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base


def _now() -> datetime:
    """Return current UTC time as naive datetime for DB timestamp columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """WhatsApp user profile and preferences."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionState", back_populates="user", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation session metadata for a user."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Inbound or outbound message in a conversation."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class SessionState(Base):
    """Ephemeral session state tracked across bot interactions."""
    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")
    escalations = relationship("Escalation", back_populates="session")


class Escalation(Base):
    """Human handoff request and resolution tracking."""
    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'resolved')",
            name="valid_escalation_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session_state.id", ondelete="SET NULL"), nullable=True, index=True)
    reason = Column(Text, nullable=False)
    context = Column(JSONB, default=dict, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)

    user = relationship("User", back_populates="escalations")
    session = relationship("SessionState", back_populates="escalations")


class EventSourceSite(str, enum.Enum):
    """Supported upstream sites used for event scraping."""
    RADHAKRISHNATEMPLE = "radhakrishnatemple"
    JKYOG = "jkyog"


class Event(Base):
    """Normalized event record scraped from temple-related sources."""
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_events_dedup_key"),
        UniqueConstraint("source_site", "source_url", name="uq_events_source_site_source_url"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)
    venue_details = Column(Text, nullable=True)
    parking_notes = Column(Text, nullable=True)
    food_info = Column(Text, nullable=True)
    sponsorship_data = Column(JSONB, default=list, nullable=False)
    image_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False)
    source_site = Column(
        SAEnum(
            EventSourceSite,
            name="event_source_site",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_pattern = Column(Text, nullable=True)
    category = Column(Text, nullable=True, index=True)
    special_notes = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)
    dedup_key = Column(String(64), nullable=False, index=True)
