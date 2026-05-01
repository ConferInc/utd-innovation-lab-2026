"""Shared Postgres URL for integration tests."""

from __future__ import annotations

import os


def integration_database_url() -> str:
    """
    ``WEEK7_E2E_DATABASE_URL`` takes precedence; otherwise ``DATABASE_URL``
    (``conftest.py`` sets a default for local runs).
    """
    url = os.environ.get("WEEK7_E2E_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL or WEEK7_E2E_DATABASE_URL for integration tests.")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url
