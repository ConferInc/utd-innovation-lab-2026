# auth/phone_verification.py
from sqlalchemy.orm import Session

from ..database.state_tracking import (
    get_or_create_user,
    get_or_create_active_conversation,
)


def authenticate_phone_user(db: Session, phone_number: str, name: str | None = None):
    """
    Identifies a user by phone number across conversations and
    guarantees there is an active conversation context.
    """
    if not phone_number:
        raise ValueError("Phone number is required for authentication.")

    cleaned_phone = phone_number.strip().replace("+", "")

    user = get_or_create_user(db=db, phone_number=cleaned_phone, name=name)
    conversation = get_or_create_active_conversation(db=db, user_id=user.id)

    return user, conversation
