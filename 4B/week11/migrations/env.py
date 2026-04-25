"""Alembic migration environment for Week 7.

Loads SQLAlchemy metadata from the app models and optionally overrides
the DB URL from DATABASE_URL.
"""

import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

# Ensure the week7 package root is importable when Alembic runs directly.
config_file = Path(config.config_file_name).resolve()
script_location = (config_file.parent / config.get_main_option("script_location", "migrations")).resolve()
week_dir = script_location.parent
if str(week_dir) not in sys.path:
    sys.path.insert(0, str(week_dir))

_models = sys.modules.get("4B.week7.database.models") or sys.modules.get("database.models")
if _models:
    Base = _models.Base
    if "4B.week7.database.schema" not in sys.modules and "database.schema" not in sys.modules:
        import database.schema  # noqa: F401
else:
    from database.models import Base
    import database.schema  # noqa: F401

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode without opening a DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode using a real DB connection."""
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
