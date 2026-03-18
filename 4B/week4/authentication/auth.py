from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import hmac
import hashlib
import base64
from starlette.middleware.base import BaseHTTPMiddleware

from ..database.models import get_db
from .phone_verification import authenticate_phone_user
from .session_manager import generate_session, validate_session


TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


def verify_twilio_signature(request_url: str, params: dict, twilio_signature: str) -> bool:
    """
    Verifies that the request came from Twilio using X-Twilio-Signature.
    """

    if not TWILIO_AUTH_TOKEN:
        raise Exception("TWILIO_AUTH_TOKEN environment variable not set")

    sorted_params = sorted(params.items())

    data = request_url
    for key, value in sorted_params:
        data += key + value

    digest = hmac.new(
        TWILIO_AUTH_TOKEN.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha1
    ).digest()

    computed_signature = base64.b64encode(digest).decode("utf-8")

    return hmac.compare_digest(computed_signature, twilio_signature)


class TwilioAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify Twilio webhook signatures
    """

    async def dispatch(self, request: Request, call_next):

        if request.url.path == "/webhook":

            twilio_signature = request.headers.get("X-Twilio-Signature")

            if not twilio_signature:
                raise HTTPException(status_code=401, detail="Missing Twilio signature")

            form = await request.form()
            params = dict(form)

            request_url = str(request.url)

            valid = verify_twilio_signature(
                request_url,
                params,
                twilio_signature
            )

            if not valid:
                raise HTTPException(status_code=401, detail="Invalid Twilio signature")

        response = await call_next(request)
        return response


def verify_internal_token(request: Request):
    """
    Optional helper for protecting internal API endpoints
    """

    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    expected_token = os.getenv("INTERNAL_API_TOKEN")

    if token != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Invalid authorization token")


async def verify_whatsapp_request(request: Request, db: Session = Depends(get_db)):
    """
    FastAPI dependency/helper to authenticate incoming Twilio WhatsApp webhook requests.

    Twilio sends form-encoded POST data with fields: From, Body, ProfileName.

    Returns:
        {
            "user": User,
            "conversation": Conversation,
            "session": SessionState,
            "message_text": str,
            "phone_number": str,
            "profile_name": str | None
        }

    If the payload contains no user message (e.g. status callbacks), returns:
        {"status": "ignored"}
    """
    # Twilio sends form-encoded data, not JSON
    try:
        form = await request.form()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid form payload")

    try:
        # Twilio prefixes numbers with "whatsapp:" e.g. "whatsapp:+1234567890"
        from_field = form.get("From", "")
        phone_number = from_field.replace("whatsapp:", "").strip()

        if not phone_number:
            return {"status": "ignored"}

        profile_name = form.get("ProfileName") or None
        message_text = (form.get("Body") or "").strip()

        if not message_text:
            return {"status": "ignored"}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Malformed Twilio payload: {exc}",
        )

    # Authenticate user + conversation
    try:
        user, conversation = authenticate_phone_user(
            db=db,
            phone_number=phone_number,
            name=profile_name,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail=f"User authentication failed: {exc}",
        )

    # Session handling:
    # If caller sends X-Session-Token and it is valid, reuse it.
    # Otherwise create a new session.
    session_token = request.headers.get("X-Session-Token")
    session = (
        validate_session(db=db, session_token=session_token)
        if session_token
        else None
    )

    if not session or str(session.user_id) != str(user.id):
        session = generate_session(db=db, user_id=user.id)

    return {
        "user": user,
        "conversation": conversation,
        "session": session,
        "message_text": message_text.strip(),
        "phone_number": phone_number,
        "profile_name": profile_name,
    }
