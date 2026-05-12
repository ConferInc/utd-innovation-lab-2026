"""User/conversation/message helpers aligned with Team 4B state_tracking."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .schema_chat import Conversation, Message, User


def normalize_twilio_phone(from_field: str) -> str:
    """Match 4B authenticate_phone_user: strip whatsapp: prefix, then strip leading +."""
    s = (from_field or "").replace("whatsapp:", "").strip()
    return s.replace("+", "")


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_or_create_user(db: Session, phone_number: str, name: Optional[str] = None) -> User:
    """Fetch or create user by phone; retry once on unique-constraint races."""
    user = db.query(User).filter(User.phone_number == phone_number).first()
    now_utc = _now()

    if not user:
        user = User(
            phone_number=phone_number,
            name=name,
            created_at=now_utc,
            last_active_at=now_utc,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.phone_number == phone_number).first()
            if user is None:
                raise
            user.last_active_at = now_utc
            if name:
                user.name = name
            db.commit()
            db.refresh(user)
            return user

    user.last_active_at = now_utc
    if name:
        user.name = name
    db.commit()
    db.refresh(user)
    return user


def get_or_create_active_conversation(db: Session, user_id: uuid.UUID) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id,
            Conversation.status == "active",
        )
        .order_by(Conversation.started_at.desc())
        .first()
    )

    if not conversation:
        conversation = Conversation(
            user_id=user_id,
            status="active",
            started_at=_now(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation


def log_message(
    db: Session,
    conversation_id: uuid.UUID,
    direction: str,
    text: str,
    intent: Optional[str] = None,
    *,
    twilio_message_sid: Optional[str] = None,
    status: Optional[str] = None,
    failure_reason: Optional[str] = None,
    correlation_id: Optional[str] = None,
    metadata_json: Optional[Mapping[str, Any]] = None,
    total_latency_ms: Optional[int] = None,
) -> Message:
    if direction not in {"inbound", "outbound"}:
        raise ValueError("direction must be either 'inbound' or 'outbound'")

    message = Message(
        conversation_id=conversation_id,
        direction=direction,
        text=text,
        intent=intent,
        twilio_message_sid=twilio_message_sid,
        status=status,
        failure_reason=failure_reason,
        correlation_id=correlation_id,
        metadata_json=dict(metadata_json or {}),
        total_latency_ms=total_latency_ms,
        created_at=_now(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_message(
    db: Session,
    message: Message,
    *,
    intent: Optional[str] = None,
    twilio_message_sid: Optional[str] = None,
    status: Optional[str] = None,
    failure_reason: Optional[str] = None,
    correlation_id: Optional[str] = None,
    metadata_json: Optional[Mapping[str, Any]] = None,
    total_latency_ms: Optional[int] = None,
) -> Message:
    if intent is not None:
        message.intent = intent
    if twilio_message_sid is not None:
        message.twilio_message_sid = twilio_message_sid
    if status is not None:
        message.status = status
    if failure_reason is not None:
        message.failure_reason = failure_reason
    if correlation_id is not None:
        message.correlation_id = correlation_id
    if metadata_json:
        existing = dict(message.metadata_json or {})
        existing.update(dict(metadata_json))
        message.metadata_json = existing
    if total_latency_ms is not None:
        message.total_latency_ms = total_latency_ms
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
