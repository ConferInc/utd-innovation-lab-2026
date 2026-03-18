import os
from pathlib import Path
from typing import Generator

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


def _get_database_url() -> str:
    """Return the configured database URL for SQLAlchemy.

    Normalizes legacy ``postgres://`` URLs to the ``postgresql://`` form
    expected by SQLAlchemy.

    Raises:
        RuntimeError: If the DATABASE_URL environment variable is not set.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


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
    pool_size=5,
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


def init_db() -> None:
    """Run Alembic migrations to bring the database schema up to date."""
    week4_dir = Path(__file__).resolve().parent.parent
    alembic_ini = week4_dir / "alembic.ini"
    if not alembic_ini.is_file():
        raise FileNotFoundError(f"Alembic config not found: {alembic_ini}")
    cfg = Config(str(alembic_ini))
    # Override script_location with an absolute path so Alembic finds the
    # migrations folder regardless of the process working directory (e.g. on Render
    # the CWD is /opt/render/project/src, not 4B/week4/).
    cfg.set_main_option("script_location", str(week4_dir / "migrations"))
    command.upgrade(cfg, "head")