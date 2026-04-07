"""Escalation HTTP API — bot-to-human handoff tickets."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..authentication.internal_bearer import verify_escalations_bearer
from ..authentication.session_manager import update_session_context
from ..database.models import get_db
from ..database.schema import Escalation
from ..database.state_tracking import (
    create_escalation,
    get_escalation_by_id,
    update_escalation_status,
)

logger = logging.getLogger("week7.escalations")

router = APIRouter(
    tags=["escalations"],
    dependencies=[Depends(verify_escalations_bearer)],
)


def _dt_iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    # Stored as naive UTC in the ORM layer
    return dt.isoformat() + "Z"


def _escalation_to_dict(escalation: Escalation) -> Dict[str, Any]:
    return {
        "id": str(escalation.id),
        "user_id": str(escalation.user_id),
        "session_id": str(escalation.session_id) if escalation.session_id else None,
        "reason": escalation.reason,
        "context": escalation.context if escalation.context is not None else {},
        "status": escalation.status,
        "created_at": _dt_iso(escalation.created_at),
        "resolved_at": _dt_iso(escalation.resolved_at),
        "resolved_by": escalation.resolved_by,
    }


class EscalationCreateBody(BaseModel):
    user_id: uuid.UUID
    reason: str
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[uuid.UUID] = None

    @field_validator("reason")
    @classmethod
    def reason_non_empty(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("reason must be a string")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("reason must be non-empty")
        return cleaned


class EscalationResolveBody(BaseModel):
    resolved_by: str
    notes: Optional[str] = None

    @field_validator("resolved_by")
    @classmethod
    def resolved_by_non_empty(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("resolved_by must be a string")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("resolved_by must be non-empty")
        return cleaned


@router.post("", status_code=201)
def create_escalation_ticket(
    body: EscalationCreateBody,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create an escalation ticket; optional session_id must belong to user_id."""
    try:
        escalation = create_escalation(
            db=db,
            user_id=body.user_id,
            reason=body.reason,
            context=body.context,
            session_id=body.session_id,
        )
    except ValueError as exc:
        logger.warning(
            "escalation_create_rejected | user_id=%s | session_id=%s | detail=%s",
            body.user_id,
            body.session_id,
            str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception(
            "escalation_create_failed | user_id=%s | session_id=%s",
            body.user_id,
            body.session_id,
        )
        raise

    if body.session_id is not None:
        try:
            update_session_context(
                db=db,
                session_id=body.session_id,
                context_updates={
                    "last_escalation_id": str(escalation.id),
                    "last_escalation_status": escalation.status,
                    "last_escalation_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as session_err:
            logger.warning(
                "escalation_session_context_failed | escalation_id=%s | session_id=%s | err=%s",
                escalation.id,
                body.session_id,
                session_err,
                exc_info=True,
            )

    logger.info(
        "escalation_created | escalation_id=%s | user_id=%s | session_id=%s | status=%s",
        escalation.id,
        escalation.user_id,
        escalation.session_id,
        escalation.status,
    )
    return {
        "id": str(escalation.id),
        "status": escalation.status,
        "user_id": str(escalation.user_id),
        "session_id": str(escalation.session_id) if escalation.session_id else None,
        "created_at": _dt_iso(escalation.created_at),
    }


@router.get("/{escalation_id}")
def get_escalation(
    escalation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return a single escalation by id."""
    escalation = get_escalation_by_id(db=db, escalation_id=escalation_id)
    if escalation is None:
        logger.warning("escalation_not_found | escalation_id=%s", escalation_id)
        raise HTTPException(status_code=404, detail="Escalation not found")
    logger.info(
        "escalation_fetched | escalation_id=%s | user_id=%s | status=%s",
        escalation.id,
        escalation.user_id,
        escalation.status,
    )
    return _escalation_to_dict(escalation)


@router.put("/{escalation_id}/resolve")
def resolve_escalation(
    escalation_id: uuid.UUID,
    body: EscalationResolveBody,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Mark an escalation resolved with optional notes; idempotent if already resolved."""
    escalation = get_escalation_by_id(db=db, escalation_id=escalation_id)
    if escalation is None:
        logger.warning("escalation_resolve_not_found | escalation_id=%s", escalation_id)
        raise HTTPException(status_code=404, detail="Escalation not found")

    if escalation.status == "resolved":
        logger.info(
            "escalation_resolve_idempotent | escalation_id=%s | user_id=%s",
            escalation.id,
            escalation.user_id,
        )
        return _escalation_to_dict(escalation)

    try:
        updated = update_escalation_status(
            db=db,
            escalation_id=escalation_id,
            new_status="resolved",
            resolved_by=body.resolved_by,
            note=body.notes,
        )
    except ValueError as exc:
        logger.warning(
            "escalation_resolve_invalid | escalation_id=%s | detail=%s",
            escalation_id,
            str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("escalation_resolve_failed | escalation_id=%s", escalation_id)
        raise

    assert updated is not None
    logger.info(
        "escalation_resolved | escalation_id=%s | user_id=%s | resolved_by=%s",
        updated.id,
        updated.user_id,
        updated.resolved_by,
    )
    return _escalation_to_dict(updated)
