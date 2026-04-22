from schedule_data import SCHEDULE
import json

with open("4A/week8/schedule_exceptions.json") as f:
    EXCEPTIONS = json.load(f)
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

# =========================
# TIMEZONE
# =========================
TIMEZONE = ZoneInfo("America/Chicago")

# =========================
# SCHEDULE DATA
# =========================
SCHEDULE = {
    "darshan_weekday": {
        "recurrence_pattern": "weekdays",
        "times": [("09:30", "13:00"), ("17:30", "20:30")]
    },
    "darshan_weekend": {
        "recurrence_pattern": "weekends",
        "times": [("09:30", "20:30")]
    },
    "aarti": {
        "recurrence_pattern": "daily",
        "times": [("12:15", "12:45"), ("19:00", "19:30")]
    },
    "bhog": {
        "recurrence_pattern": "daily",
        "times": [("11:30", "12:00")]
    },
    "satsang": {
        "recurrence_pattern": "weekly:sunday",
        "times": [("10:30", "12:30")]
    },
    "bhajans": {
        "recurrence_pattern": "daily",
        "times": [("18:00", "19:00")]
    },
    "mahaprasad": {
        "recurrence_pattern": "weekly:sunday",
        "times": [("12:30", "13:30")]
    }
}

# =========================
# EXCEPTIONS
# =========================
EXCEPTIONS = {
    "2026-04-08": {
        "closed": True,
        "reason": "Solar Eclipse — Temple closed for the day",
        "affected_programs": ["darshan", "aarti", "bhog"]
    }
}

# =========================
# HELPERS
# =========================

def to_datetime(time_str: str, base_date: date) -> datetime:
    hour, minute = map(int, time_str.split(":"))
    return datetime(
        base_date.year,
        base_date.month,
        base_date.day,
        hour,
        minute,
        tzinfo=TIMEZONE
    )


def matches_pattern(pattern: str, current_day: int) -> bool:
    if pattern == "daily":
        return True
    if pattern == "weekdays":
        return current_day < 5
    if pattern == "weekends":
        return current_day >= 5
    if pattern.startswith("weekly:"):
        day = pattern.split(":")[1]
        days = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4,
            "saturday": 5, "sunday": 6
        }
        return current_day == days[day]
    return False


def check_exception(check_date: date):
    exception = EXCEPTIONS.get(str(check_date))
    if exception:
        return exception.get("reason")
    return None


def get_program_data(program: str, day: int):
    if program == "darshan":
        return SCHEDULE["darshan_weekday"] if day < 5 else SCHEDULE["darshan_weekend"]
    return SCHEDULE.get(program)

# =========================
# CORE FUNCTIONS
# =========================

def is_happening_now(program: str, now: datetime) -> bool:
    today = now.date()
    day = now.weekday()

    exception = EXCEPTIONS.get(str(today))
    if exception and exception.get("closed"):
        if program in exception.get("affected_programs", []):
            return False

    program_data = get_program_data(program, day)
    if not program_data:
        return False

    if not matches_pattern(program_data["recurrence_pattern"], day):
        return False

    for start, end in program_data["times"]:
        start_dt = to_datetime(start, today)
        end_dt = to_datetime(end, today)

        if start_dt <= now <= end_dt:
            return True

    return False


def get_next_occurrence(program: str, from_time: datetime):
    for i in range(7):
        check_day = from_time + timedelta(days=i)
        day = check_day.weekday()

        program_data = get_program_data(program, day)
        if not program_data:
            continue

        if not matches_pattern(program_data["recurrence_pattern"], day):
            continue

        for start, end in program_data["times"]:
            start_dt = to_datetime(start, check_day.date())
            end_dt = to_datetime(end, check_day.date())

            if start_dt > from_time:
                return {
                    "program": program.capitalize(),
                    "start": start_dt,
                    "end": end_dt,
                    "day": check_day.strftime("%A")
                }

    return None


def get_current_schedule(now: datetime):
    live = []
    upcoming = []

    programs = ["darshan", "aarti", "bhog", "satsang", "bhajans", "mahaprasad"]

    for program in programs:
        if is_happening_now(program, now):
            live.append(program.capitalize())

        next_occ = get_next_occurrence(program, now)
        if next_occ:
            if next_occ["start"] <= now + timedelta(hours=2):
                upcoming.append((program.capitalize(), next_occ["start"]))

    exception_message = check_exception(now.date())

    return {
        "live": live,
        "upcoming": sorted(upcoming, key=lambda x: x[1]),
        "exception": exception_message
    }


def get_full_day_schedule(check_date: date):
    result = []
    day = check_date.weekday()

    programs = ["darshan", "aarti", "bhog", "satsang", "bhajans", "mahaprasad"]

    for program in programs:
        program_data = get_program_data(program, day)
        if not program_data:
            continue

        if not matches_pattern(program_data["recurrence_pattern"], day):
            continue

        for start, end in program_data["times"]:
            result.append({
                "program": program.capitalize(),
                "start": to_datetime(start, check_date),
                "end": to_datetime(end, check_date)
            })

    return sorted(result, key=lambda x: x["start"])


# =========================
# TEST BLOCK
# =========================
if __name__ == "__main__":
    now = datetime.now(TIMEZONE)

    print("\n--- CURRENT SCHEDULE ---")
    print(get_current_schedule(now))

    print("\n--- NEXT AARTI ---")
    print(get_next_occurrence("aarti", now))

    print("\n--- FULL DAY SCHEDULE ---")
    print(get_full_day_schedule(now.date()))
