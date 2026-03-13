"""
Unified FastAPI entrypoint for Week 4.

Implements the orchestration pipeline for the JKYog WhatsApp bot:
- Initializes the database
- Handles WhatsApp webhook requests
- Wires together authentication, session management, logging, and bot core
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from authentication.auth import verify_whatsapp_request
from authentication.session_manager import update_session_context
from bot.intent_classifier import classify_intent
from bot.response_builder import build_response
from database.models import get_db, init_db
from database.state_tracking import log_message


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("week4.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    Initializes the database before serving requests.
    """
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Database initialization failed: %s", exc)
        # Continue running so non-DB paths can still function if needed.
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="JKYog WhatsApp Bot",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


@app.get("/")
def root() -> Dict[str, str]:
    """
    Root endpoint to confirm the bot is running.
    """
    return {"message": "JKYog WhatsApp Bot is running"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Main WhatsApp webhook endpoint.

    Lifecycle:
    1. Validate/parse request (verify_whatsapp_request)
    2. Authenticate user + session
    3. Log inbound message
    4. Build response via bot core
    5. Update session context
    6. Log outbound message
    7. Return JSON response
    """
    try:
        auth_result = await verify_whatsapp_request(request=request, db=db)

        if auth_result.get("status") == "ignored":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ignored",
                    "message": "Non-message event ignored",
                },
            )

        user = auth_result["user"]
        conversation = auth_result["conversation"]
        session = auth_result["session"]
        user_message: str = auth_result["message_text"]
        phone_number: str = auth_result["phone_number"]
        profile_name: Optional[str] = auth_result.get("profile_name")

        logger.info(
            "Incoming message | phone=%s | user_id=%s | conversation_id=%s",
            phone_number,
            user.id,
            conversation.id,
        )

        # Log inbound message with optional pre-classified intent
        inbound_intent: Optional[str] = None
        try:
            inbound_intent = classify_intent(user_message).get("intent")
        except Exception as classify_err:
            logger.warning(
                "Intent classification failed before logging: %s",
                classify_err,
            )

        log_message(
            db=db,
            conversation_id=conversation.id,
            direction="inbound",
            text=user_message,
            intent=inbound_intent,
        )

        # Build response from bot core
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
        )

        # Update session context with latest interaction
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
            logger.warning("Session context update failed: %s", session_err)

        # Log outbound message
        log_message(
            db=db,
            conversation_id=conversation.id,
            direction="outbound",
            text=bot_reply,
            intent=inbound_intent,
        )

        logger.info(
            "Response generated | user_id=%s | conversation_id=%s",
            user.id,
            conversation.id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "reply": bot_reply,
                "user_id": str(user.id),
                "conversation_id": str(conversation.id),
                "session_token": session.session_token,
            },
        )

    except HTTPException as exc:
        logger.error("HTTP error in webhook: %s", exc.detail)
        raise exc

    except Exception as exc:  # pragma: no cover - catch-all safety
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

