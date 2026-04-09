"""
Database connection, engine, session factory, and health checks.

Supports both PostgreSQL (production / Render) and SQLite (local dev fallback).
If DATABASE_URL is not set, defaults to sqlite:///./local_dev.db so that
Team 4A can run the API locally without Render credentials.
"""

import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Database URL resolution
# ---------------------------------------------------------------------------

def _get_database_url() -> str:
    """Return normalized database URL from DATABASE_URL env var.

    Falls back to a local SQLite file when the variable is absent,
    so Team 4A can test the API without PostgreSQL.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Default to local SQLite for offline / local development
        db_url = "sqlite:///./local_dev.db"
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url


def _is_sqlite(url: str) -> bool:
    """Return True when the URL points to a SQLite database."""
    return url.startswith("sqlite:///")


# ---------------------------------------------------------------------------
# Env helpers
# ---------------------------------------------------------------------------

def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    """Execute a database operation with exponential-backoff retries."""
    max_attempts = retries or _env_int("DB_CONNECT_RETRIES", 4)
    base_delay = (
        base_delay_seconds
        if base_delay_seconds is not None
        else _env_float("DB_RETRY_BASE_DELAY_SECONDS", 1.0)
    )

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            time.sleep(delay)

    raise RuntimeError(f"Database operation failed after {max_attempts} attempts") from last_error


# ---------------------------------------------------------------------------
# SQLAlchemy setup
# ---------------------------------------------------------------------------

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

DATABASE_URL = _get_database_url()
IS_SQLITE = _is_sqlite(DATABASE_URL)

if IS_SQLITE:
    # SQLite does not support connection pooling parameters
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


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def _execute_health_query() -> None:
    """Run a lightweight connectivity query."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def _execute_escalations_probe() -> None:
    """Verify escalations table can be queried."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM escalations LIMIT 1"))


def _execute_events_probe() -> None:
    """Verify events table can be queried."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1 FROM events LIMIT 1"))


def check_db_health() -> dict[str, Any]:
    """Return service health based on connection and table probes."""
    try:
        _run_with_retry(_execute_health_query)
    except Exception as exc:
        return {"status": "error", "database": "disconnected", "detail": str(exc)}

    escalations_ok = True
    events_ok = True

    try:
        _run_with_retry(_execute_escalations_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        escalations_ok = False

    try:
        _run_with_retry(_execute_events_probe, retries=2, base_delay_seconds=0.5)
    except Exception:
        events_ok = False

    if escalations_ok and events_ok:
        return {
            "status": "ok",
            "database": "connected",
            "tables": {"escalations": "ok", "events": "ok"},
        }

    return {
        "status": "degraded",
        "database": "connected",
        "tables": {
            "escalations": "ok" if escalations_ok else "unreachable",
            "events": "ok" if events_ok else "unreachable",
        },
    }


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Apply Alembic migrations (PostgreSQL) or create all tables (SQLite)."""
    if IS_SQLITE:
        # For SQLite we skip Alembic and create tables directly from metadata.
        # Import schema so all models are registered on Base.metadata.
        from . import schema as _schema  # noqa: F401
        Base.metadata.create_all(bind=engine)
        return

    from alembic import command
    from alembic.config import Config

    week_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week_dir / "migrations"))
    _run_with_retry(lambda: command.upgrade(cfg, "head"))
