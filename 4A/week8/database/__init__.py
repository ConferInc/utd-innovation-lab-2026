"""Postgres message logging (Team 4B schema); optional when DATABASE_URL is unset."""

from .message_logging import (
    get_or_create_active_conversation,
    get_or_create_user,
    log_message,
    normalize_twilio_phone,
)
from .models import SessionLocal

__all__ = [
    "SessionLocal",
    "get_or_create_user",
    "get_or_create_active_conversation",
    "log_message",
    "normalize_twilio_phone",
]
