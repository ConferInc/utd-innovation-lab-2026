"""Canonical Pydantic payloads for event ingestion and escalation responses."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from .recurrence import ALLOWED_RECURRENCE_VALUES, RecurrenceText, validate_recurrence_value

class SponsorshipTier(BaseModel):
    tier_name: str
    price: Optional[float] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def _validate_tier(self) -> SponsorshipTier:
        self.tier_name = self.tier_name.strip()
        if not self.tier_name:
            raise ValueError("tier_name must be non-empty")
        if self.description is not None:
            self.description = self.description.strip() or None
        return self


class Price(BaseModel):
    amount: Optional[float] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _normalize_notes(self) -> Price:
        if self.notes is not None:
            self.notes = self.notes.strip() or None
        return self


Category = Literal[
    "festival",
    "retreat",
    "satsang",
    "youth",
    "class",
    "workshop",
    "health",
    "special_event",
    "other",
]
EventType = Literal["in_person", "online", "hybrid", "unknown"]
RegistrationStatus = Literal["open", "closed", "unknown"]
SourceSite = Literal["radhakrishnatemple", "jkyog"]
SourceConfidence = Literal["high", "medium", "low"]
Priority = Literal["low", "medium", "high", "critical"]
QueueStatus = Literal["queued", "assigned", "resolved"]
NextState = Literal["WAITING_FOR_VOLUNTEER", "ACTIVE_HANDOFF", "RESOLVED"]


class EventPayload(BaseModel):
    id: Optional[int] = None
    name: str
    subtitle: Optional[str] = None
    category: Optional[Category] = None
    event_type: Optional[EventType] = None
    is_recurring: bool = False
    recurrence_text: Optional[RecurrenceText] = Field(
        default=None,
        description=(
            "Machine-readable recurrence; constrained to RecurrenceText Literal; "
            f"allowed: {', '.join(ALLOWED_RECURRENCE_VALUES)}"
        ),
    )
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    registration_required: Optional[bool] = None
    registration_status: Optional[RegistrationStatus] = None
    registration_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    parking_notes: Optional[str] = None
    transportation_notes: Optional[str] = None
    food_info: Optional[str] = None
    price: Price = Field(default_factory=Price)
    sponsorship_tiers: List[SponsorshipTier] = Field(default_factory=list)
    source_url: HttpUrl
    source_site: SourceSite
    source_page_type: Optional[str] = None
    scraped_at: datetime
    source_confidence: Optional[SourceConfidence] = None
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _apply_legacy_aliases(cls, raw: Any) -> Any:
        if not isinstance(raw, dict):
            return raw
        data = dict(raw)
        if data.get("location_name") in (None, "") and data.get("location"):
            data["location_name"] = data.get("location")
        if data.get("notes") in (None, "") and data.get("special_notes"):
            data["notes"] = data.get("special_notes")
        if data.get("sponsorship_tiers") is None and data.get("sponsorship_data") is not None:
            legacy_tiers = data.get("sponsorship_data")
            if isinstance(legacy_tiers, list):
                def _normalize_price(value: Any) -> Any:
                    if isinstance(value, str) and not value.strip():
                        return None
                    return value
                data["sponsorship_tiers"] = [
                    {
                        "tier_name": item.get("tier_name") or item.get("name"),
                        "price": _normalize_price(item.get("price") if "price" in item else item.get("amount")),
                        "description": item.get("description") or item.get("link"),
                    }
                    for item in legacy_tiers
                    if isinstance(item, dict)
                ]
        elif isinstance(data.get("sponsorship_tiers"), list):
            normalized_tiers: List[Dict[str, Any]] = []
            for item in data["sponsorship_tiers"]:
                if not isinstance(item, dict):
                    normalized_tiers.append(item)
                    continue
                mapped_price = item.get("price") if "price" in item else item.get("amount")
                if isinstance(mapped_price, str) and not mapped_price.strip():
                    mapped_price = None
                normalized_tiers.append(
                    {
                        "tier_name": item.get("tier_name") or item.get("name"),
                        "price": mapped_price,
                        "description": item.get("description") or item.get("link"),
                    }
                )
            data["sponsorship_tiers"] = normalized_tiers
        if data.get("recurrence_text") in (None, "") and data.get("recurrence_pattern"):
            data["recurrence_text"] = data.get("recurrence_pattern")
        return data

    @field_validator("recurrence_text", mode="before")
    @classmethod
    def _validate_recurrence_text(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return validate_recurrence_value(value if isinstance(value, str) else str(value))

    @model_validator(mode="after")
    def _validate_contract(self) -> EventPayload:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name must be non-empty")
        for attr in (
            "subtitle",
            "timezone",
            "location_name",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
            "description",
            "registration_url",
            "contact_email",
            "contact_phone",
            "parking_notes",
            "transportation_notes",
            "food_info",
            "source_page_type",
            "notes",
        ):
            value = getattr(self, attr)
            if isinstance(value, str):
                setattr(self, attr, value.strip() or None)
        if self.is_recurring and self.recurrence_text is None:
            raise ValueError(
                "recurrence_text is required when is_recurring is true. "
                f"Allowed values: {', '.join(ALLOWED_RECURRENCE_VALUES)}"
            )
        if not self.is_recurring:
            self.recurrence_text = None
        return self


ScrapedEventPayload = EventPayload


class EscalationResponse(BaseModel):
    success: bool
    ticket_id: str
    queue_status: QueueStatus
    assigned_volunteer: Optional[str] = None
    next_state: NextState
    message_for_user: str
    priority: Priority
    errors: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _normalize(self) -> EscalationResponse:
        if self.assigned_volunteer is not None:
            self.assigned_volunteer = self.assigned_volunteer.strip() or None
        self.message_for_user = self.message_for_user.strip()
        self.errors = [error.strip() for error in self.errors if isinstance(error, str) and error.strip()]
        return self


def as_seed_payload(event: EventPayload) -> Dict[str, Any]:
    data = event.model_dump(mode="json")
    for key in ("start_datetime", "end_datetime", "scraped_at"):
        dt = data.get(key)
        if isinstance(dt, datetime):
            data[key] = dt.isoformat()
    return data
