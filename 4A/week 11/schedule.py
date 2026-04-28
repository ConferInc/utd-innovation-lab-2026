from datetime import datetime
from zoneinfo import ZoneInfo
from schedule_data import SCHEDULE
import json

# Load exceptions
with open("schedule_exceptions.json", "r") as f:
    EXCEPTIONS = json.load(f)

TIMEZONE = ZoneInfo("America/Chicago")


def is_happening_now(program, now=None):
    if not now:
        now = datetime.now(TIMEZONE)

    today = now.strftime("%Y-%m-%d")
    current_time = now.time()
    weekday = now.strftime("%A")

    # Check exceptions
    if today in EXCEPTIONS:
        if program in EXCEPTIONS[today].get("closed", []):
            return False

    details = SCHEDULE.get(program)

    if not details:
        return False

    # Daily ranges
    if "daily" in details:
        for entry in details["daily"]:
            if isinstance(entry, tuple):
                if entry[0] <= current_time <= entry[1]:
                    return True
            else:
                if current_time.hour == entry.hour and current_time.minute == entry.minute:
                    return True

    # Weekly
    if "weekly" in details:
        if weekday in details["weekly"]:
            entry = details["weekly"][weekday]
            if isinstance(entry, tuple):
                return entry[0] <= current_time <= entry[1]
            else:
                return current_time.hour == entry.hour and current_time.minute == entry.minute

    return False


def get_current_schedule(now=None):
    if not now:
        now = datetime.now(TIMEZONE)

    active = []

    for program in SCHEDULE:
        if is_happening_now(program, now):
            active.append(program)

    return active
