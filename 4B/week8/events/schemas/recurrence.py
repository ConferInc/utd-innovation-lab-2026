"""Single source of truth for allowed machine-readable recurrence values (Pydantic, ORM, migrations)."""

from __future__ import annotations

ALLOWED_RECURRENCE_VALUES: tuple[str, ...] = (
    "daily",
    "weekdays",
    "weekends",
    "weekly:monday",
    "weekly:tuesday",
    "weekly:wednesday",
    "weekly:thursday",
    "weekly:friday",
    "weekly:saturday",
    "weekly:sunday",
)

ALLOWED_RECURRENCE_SET = frozenset(ALLOWED_RECURRENCE_VALUES)


def normalize_recurrence_for_storage(value: str) -> str:
    """Lowercase and normalize ``weekly:<day>`` casing."""
    v = value.strip().lower()
    if not v:
        return ""
    if v.startswith("weekly:"):
        day = v.split(":", 1)[1].strip().lower()
        return f"weekly:{day}"
    return v


def validate_recurrence_value(value: str | None) -> str | None:
    """Return normalized value or None; raise ValueError if non-empty but not allowed."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    stripped = value.strip()
    if not stripped:
        return None
    normalized = normalize_recurrence_for_storage(stripped)
    if normalized not in ALLOWED_RECURRENCE_SET:
        allowed = ", ".join(ALLOWED_RECURRENCE_VALUES)
        raise ValueError(
            f"Invalid recurrence value {value!r}. Allowed values: {allowed}"
        )
    return normalized


def recurrence_check_clause_for_column(column_name: str) -> str:
    """SQL boolean expression for CHECK constraints (PostgreSQL / SQLite)."""
    quoted = ", ".join(f"'{v}'" for v in ALLOWED_RECURRENCE_VALUES)
    return f"{column_name} IS NULL OR {column_name} IN ({quoted})"
