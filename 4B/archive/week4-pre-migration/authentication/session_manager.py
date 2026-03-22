# auth/session_manager.py
import uuid
from sqlalchemy.orm import Session
from ..database.state_tracking import create_session, get_session_by_token, merge_session_state

def generate_session(db: Session, user_id: uuid.UUID, ttl_minutes: int = 1440):
    """
    Generates a new secure session token for the user.
    Automatically invalidates any previous active sessions.
    """
    return create_session(db=db, user_id=user_id, ttl_minutes=ttl_minutes)

def validate_session(db: Session, session_token: str):
    """
    Validates an existing session token.
    Returns the session if valid and unexpired, otherwise None.
    """
    if not session_token:
        return None
    return get_session_by_token(db=db, session_token=session_token)

def update_session_context(db: Session, session_id: uuid.UUID, context_updates: dict):
    """
    Updates the session state (context tracking) for the current user.
    Useful for storing temporary bot data (e.g., current intent, booking step).
    """
    return merge_session_state(db=db, session_id=session_id, updates=context_updates)