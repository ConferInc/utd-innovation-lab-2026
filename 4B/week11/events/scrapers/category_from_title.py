"""Infer EventPayload ``category`` from free text (title or card body).

Matching uses word-boundary regex (``\\b``) so substring collisions like
``"classical"`` no longer match ``class`` and ``"campus"`` no longer matches
``camp``. Keyword tuples below should list all forms (singular/plural) that
should match - ``\\bprayer\\b`` deliberately does not match ``"prayers"``.
"""
from __future__ import annotations

import re
from typing import Final, Literal, Pattern

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
        "international yoga day",
        "yoga day",
        "janmashtami",
        "rama navami",
        "ram navami",
        "hanuman",
        "jayanti",
        "utsav",
        "festival",
        "festivals",
    ),
    # Avoid bare "camp" - it would match inside unrelated words like "campus"
    # even with word boundaries when the upstream copy literally says "camp".
    "retreat": ("retreat", "retreats", "spiritual camp", "weekend retreat"),
    "satsang": (
        "satsang",
        "satsangs",
        "kirtan",
        "kirtans",
        "bhajan",
        "bhajans",
        "aarti",
        "arati",
        "prayer",
        "prayers",
        "parayanam",
    ),
    "youth": ("yuva", "youth", "students", "utd", "college"),
    "class": ("class", "classes", "course", "courses", "seminar", "yoga", "meditation", "kriya"),
    "workshop": ("workshop", "workshops", "training", "intensive"),
    "health": ("health fair", "health camp", "medical", "biometric", "screening"),
    "special_event": ("visit", "talk", "speaker", "swami", "lecture", "guest"),
}


def _compile_patterns(keyword_map: dict[str, tuple[str, ...]]) -> dict[str, Pattern[str]]:
    """Return one compiled ``\\b(kw1|kw2|...)\\b`` regex per category."""
    compiled: dict[str, Pattern[str]] = {}
    for category, keywords in keyword_map.items():
        if not keywords:
            continue
        alternation = "|".join(re.escape(kw) for kw in keywords)
        compiled[category] = re.compile(rf"\b(?:{alternation})\b", re.IGNORECASE)
    return compiled


CATEGORY_PATTERNS: Final[dict[str, Pattern[str]]] = _compile_patterns(CATEGORY_KEYWORDS)


def guess_event_category(text: str) -> Category:
    """Return a ``Category`` literal; defaults to ``\"other\"`` when no keyword matches."""
    t = (text or "").lower()
    if not t.strip():
        return "other"
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(t):
            return category  # type: ignore[return-value]
    return "other"
