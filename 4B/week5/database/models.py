import os
import time
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

T = TypeVar("T")


def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy postgres:// URLs to postgresql:// for SQLAlchemy.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    """Read a float environment variable with a fallback default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _run_with_retry(
    operation: Callable[[], T],
    retries: int | None = None,
    base_delay_seconds: float | None = None,
) -> T:
    """Run a database operation with exponential backoff retries."""
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

    raise RuntimeError(
        f"Database operation failed after {max_attempts} attempts"
    ) from last_error


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=_env_int("DB_POOL_SIZE", 5),
    max_overflow=_env_int("DB_MAX_OVERFLOW", 2),
    pool_timeout=_env_int("DB_POOL_TIMEOUT", 30),
    pool_recycle=_env_int("DB_POOL_RECYCLE", 300),
    pool_use_lifo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _execute_health_query() -> None:
    """Run a lightweight query used by the DB health endpoint."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def check_db_health() -> dict[str, Any]:
    """Check whether the application can connect to the database."""
    try:
        _run_with_retry(_execute_health_query)
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }


def init_db() -> None:
    """Run Alembic migrations to bring the database schema up to date."""
    week4_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week4_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(week4_dir / "migrations"))

    _run_with_retry(lambda: command.upgrade(cfg, "head"))