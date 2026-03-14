"""
Alembic migration environment.

Database URL is read from DATABASE_URL and normalized (postgres:// -> postgresql://).
Metadata is taken from the application's Base so autogenerate detects all models.
"""
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

# Add the week4 directory to sys.path so "database" package resolves when
# running Alembic from 4B/week4 (e.g. `alembic upgrade head`).
config_file = Path(config.config_file_name).resolve()
script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
week4_dir = script_location.parent
if str(week4_dir) not in sys.path:
    sys.path.insert(0, str(week4_dir))

# Prefer the already-loaded module from the running FastAPI app so we don't
# create a second SQLAlchemy engine (and leak a second connection pool).
_models = (
    sys.modules.get("4B.week4.database.models")
    or sys.modules.get("database.models")
)
if _models:
    Base = _models.Base
    # Ensure schema models are registered with this Base.
    if "4B.week4.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401 - register all models with Base.metadata

# Set sqlalchemy.url from DATABASE_URL so we don't hardcode in alembic.ini.
db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Only generates SQL; does not connect to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
