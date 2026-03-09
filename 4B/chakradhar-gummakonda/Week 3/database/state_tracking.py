# database/state_tracking.py

import copy
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from database.schema import Conversation, Message, SessionState, User


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Recursively merge dict2 into dict1 without mutating the originals."""
    result = copy.deepcopy(dict1)

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


# --- USER HELPERS ---
def get_or_create_user(db: Session, phone_number: str, name: Optional[str] = None) -> User:
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
    else:
        user.last_active_at = now_utc
        if name:
            user.name = name

    db.commit()
    db.refresh(user)
    return user


# --- CONVERSATION HELPERS ---
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


# --- SESSION HELPERS ---
def create_session(db: Session, user_id: uuid.UUID, ttl_minutes: int = 1440) -> SessionState:
    now_utc = _now()

    (
        db.query(SessionState)
        .filter(
            SessionState.user_id == user_id,
            SessionState.is_active.is_(True),
        )
        .update(
            {
                "is_active": False,
                "updated_at": now_utc,
            },
            synchronize_session=False,
        )
    )

    new_session = SessionState(
        user_id=user_id,
        session_token=str(uuid.uuid4()),
        expires_at=now_utc + timedelta(minutes=ttl_minutes),
        is_active=True,
        state={},
        updated_at=now_utc,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def get_session_by_token(db: Session, session_token: str) -> Optional[SessionState]:
    """Lookup active, non-expired session by token."""
    now_utc = _now()

    return (
        db.query(SessionState)
        .filter(
            SessionState.session_token == session_token,
            SessionState.is_active.is_(True),
            SessionState.expires_at > now_utc,
        )
        .first()
    )


def merge_session_state(
    db: Session,
    session_id: uuid.UUID,
    updates: Dict[str, Any],
) -> Optional[SessionState]:
    session_obj = db.query(SessionState).filter(SessionState.id == session_id).first()

    if not session_obj:
        return None

    current_state = session_obj.state or {}
    session_obj.state = deep_merge_dicts(current_state, updates)
    session_obj.updated_at = _now()

    db.commit()
    db.refresh(session_obj)
    return session_obj
