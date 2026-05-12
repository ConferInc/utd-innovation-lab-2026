"""
Subset of Team 4B ORM models for users / conversations / messages only.

Kept separate from 4B's schema.py to avoid importing events/recurrence.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, types
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

from .models import Base


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


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(PortableJSON(), default=dict, nullable=False)
    last_active_at = Column(DateTime, default=_now, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        PortableUUID(),
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
    __tablename__ = "messages"

    id = Column(PortableUUID(), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        PortableUUID(),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
