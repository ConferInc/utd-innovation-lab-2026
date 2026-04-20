"""
Extract event start/end datetimes from noisy HTML-derived text.

Output strings must be accepted by ``events.storage.event_storage._parse_datetime``:
- ISO-8601 with optional ``Z`` or numeric offset
- After parsing, storage normalizes to naive UTC

**Timezone policy:** Date-only values (no time in source) are interpreted in
``EVENT_SCRAPER_DEFAULT_TZ`` (default ``America/Chicago``) at
``EVENT_SCRAPER_DEFAULT_START_HOUR`` / ``EVENT_SCRAPER_DEFAULT_START_MINUTE``,
then converted to UTC for the emitted ISO string ending in ``Z``.
"""

from __future__ import annotations

import calendar
import os
import re
from datetime import date, datetime, time, timezone
from typing import Any, Optional, Tuple
from zoneinfo import ZoneInfo

from dateutil import parser as dateutil_parser

# ---------------------------------------------------------------------------
# Mirror events.storage.event_storage._parse_datetime (no SQLAlchemy import)
# ---------------------------------------------------------------------------


def parse_storage_datetime(value: Any) -> Optional[datetime]:
    """Return naive UTC datetime or None — same rules as event_storage._parse_datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    return None


def is_valid_storage_datetime(value: Any) -> bool:
    return parse_storage_datetime(value) is not None


def _default_tz() -> ZoneInfo:
    name = os.getenv("EVENT_SCRAPER_DEFAULT_TZ", "America/Chicago")
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("America/Chicago")


def _default_start_time() -> time:
    h = int(os.getenv("EVENT_SCRAPER_DEFAULT_START_HOUR", "10"))
    m = int(os.getenv("EVENT_SCRAPER_DEFAULT_START_MINUTE", "0"))
    return time(hour=max(0, min(h, 23)), minute=max(0, min(m, 59)))


def _to_storage_iso_utc(dt: datetime) -> str:
    """Emit UTC with Z suffix for JSON; storage accepts this."""
    if dt.tzinfo is None:
        u = dt.replace(tzinfo=timezone.utc)
    else:
        u = dt.astimezone(timezone.utc)
    naive = u.replace(tzinfo=None)
    return naive.isoformat(timespec="seconds") + "Z"


def _local_date_at_default_time(d: date) -> str:
    tz = _default_tz()
    dt = datetime.combine(d, _default_start_time(), tzinfo=tz)
    return _to_storage_iso_utc(dt)


_ISO_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(?:\.\d+)?(Z|[+-]\d{2}:?\d{2})?",
    re.IGNORECASE,
)

_MONTH_LONG = "|".join(calendar.month_name[1:])
_MONTH_SHORT = "|".join(calendar.month_abbr[1:])
_RANGE_SAME_MONTH = re.compile(
    rf"(?P<m>{_MONTH_LONG}|{_MONTH_SHORT})\s+"
    rf"(?P<d1>\d{{1,2}})\s*[–\-\s]+\s*(?P<d2>\d{{1,2}}),?\s*(?P<y>\d{{4}})",
    re.IGNORECASE,
)

# e.g. "Apr 1st, 2026" or "April 4th, 2026, 11:00 AM" (temple / Webflow copy)
_ORDINAL_DATE = re.compile(
    r"\b(?P<mon>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+"
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?,?\s*(?P<year>\d{4})",
    re.IGNORECASE,
)

_HAS_TIME = re.compile(r"\b\d{1,2}:\d{2}\b")


# Known US timezone abbreviations mapped to fixed UTC offsets in seconds.
# dateutil emits UnknownTimezoneWarning otherwise and leaves ``tzinfo`` as None,
# forcing fallback to ``_default_tz`` even when the source explicitly named CST/EST/PST.
# ``"T"`` is mapped to ``None`` so the stray separator from strings like
# ``"2026-04-04T14:30"`` is treated as literal text instead of an unknown zone.
_TZINFOS: dict[str, int | None] = {
    "UTC": 0,
    "GMT": 0,
    "EST": -5 * 3600,
    "EDT": -4 * 3600,
    "CST": -6 * 3600,
    "CDT": -5 * 3600,
    "MST": -7 * 3600,
    "MDT": -6 * 3600,
    "PST": -8 * 3600,
    "PDT": -7 * 3600,
    "T": None,
}


def _first_iso_substring(text: str) -> Optional[str]:
    m = _ISO_PATTERN.search(text)
    return m.group(0) if m else None


def _month_name_to_num(name: str) -> int:
    n = name.strip().lower()
    for i in range(1, 13):
        if calendar.month_name[i].lower() == n or calendar.month_abbr[i].lower() == n:
            return i
    raise ValueError(f"unknown month: {name!r}")


def extract_event_datetimes(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    From free-form page text, return (start_iso, end_iso) strings for JSON storage.

    - Prefer first valid ISO-8601 substring in ``text``.
    - Else try "Month d1 – d2, year" range (same month).
    - Else try dateutil fuzzy parse on ``text`` (first date found).
    - Date-only results use default local time → UTC ``Z`` string.
    """
    if not text or not text.strip():
        return None, None

    # 1) ISO in page
    iso = _first_iso_substring(text)
    if iso:
        parsed = parse_storage_datetime(iso)
        if parsed:
            return parsed.strftime("%Y-%m-%dT%H:%M:%S") + "Z", None
        try:
            fix = iso
            if fix.endswith("Z"):
                fix = fix[:-1] + "+00:00"
            dt = datetime.fromisoformat(fix)
            return _to_storage_iso_utc(dt), None
        except ValueError:
            pass

    # 2) Ordinal dates: Apr 1st, 2026 …
    om = _ORDINAL_DATE.search(text)
    if om:
        # Slice from the date token onward; stop before a second date clause (em dash / "&").
        end_i = min(len(text), om.end() + 40)
        snippet = text[om.start() : end_i]
        for sep in ("\u2014", "\u2013", " & ", " \u0026 "):  # em dash, en dash, ampersand clauses
            if sep in snippet:
                snippet = snippet.split(sep)[0].strip()
                break
        try:
            now_local = datetime.now(_default_tz())
            dt = dateutil_parser.parse(snippet, fuzzy=True, default=now_local, tzinfos=_TZINFOS)
            if 1990 <= dt.year <= 2100:
                has_explicit_time = bool(_HAS_TIME.search(snippet))
                if not has_explicit_time and dt.hour == 0 and dt.minute == 0 and dt.second == 0:
                    return _local_date_at_default_time(dt.date()), None
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_default_tz())
                return _to_storage_iso_utc(dt), None
        except (ValueError, TypeError, OverflowError):
            pass

    # 3) Same-month range: Mar 26-29, 2026
    m = _RANGE_SAME_MONTH.search(text)
    if m:
        month_s = m.group("m")
        d1, d2, y = int(m.group("d1")), int(m.group("d2")), int(m.group("y"))
        try:
            month_num = _month_name_to_num(month_s)
            start_d = date(y, month_num, d1)
            end_d = date(y, month_num, d2)
            if end_d >= start_d:
                return _local_date_at_default_time(start_d), _local_date_at_default_time(end_d)
        except ValueError:
            pass

    # 4) dateutil fuzzy on full text
    try:
        now_local = datetime.now(_default_tz())
        dt = dateutil_parser.parse(text, fuzzy=True, default=now_local, tzinfos=_TZINFOS)
        if dt.year < 1990 or dt.year > 2100:
            return None, None
        has_explicit_time = bool(_HAS_TIME.search(text))
        if not has_explicit_time and dt.hour == 0 and dt.minute == 0 and dt.second == 0:
            return _local_date_at_default_time(dt.date()), None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_default_tz())
        return _to_storage_iso_utc(dt), None
    except (ValueError, TypeError, OverflowError):
        pass

    return None, None
