# database/state_tracking.py

import copy
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from .schema import Conversation, Escalation, Message, SessionState, User


VALID_ESCALATION_STATUSES = {"queued", "assigned", "resolved"}
VALID_ESCALATION_PRIORITIES = {"low", "medium", "high", "critical"}


def _next_state_for_queue_status(queue_status: str) -> str:
    if queue_status == "assigned":
        return "ACTIVE_HANDOFF"
    if queue_status == "resolved":
        return "RESOLVED"
    return "WAITING_FOR_VOLUNTEER"


def _now() -> datetime:
    """Return the current UTC time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_session_token(session_token: str) -> str:
    """Return a SHA-256 hash for a raw session token."""
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries without mutating the originals."""
    result = copy.deepcopy(dict1)

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def get_or_create_user(db: Session, phone_number: str, name: Optional[str] = None) -> User:
    """Fetch an existing user by phone number or create a new one."""
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


def get_or_create_active_conversation(db: Session, user_id: uuid.UUID) -> Conversation:
    """Return the user's latest active conversation, creating one if needed."""
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
    """Store a single inbound or outbound message for a conversation."""
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


def create_session(db: Session, user_id: uuid.UUID, ttl_minutes: int = 1440) -> SessionState:
    """Create a new active session for a user and deactivate older sessions.

    The raw token is returned only as a transient `raw_session_token attribute
    on the returned SQLAlchemy object. The database stores only the hashed token.
    """
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

    raw_session_token = str(uuid.uuid4())
    hashed_session_token = _hash_session_token(raw_session_token)

    new_session = SessionState(
        user_id=user_id,
        session_token=hashed_session_token,
        expires_at=now_utc + timedelta(minutes=ttl_minutes),
        is_active=True,
        state={},
        updated_at=now_utc,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    new_session.raw_session_token = raw_session_token
    return new_session


def get_session_by_token(db: Session, session_token: str) -> Optional[SessionState]:
    """Lookup an active, non-expired session by a raw session token."""
    if not session_token:
        return None

    now_utc = _now()
    hashed_session_token = _hash_session_token(session_token)

    return (
        db.query(SessionState)
        .filter(
            SessionState.session_token == hashed_session_token,
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
    """Merge new context values into an existing session state object."""
    session_obj = db.query(SessionState).filter(SessionState.id == session_id).first()

    if not session_obj:
        return None

    current_state = session_obj.state or {}
    session_obj.state = deep_merge_dicts(current_state, updates)
    session_obj.updated_at = _now()

    db.commit()
    db.refresh(session_obj)
    return session_obj


def create_escalation(
    db: Session,
    priority: str = "medium",
    queue_status: str = "queued",
    assigned_volunteer: Optional[str] = None,
    next_state: Optional[str] = None,
    message_for_user: Optional[str] = None,
    success: bool = True,
    errors: Optional[List[str]] = None,
) -> Escalation:
    """Create a new escalation ticket aligned to the locked schema fields."""
    cleaned_priority = priority.strip().lower() if isinstance(priority, str) else ""
    if cleaned_priority not in VALID_ESCALATION_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. Must be one of: {', '.join(sorted(VALID_ESCALATION_PRIORITIES))}"
        )

    cleaned_status = queue_status.strip().lower() if isinstance(queue_status, str) else ""
    if cleaned_status not in VALID_ESCALATION_STATUSES:
        raise ValueError(
            f"Invalid queue_status '{queue_status}'. Must be one of: {', '.join(sorted(VALID_ESCALATION_STATUSES))}"
        )

    cleaned_assigned = assigned_volunteer.strip() if isinstance(assigned_volunteer, str) else None
    if cleaned_assigned == "":
        cleaned_assigned = None

    cleaned_message = message_for_user.strip() if isinstance(message_for_user, str) else ""
    if cleaned_message == "":
        cleaned_message = "I'm connecting you to a human volunteer now. Please hold on."

    cleaned_errors: List[str] = []
    if isinstance(errors, list):
        for item in errors:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    cleaned_errors.append(text)

    escalation = Escalation(
        success=bool(success),
        queue_status=cleaned_status,
        assigned_volunteer=cleaned_assigned,
        next_state=(next_state.strip() if isinstance(next_state, str) else "") or _next_state_for_queue_status(cleaned_status),
        message_for_user=cleaned_message,
        priority=cleaned_priority,
        errors=cleaned_errors,
    )
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    return escalation


def update_escalation_status(
    db: Session,
    ticket_id: uuid.UUID,
    queue_status: str,
    assigned_volunteer: Optional[str] = None,
    error_note: Optional[str] = None,
) -> Optional[Escalation]:
    """Transition an escalation to a new status.

    Updates queue_status, next_state, and assigned_volunteer using the
    finalized escalation schema fields.
    """
    if queue_status not in VALID_ESCALATION_STATUSES:
        raise ValueError(
            f"Invalid status '{queue_status}'. "
            f"Must be one of: {', '.join(sorted(VALID_ESCALATION_STATUSES))}"
        )

    escalation = db.query(Escalation).filter(Escalation.ticket_id == ticket_id).first()
    if not escalation:
        return None

    escalation.queue_status = queue_status
    escalation.next_state = _next_state_for_queue_status(queue_status)

    if isinstance(assigned_volunteer, str):
        cleaned_assigned = assigned_volunteer.strip() or None
        if cleaned_assigned is not None:
            escalation.assigned_volunteer = cleaned_assigned

    if queue_status == "queued":
        escalation.assigned_volunteer = None

    if isinstance(error_note, str):
        cleaned_note = error_note.strip()
        if cleaned_note:
            errors = escalation.errors or []
            errors.append(cleaned_note)
            escalation.errors = errors

    db.commit()
    db.refresh(escalation)
    return escalation


def get_escalations_by_status(
    db: Session,
    status: Optional[str] = None,
) -> List[Escalation]:
    """Return all escalations, optionally filtered by status."""
    query = db.query(Escalation)

    if status:
        if status not in VALID_ESCALATION_STATUSES:
            raise ValueError(
                f"Invalid status filter '{status}'. "
                f"Must be one of: {', '.join(sorted(VALID_ESCALATION_STATUSES))}"
            )
        query = query.filter(Escalation.queue_status == status)

    return query.all()


def get_escalation_by_id(
    db: Session,
    escalation_id: uuid.UUID,
) -> Optional[Escalation]:
    """Fetch a single escalation by its primary key."""
    return db.query(Escalation).filter(Escalation.ticket_id == escalation_id).first() 