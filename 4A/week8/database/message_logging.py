"""User/conversation/message helpers aligned with Team 4B state_tracking."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

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
) -> Message:
    if direction not in {"inbound", "outbound"}:
        raise ValueError("direction must be either 'inbound' or 'outbound'")

    message = Message(
        conversation_id=conversation_id,
        direction=direction,
        text=text,
        intent=intent,
        created_at=_now(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
