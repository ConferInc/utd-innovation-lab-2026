"""Infer EventPayload ``category`` from free text (title or card body)."""
from __future__ import annotations

from typing import Final, Literal

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

# First matching bucket wins (order matters for overlapping keywords).
CATEGORY_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "festival": (
        "navratri",
        "diwali",
        "holi",
        "janmashtami",
        "rama navami",
        "ram navami",
        "hanuman",
        "jayanti",
        "utsav",
        "festival",
    ),
    # Avoid bare "camp" — it matches inside unrelated words like "campus".
    "retreat": ("retreat", "spiritual camp", "weekend retreat"),
    "satsang": ("satsang", "kirtan", "bhajan", "aarti", "arati", "prayer", "parayanam"),
    "youth": ("yuva", "youth", "students", "utd", "college"),
    "class": ("class", "course", "seminar", "yoga", "meditation", "kriya"),
    "workshop": ("workshop", "training", "intensive"),
    "health": ("health fair", "health camp", "medical", "biometric", "screening"),
    "special_event": ("visit", "talk", "speaker", "swami", "lecture", "guest"),
}


def guess_event_category(text: str) -> Category:
    """Return a ``Category`` literal; defaults to ``\"other\"`` when no keyword matches."""
    t = (text or "").lower()
    if not t.strip():
        return "other"
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return category  # type: ignore[return-value]
    return "other"
