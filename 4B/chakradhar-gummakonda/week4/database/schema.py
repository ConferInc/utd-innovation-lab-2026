import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .models import Base


def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Represents a WhatsApp user known to the bot."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSONB, default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "SessionState",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    """Represents a chat session history for a user."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="active", index=True, nullable=False)
    started_at = Column(DateTime, default=_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """Represents a single inbound or outbound bot message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class SessionState(Base):
    """Stores temporary conversational context for an active user session.

    Security note:
        The ``session_token`` column stores a hashed token value rather than the
        raw session token. The raw token should only be exposed by backend code
        immediately after session creation.
    """

    __tablename__ = "session_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Stores a SHA-256 hash of the session token, not the raw token itself.
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    state = Column(JSONB, default=dict, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    user = relationship("User", back_populates="sessions")