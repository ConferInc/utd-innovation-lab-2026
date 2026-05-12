"""
Engine and session factory for Team 4B–aligned Postgres.

When DATABASE_URL is unset, no engine is created — DB logging is skipped (local dev).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from sqlalchemy import MetaData, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------------------------
# URL (optional)
# ---------------------------------------------------------------------------


def _get_database_url() -> str | None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return None
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite:///")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


DATABASE_URL = _get_database_url()
IS_SQLITE = bool(DATABASE_URL and _is_sqlite(DATABASE_URL))

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = None
SessionLocal: sessionmaker | None = None

if DATABASE_URL:
    if IS_SQLITE:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=_env_int("DB_POOL_SIZE", 5),
            max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
            pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
            pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
            pool_use_lifo=True,
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _message_column_ddl() -> Dict[str, str]:
    if engine is None:
        return {}
    dialect = engine.dialect.name
    json_type = "JSONB" if dialect == "postgresql" else "TEXT"
    return {
        "twilio_message_sid": "VARCHAR(255)",
        "status": "VARCHAR(64)",
        "failure_reason": "TEXT",
        "correlation_id": "VARCHAR(64)",
        "metadata_json": json_type,
        "total_latency_ms": "INTEGER",
    }


def _ensure_message_table_columns() -> List[str]:
    if engine is None:
        return []

    inspector = inspect(engine)
    if "messages" not in inspector.get_table_names():
        return []

    existing_columns = {column["name"] for column in inspector.get_columns("messages")}
    added_columns: List[str] = []
    column_ddl = _message_column_ddl()

    with engine.begin() as connection:
        for column_name, ddl in column_ddl.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(f"ALTER TABLE messages ADD COLUMN {column_name} {ddl}")
            )
            added_columns.append(column_name)
    return added_columns


def init_database() -> Dict[str, Any]:
    if engine is None:
        return {
            "enabled": False,
            "healthy": False,
            "status": "disabled",
            "reason": "DATABASE_URL not set",
            "columns_added": [],
        }

    from . import schema_chat  # noqa: F401 - ensure ORM models are registered

    Base.metadata.create_all(bind=engine)
    columns_added = _ensure_message_table_columns()
    return {
        "enabled": True,
        "healthy": True,
        "status": "ready",
        "columns_added": columns_added,
    }


def check_database_health() -> Dict[str, Any]:
    if engine is None:
        return {
            "enabled": False,
            "healthy": False,
            "status": "disabled",
            "reason": "DATABASE_URL not set",
        }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "enabled": True,
            "healthy": True,
            "status": "ok",
        }
    except Exception as exc:
        return {
            "enabled": True,
            "healthy": False,
            "status": "error",
            "reason": str(exc),
        }
