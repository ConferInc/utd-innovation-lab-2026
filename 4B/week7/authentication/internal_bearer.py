"""Bearer token verification for internal APIs (e.g. escalations)."""

from __future__ import annotations

import os
import secrets

from fastapi import HTTPException, Request

_UNAUTH_DETAIL = "Not authenticated"


def verify_escalations_bearer(request: Request) -> None:
    expected = os.environ.get("ESCALATIONS_API_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=401,
            detail=_UNAUTH_DETAIL,
        )
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=_UNAUTH_DETAIL)
    token = auth[7:].strip()
    if not token or len(token) != len(expected) or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail=_UNAUTH_DETAIL)
