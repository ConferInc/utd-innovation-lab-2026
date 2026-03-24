"""
Unified FastAPI entrypoint for Week 6.

Implements the orchestration pipeline for the JKYog WhatsApp bot:
- Initializes the database
- Handles WhatsApp webhook requests
- Wires together authentication, session management, logging, and bot core
"""

import logging
import os
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .authentication.auth import verify_whatsapp_request
from .authentication.session_manager import update_session_context
from .bot.intent_classifier import classify_intent
from .bot.response_builder import build_response
from .database.models import SessionLocal, check_db_health, get_db, init_db
from .database.state_tracking import log_message
from .service_wrappers import StripeWrapper, MapsWrapper, CalendarWrapper
from .service_wrappers.base_wrapper import NonRetryableServiceError


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("week4.main")

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    Initializes the database before serving requests.
    """
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="JKYog WhatsApp Bot",
    version="1.0.0",
    lifespan=lifespan,
)

def send_whatsapp_message(to: str, body: str) -> str:
    """Send a text message to a WhatsApp user via Twilio."""
    from twilio.rest import Client

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    to_e164 = to if to.startswith("+") else f"+{to}"
    msg = client.messages.create(
        from_=os.environ["TWILIO_WHATSAPP_FROM"],
        body=body,
        to=f"whatsapp:{to_e164}",
    )
    return getattr(msg, "sid", "")


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/health/db", response_model=None)
def health_check_db():
    """
    Database health check endpoint.
    Returns 200 if the database is fully healthy or degraded (base
    connectivity works but an auxiliary table is unreachable).
    Returns 503 only when base database connectivity fails entirely.
    """
    result = check_db_health()
    if result["status"] == "ok":
        return result
    if result["status"] == "degraded":
        return JSONResponse(status_code=200, content=result)
    return JSONResponse(status_code=503, content=result)


@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint to confirm the bot is running."""
    return {"message": "JKYog WhatsApp Bot is running"}


@app.post("/create-payment")
def create_payment() -> Dict[str, Any]:
    """
    Create a Stripe payment intent (demo). Returns client_secret for client-side confirm.

    Uses StripeWrapper with retry and error handling. Returns 400 on bad inputs and
    503 on upstream Stripe issues.
    """
    logger.info("create_payment: initializing StripeWrapper")
    try:
        stripe = StripeWrapper()
    except ValueError as exc:
        logger.exception("create_payment: Stripe configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Stripe configuration error: {str(exc)}"},
        )

    try:
        intent = stripe.create_payment_intent(amount=1000)
        client_secret = intent.get("client_secret")
        logger.info("create_payment: payment_intent created successfully")
        return {"client_secret": client_secret}
    except NonRetryableServiceError as exc:
        logger.exception("create_payment: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("create_payment: unexpected Stripe error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Stripe service error: {str(exc)}"},
        )


@app.get("/maps")
def maps_test() -> Any:
    """
    Test Google Maps geocode (Dallas) using MapsWrapper.

    Returns geocode results for a hardcoded address. Returns 503 on upstream issues.
    """
    logger.info("maps_test: initializing MapsWrapper")
    try:
        maps = MapsWrapper()
    except ValueError as exc:
        logger.exception("maps_test: Maps configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Maps configuration error: {str(exc)}"},
        )

    try:
        return maps.geocode("Dallas")
    except NonRetryableServiceError as exc:
        logger.exception("maps_test: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("maps_test: unexpected Google Maps error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Maps service error: {str(exc)}"},
        )


@app.get("/calendar")
def calendar_test() -> Any:
    """
    Test Google Calendar upcoming events using CalendarWrapper.

    Returns a JSON object with upcoming events. Returns 503 on upstream issues.
    """
    logger.info("calendar_test: initializing CalendarWrapper")
    try:
        calendar = CalendarWrapper()
    except ValueError as exc:
        logger.exception("calendar_test: Calendar configuration error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Calendar configuration error: {str(exc)}"},
        )

    try:
        return calendar.list_events()
    except NonRetryableServiceError as exc:
        logger.exception("calendar_test: non-retryable error")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    except Exception as exc:
        logger.exception("calendar_test: unexpected Google Calendar error")
        return JSONResponse(
            status_code=503,
            content={"detail": f"Google Calendar service error: {str(exc)}"},
        )


