"""Mocked Twilio webhook end-to-end test for Team 4B bot pipeline."""

from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType
from types import SimpleNamespace
import os
import uuid
from unittest.mock import AsyncMock, patch

from fastapi import APIRouter
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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

try:
    from database.models import Base
    from database.schema import Conversation, SessionState, User
except ImportError:
    from week8.database.models import Base
    from week8.database.schema import Conversation, SessionState, User


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


def test_whatsapp_webhook_e2e_with_real_sqlite_and_classifier_content() -> None:
    """
    Companion webhook test (Week 11 polish):
    - real SQLite backend
    - real classify_intent path (not mocked)
    - content assertions on outbound message body
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    try:
        user = User(id=uuid.uuid4(), phone_number="+14695550124", name="Real Classifier User")
        db.add(user)
        db.flush()
        conversation = Conversation(id=uuid.uuid4(), user_id=user.id, status="active")
        db.add(conversation)
        session = SessionState(
            id=uuid.uuid4(),
            user_id=user.id,
            session_token="a" * 64,
            is_active=True,
            state={},
        )
        db.add(session)
        db.commit()

        auth_result = {
            "user": SimpleNamespace(id=user.id),
            "conversation": SimpleNamespace(id=conversation.id),
            "session": SimpleNamespace(id=session.id, state={}),
            "message_text": "Can you share upcoming holi events?",
            "phone_number": user.phone_number,
            "profile_name": user.name,
        }

        def _override_get_db():
            s = TestSessionLocal()
            try:
                yield s
            finally:
                s.close()

        app_main.app.dependency_overrides[app_main.get_db] = _override_get_db

        sent_payload: dict[str, str] = {}

        def _capture_send(to: str, body: str) -> str:
            sent_payload["to"] = to
            sent_payload["body"] = body
            return "SM_REAL_SQLITE_001"

        with (
            patch.object(app_main, "verify_whatsapp_request", new=AsyncMock(return_value=auth_result)),
            patch.object(app_main, "SessionLocal", TestSessionLocal),
            patch.object(app_main, "send_whatsapp_message", side_effect=_capture_send),
            patch("bot.response_builder._generate_with_llm", return_value=None),
            patch("bot.response_builder._get_calendar_events_from_wrapper", return_value=[]),
            patch(
                "bot.response_builder.get_upcoming_events",
                return_value=[
                    {"summary": "Holi Mela Dallas", "start": "2026-03-07T10:00:00"},
                    {"summary": "Weekly Sunday Satsang", "start": "2026-03-08T10:30:00"},
                ],
            ),
            patch.dict(os.environ, {"DISABLE_SINGLE_CALL": "1"}, clear=False),
        ):
            client = TestClient(app_main.app)
            resp = client.post(
                "/webhook/whatsapp",
                data={
                    "From": "whatsapp:+14695550124",
                    "Body": auth_result["message_text"],
                    "MessageSid": "SM_IN_REAL_001",
                },
                headers={"X-Twilio-Signature": "test-signature"},
            )

            assert resp.status_code == 200
            assert resp.json()["status"] == "accepted"
            assert sent_payload["to"] == "+14695550124"

            # Real classifier + real response pipeline should produce event-focused content.
            body = sent_payload["body"]
            assert "Upcoming Events:" in body
            assert "Holi Mela Dallas" in body
            assert "Weekly Sunday Satsang" in body
            assert len(body.strip()) > 20
    finally:
        db.close()
        engine.dispose()
        app_main.app.dependency_overrides.clear()
