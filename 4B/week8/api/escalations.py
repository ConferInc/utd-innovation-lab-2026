"""Escalation HTTP API — bot-to-human handoff tickets (Team 4A / Chanakya contract)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from authentication.internal_bearer import verify_escalations_bearer
from authentication.session_manager import update_session_context
from database.models import get_db
from database.schema import Escalation
from database.state_tracking import (
    create_escalation,
    get_escalation_by_id,
    update_escalation_status,
)
from events.schemas.event_payload import EscalationResponse

logger = logging.getLogger("week8.escalations")

router = APIRouter(
    tags=["escalations"],
    dependencies=[Depends(verify_escalations_bearer)],
)


def _escalation_to_response(row: Escalation) -> Dict[str, Any]:
    return EscalationResponse.model_validate(
        {
            "success": row.success,
            "ticket_id": str(row.ticket_id),
            "queue_status": row.queue_status,
            "assigned_volunteer": row.assigned_volunteer,
            "next_state": row.next_state,
            "message_for_user": row.message_for_user,
            "priority": row.priority,
            "errors": list(row.errors or []),
        }
    ).model_dump(mode="json")


class EscalationCreateBody(BaseModel):
    priority: str = "medium"
    queue_status: str = "queued"
    assigned_volunteer: Optional[str] = None
    next_state: Optional[str] = None
    message_for_user: Optional[str] = None
    success: bool = True
    errors: List[str] = Field(default_factory=list)
    requester_user_id: Optional[uuid.UUID] = None
    requester_session_id: Optional[uuid.UUID] = None


class EscalationResolveBody(BaseModel):
    assigned_volunteer: Optional[str] = None
    error_note: Optional[str] = None

    @field_validator("assigned_volunteer")
    @classmethod
    def strip_assigned(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s or None


@router.post("", status_code=201)
def create_escalation_ticket(
    body: EscalationCreateBody,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a canonical escalation ticket."""
    try:
        escalation = create_escalation(
            db=db,
            priority=body.priority,
            queue_status=body.queue_status,
            assigned_volunteer=body.assigned_volunteer,
            next_state=body.next_state,
            message_for_user=body.message_for_user,
            success=body.success,
            errors=body.errors,
            requester_user_id=body.requester_user_id,
            requester_session_id=body.requester_session_id,
        )
    except ValueError as exc:
        logger.warning("escalation_create_rejected | detail=%s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("escalation_create_failed")
        raise

    if body.requester_session_id is not None:
        try:
            update_session_context(
                db=db,
                session_id=body.requester_session_id,
                context_updates={
                    "last_escalation_ticket_id": str(escalation.ticket_id),
                    "last_escalation_queue_status": escalation.queue_status,
                    "last_escalation_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as session_err:
            logger.warning(
                "escalation_session_context_failed | ticket_id=%s | session_id=%s | err=%s",
                escalation.ticket_id,
                body.requester_session_id,
                session_err,
                exc_info=True,
            )

    logger.info(
        "escalation_created | ticket_id=%s | queue_status=%s | priority=%s",
        escalation.ticket_id,
        escalation.queue_status,
        escalation.priority,
    )
    return _escalation_to_response(escalation)


@router.get("/{ticket_id}")
def get_escalation(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return a single escalation by ticket id."""
    escalation = get_escalation_by_id(db=db, escalation_id=ticket_id)
    if escalation is None:
        logger.warning("escalation_not_found | ticket_id=%s", ticket_id)
        raise HTTPException(status_code=404, detail="Escalation not found")
    logger.info(
        "escalation_fetched | ticket_id=%s | queue_status=%s",
        escalation.ticket_id,
        escalation.queue_status,
    )
    return _escalation_to_response(escalation)


@router.put("/{ticket_id}/resolve")
def resolve_escalation(
    ticket_id: uuid.UUID,
    body: EscalationResolveBody,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Set queue_status to resolved; idempotent if already resolved."""
    escalation = get_escalation_by_id(db=db, escalation_id=ticket_id)
    if escalation is None:
        logger.warning("escalation_resolve_not_found | ticket_id=%s", ticket_id)
        raise HTTPException(status_code=404, detail="Escalation not found")

    if escalation.queue_status == "resolved":
        logger.info(
            "escalation_resolve_idempotent | ticket_id=%s",
            escalation.ticket_id,
        )
        return _escalation_to_response(escalation)

    try:
        updated = update_escalation_status(
            db=db,
            ticket_id=ticket_id,
            queue_status="resolved",
            assigned_volunteer=body.assigned_volunteer,
            error_note=body.error_note,
        )
    except ValueError as exc:
        logger.warning("escalation_resolve_invalid | ticket_id=%s | detail=%s", ticket_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("escalation_resolve_failed | ticket_id=%s", ticket_id)
        raise

    if updated is None:
        raise HTTPException(status_code=404, detail="Escalation not found")

    logger.info(
        "escalation_resolved | ticket_id=%s | assigned_volunteer=%s",
        updated.ticket_id,
        updated.assigned_volunteer,
    )
    return _escalation_to_response(updated)
