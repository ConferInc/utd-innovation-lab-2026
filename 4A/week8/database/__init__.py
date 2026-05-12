"""Postgres message logging (Team 4B schema); optional when DATABASE_URL is unset."""

from .message_logging import (
    get_or_create_active_conversation,
    get_or_create_user,
    log_message,
    normalize_twilio_phone,
    update_message,
)
from .models import SessionLocal, check_database_health, init_database

__all__ = [
    "SessionLocal",
    "get_or_create_user",
    "get_or_create_active_conversation",
    "log_message",
    "normalize_twilio_phone",
    "update_message",
    "init_database",
    "check_database_health",
]
