# Twilio authentication middleware integration
_Exported on 3/23/2026 at 14:00:27 CDT from Cursor (2.6.19)_

---

**User**

import os
import hmac
import hashlib
import base64
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Load Twilio auth token from environment
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


def verify_twilio_signature(request_url: str, params: dict, twilio_signature: str) -> bool:
    """
    Verifies that the request came from Twilio using X-Twilio-Signature.
    """

    if not TWILIO_AUTH_TOKEN:
        raise Exception("TWILIO_AUTH_TOKEN environment variable not set")

    # Sort parameters alphabetically
    sorted_params = sorted(params.items())

    # Construct data string
    data = request_url
    for key, value in sorted_params:
        data += key + value

    # Create HMAC-SHA1 signature
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

        # Only check webhook endpoint
        if request.url.path == "/webhook":

            twilio_signature = request.headers.get("X-Twilio-Signature")

            if not twilio_signature:
                raise HTTPException(status_code=401, detail="Missing Twilio signature")

            # Read form data from Twilio
            form = await request.form()
            params = dict(form)

            # Full URL Twilio used
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

compare the above code with the existing code in this page and add all new lines of code 

---

**Cursor**

I’ll load your existing `auth.py`, compare it to the snippet you pasted, and then update the file by inserting only the missing/new lines so it matches your latest version.

I’ll merge your Twilio verification and middleware code into the existing `auth.py`, keeping the current `verify_whatsapp_request` intact and only adding the missing imports and functions.

Your new Twilio verification and middleware code has been merged into the existing `auth.py` without removing any of the original logic.

- **Added imports**: `os`, `hmac`, `hashlib`, `base64`, and `BaseHTTPMiddleware`.
- **Added** `TWILIO_AUTH_TOKEN`, `verify_twilio_signature`, `TwilioAuthMiddleware`, and `verify_internal_token` above the existing `verify_whatsapp_request`.
- The original `verify_whatsapp_request` function remains unchanged at the bottom of the file.

