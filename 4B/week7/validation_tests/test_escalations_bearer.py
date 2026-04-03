"""Bearer auth on /escalations (401 without token, success path when configured)."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_4B_ROOT = Path(__file__).resolve().parents[2]
if str(_4B_ROOT) not in sys.path:
    sys.path.insert(0, str(_4B_ROOT))

from week7.api.escalations import router as escalations_router
from week7.database.models import get_db


@pytest.fixture
def esc_app(monkeypatch):
    monkeypatch.setenv("ESCALATIONS_API_TOKEN", "test-bearer-token")
    app = FastAPI()
    app.include_router(escalations_router, prefix="/escalations")

    def _db():
        yield None

    app.dependency_overrides[get_db] = _db
    return app


def test_escalations_rejects_missing_bearer(esc_app, monkeypatch) -> None:
    monkeypatch.delenv("ESCALATIONS_API_TOKEN", raising=False)
    with TestClient(esc_app) as client:
        eid = uuid.uuid4()
        r = client.get(f"/escalations/{eid}")
    assert r.status_code == 401


def test_escalations_rejects_wrong_bearer(esc_app) -> None:
    with TestClient(esc_app) as client:
        eid = uuid.uuid4()
        r = client.get(
            f"/escalations/{eid}",
            headers={"Authorization": "Bearer wrong"},
        )
    assert r.status_code == 401


@patch("week7.api.escalations.get_escalation_by_id")
def test_escalations_accepts_bearer(mock_get, esc_app) -> None:
    mock_get.return_value = None
    with TestClient(esc_app) as client:
        eid = uuid.uuid4()
        r = client.get(
            f"/escalations/{eid}",
            headers={"Authorization": "Bearer test-bearer-token"},
        )
    assert r.status_code == 404
    mock_get.assert_called_once()
