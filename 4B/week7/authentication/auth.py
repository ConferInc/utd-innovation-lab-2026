import os

from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.models import get_db
from .phone_verification import authenticate_phone_user
from .session_manager import generate_session, validate_session


def _build_public_url(request: Request) -> str:
    """
    Build the URL Twilio used to call this endpoint.

    Twilio signature validation requires the exact URL (scheme/host/path/query).
    In reverse-proxy deployments (e.g., Render), the app may see an internal URL;
    prefer forwarded headers if present.
    """
    proto = request.headers.get("x-forwarded-proto")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if proto and host:
        path = request.url.path
        query = request.url.query
        return f"{proto}://{host}{path}" + (f"?{query}" if query else "")

    return str(request.url)


def _verify_twilio_signature(request: Request, form: dict) -> None:
    """
    Verify Twilio webhook signature.

    Raises HTTPException(401) if the signature is missing/invalid.
    """
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing Twilio signature")

    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise HTTPException(status_code=500, detail="Server missing TWILIO_AUTH_TOKEN")

    try:
        from twilio.request_validator import RequestValidator
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Twilio validator unavailable: {exc}")

    url = _build_public_url(request)
    validator = RequestValidator(auth_token)
    if not validator.validate(url, form, signature):
        raise HTTPException(status_code=401, detail="Invalid Twilio signature")


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

    # Verify Twilio signature before any DB work.
    _verify_twilio_signature(request=request, form=dict(form))

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
