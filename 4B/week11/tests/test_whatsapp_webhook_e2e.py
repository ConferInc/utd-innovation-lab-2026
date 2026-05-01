"""Mocked Twilio webhook end-to-end test for Team 4B bot pipeline."""

from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import APIRouter
from fastapi.testclient import TestClient

_4B_ROOT = Path(__file__).resolve().parents[2]
_WEEK8_ROOT = Path(__file__).resolve().parents[1]
for p in (str(_WEEK8_ROOT), str(_4B_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Prevent import-path issues in api.stripe_webhooks from blocking webhook E2E test.
if "api.stripe_webhooks" not in sys.modules:
    stripe_stub = ModuleType("api.stripe_webhooks")
    stripe_stub.router = APIRouter()
    sys.modules["api.stripe_webhooks"] = stripe_stub

try:
    import main as app_main
except ImportError:
    from week8 import main as app_main


class _FakeDbSession:
    def close(self) -> None:
        pass


def _auth_result() -> dict:
    return {
        "user": SimpleNamespace(id="u-1"),
        "conversation": SimpleNamespace(id="c-1"),
        "session": SimpleNamespace(id="s-1", state={}),
        "message_text": "What are today's events?",
        "phone_number": "+14695550123",
        "profile_name": "Webhook User",
    }


def test_whatsapp_webhook_e2e_pipeline_sends_formatted_reply() -> None:
    expected_reply = "📅 Upcoming Events:\n• Holi Mela Dallas\n• Weekly Sunday Satsang"
    fake_session = _FakeDbSession()

    app_main.app.dependency_overrides[app_main.get_db] = lambda: iter([fake_session])
    try:
        with (
            patch.object(app_main, "verify_whatsapp_request", new=AsyncMock(return_value=_auth_result())),
            patch.object(app_main, "SessionLocal", return_value=fake_session),
            patch.object(
                app_main,
                "classify_intent",
                return_value={"intent": "event_query", "confidence": 0.98},
            ) as mock_classify,
            patch.object(app_main, "build_response", return_value=expected_reply) as mock_build,
            patch.object(app_main, "send_whatsapp_message", return_value="SM_TEST_001") as mock_send,
            patch.object(app_main, "log_message") as mock_log,
            patch.object(app_main, "update_session_context") as mock_update_session,
        ):
            client = TestClient(app_main.app)
            resp = client.post(
                "/webhook/whatsapp",
                data={
                    "From": "whatsapp:+14695550123",
                    "Body": "What are today's events?",
                    "MessageSid": "SM_IN_001",
                },
                headers={"X-Twilio-Signature": "test-signature"},
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "accepted"

            # Background task path should execute in TestClient request lifecycle.
            mock_classify.assert_called_once()
            mock_build.assert_called_once()
            mock_send.assert_called_once_with(to="+14695550123", body=expected_reply)
            assert mock_log.call_count >= 2  # inbound + outbound
            mock_update_session.assert_called_once()
    finally:
        app_main.app.dependency_overrides.clear()
