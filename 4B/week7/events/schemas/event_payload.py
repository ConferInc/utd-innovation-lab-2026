from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SponsorshipTier(BaseModel):
    name: str
    amount: str
    link: str

    @field_validator("name", "amount", "link")
    @classmethod
    def non_empty_str(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("must be a string")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned


class ScrapedEventPayload(BaseModel):
    """
    Canonical scraped event payload (DB-friendly).

    This shape is intended to match the Week 7 `events` table columns and be consumable
    by the database upsert layer.
    """

    name: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    venue_details: Optional[str] = None
    parking_notes: Optional[str] = None
    food_info: Optional[str] = None
    sponsorship_data: List[SponsorshipTier] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None
    source_url: HttpUrl
    source_site: str = Field(description="One of: radhakrishnatemple, jkyog")
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    category: Optional[str] = None
    special_notes: Optional[str] = None
    scraped_at: datetime

    @field_validator("name", "source_site")
    @classmethod
    def required_str_non_empty(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("must be a string")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    @field_validator("source_site")
    @classmethod
    def validate_source_site(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in {"radhakrishnatemple", "jkyog"}:
            raise ValueError("source_site must be one of: radhakrishnatemple, jkyog")
        return cleaned

    @field_validator(
        "description",
        "location",
        "venue_details",
        "parking_notes",
        "food_info",
        "recurrence_pattern",
        "category",
        "special_notes",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        text = str(v).strip()
        return text or None


def as_seed_payload(event: ScrapedEventPayload) -> Dict[str, Any]:
    """
    Convert to a JSON-serializable dict suitable for seeding/upsert.

    Note: datetimes are emitted as ISO-8601 with 'Z' if UTC-aware; otherwise as ISO.
    """

    data = event.model_dump()
    # Pydantic will serialize HttpUrl to string already. Ensure datetimes are strings.
    for key in ("start_datetime", "end_datetime", "scraped_at"):
        dt = data.get(key)
        if isinstance(dt, datetime):
            iso = dt.isoformat()
            data[key] = iso
    return data

