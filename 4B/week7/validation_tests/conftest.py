import getpass
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text


def pytest_configure(config) -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    validation_tests_dir = Path(__file__).resolve().parent
    for d in (week7_dir, validation_tests_dir):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    # Default favors local peer auth (common on macOS/Homebrew Postgres); override with DATABASE_URL.
    _u = getpass.getuser()
    os.environ.setdefault("DATABASE_URL", f"postgresql://{_u}@127.0.0.1:5432/postgres")
    config.addinivalue_line("markers", "integration: Postgres-backed tests (use DATABASE_URL or WEEK7_E2E_DATABASE_URL)")


def pytest_runtest_setup(item: pytest.Function) -> None:
    """Skip ``integration`` tests when Postgres is down or ``events`` is not migrated."""
    if not list(item.iter_markers(name="integration")):
        return
    from integration_db import integration_database_url

    url = integration_database_url()
    if not url.startswith("postgresql"):
        pytest.skip("integration tests require a postgresql DATABASE_URL")

    try:
        eng = create_engine(url, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
            reg = conn.execute(text("SELECT to_regclass('public.events')")).scalar()
            if reg is None:
                pytest.skip(
                    "integration tests need table `public.events` — run Alembic migrations against DATABASE_URL"
                )
    except Exception as exc:
        pytest.skip(f"Postgres unavailable for integration tests: {exc}")
