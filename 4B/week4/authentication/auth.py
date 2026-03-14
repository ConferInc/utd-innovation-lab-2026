from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.models import get_db
from .phone_verification import authenticate_phone_user
from .session_manager import generate_session, validate_session


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