def _process_incoming_message(
    *,
    auth_result: Dict[str, Any],
    received_at_iso: str,
    received_monotonic_s: float,
) -> None:
    db: Session = SessionLocal()
    process_start_monotonic_s = time.monotonic()
    try:
        user = auth_result["user"]
        conversation = auth_result["conversation"]
        session = auth_result["session"]
        user_message: str = auth_result["message_text"]
        phone_number: str = auth_result["phone_number"]
        profile_name: Optional[str] = auth_result.get("profile_name")

        queue_delay_ms = int((process_start_monotonic_s - received_monotonic_s) * 1000)
        logger.info(
            "Message received_at=%s | queue_delay_ms=%s | phone=%s | user_id=%s | conversation_id=%s",
            received_at_iso,
            queue_delay_ms,
            phone_number,
            user.id,
            conversation.id,
        )

        inbound_intent: Optional[str] = None
        inbound_confidence: Optional[float] = None
        try:
            intent_result = classify_intent(user_message)
            inbound_intent = intent_result.get("intent")
            inbound_confidence = intent_result.get("confidence")
        except Exception as classify_err:
            logger.warning("Intent classification failed: %s", classify_err)

        try:
            log_message(
                db=db,
                conversation_id=conversation.id,
                direction="inbound",
                text=user_message,
                intent=inbound_intent,
            )
        except Exception as log_err:
            logger.error("Failed to log inbound message: %s", log_err, exc_info=True)

        user_context: Dict[str, Any] = {
            "user_id": str(user.id),
            "conversation_id": str(conversation.id),
            "session_id": str(session.id),
            "phone_number": phone_number,
            "profile_name": profile_name,
            "session_state": session.state or {},
        }

        bot_reply = build_response(
            user_message=user_message,
            user_context=user_context,
            intent=inbound_intent,
            confidence=inbound_confidence,
        )

        try:
            send_start = time.monotonic()
            twilio_sid = send_whatsapp_message(to=phone_number, body=bot_reply)
            send_ms = int((time.monotonic() - send_start) * 1000)
            total_ms = int((time.monotonic() - received_monotonic_s) * 1000)
            logger.info(
                "Message sent_at=%s | twilio_sid=%s | send_ms=%s | total_ms=%s | phone=%s | conversation_id=%s",
                _utc_now_iso(),
                twilio_sid,
                send_ms,
                total_ms,
                phone_number,
                conversation.id,
            )
        except Exception as send_err:
            logger.error(
                "Failed to send WhatsApp message to %s: %s",
                phone_number,
                send_err,
                exc_info=True,
            )

        try:
            update_session_context(
                db=db,
                session_id=session.id,
                context_updates={
                    "last_user_message": user_message,
                    "last_bot_reply": bot_reply,
                    "last_intent": inbound_intent,
                },
            )
        except Exception as session_err:
            logger.error("Session context update failed: %s", session_err, exc_info=True)

        try:
            log_message(
                db=db,
                conversation_id=conversation.id,
                direction="outbound",
                text=bot_reply,
                intent=inbound_intent,
            )
        except Exception as log_err:
            logger.error("Failed to log outbound message: %s", log_err, exc_info=True)

        logger.info(
            "Response generated | user_id=%s | conversation_id=%s",
            user.id,
            conversation.id,
        )
    except Exception as exc:
        logger.exception("Unhandled error while processing incoming message: %s", exc)
    finally:
        db.close()


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Main WhatsApp webhook endpoint."""
    try:
        req_start = time.monotonic()
        received_at_iso = _utc_now_iso()
        auth_result = await verify_whatsapp_request(request=request, db=db)

        if auth_result.get("status") == "ignored":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ignored",
                    "message": "Non-message event ignored",
                },
            )

        background_tasks.add_task(
            _process_incoming_message,
            auth_result=auth_result,
            received_at_iso=received_at_iso,
            received_monotonic_s=req_start,
        )

        ack_ms = int((time.monotonic() - req_start) * 1000)
        logger.info(
            "Webhook ack | received_at=%s | ack_ms=%s | phone=%s",
            received_at_iso,
            ack_ms,
            auth_result.get("phone_number"),
        )
        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "detail": "Message accepted for background processing",
            },
        )

    except HTTPException as exc:
        logger.error("HTTP error in webhook: %s", exc.detail)
        raise exc

    except Exception as exc:
        logger.exception("Unhandled webhook error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": "Internal server error while processing webhook",
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("4B.week4.main:app", host="0.0.0.0", port=8000, reload=True)