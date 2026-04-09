from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from schedule_data import SCHEDULE

TIMEZONE = ZoneInfo("America/Chicago")

with open("schedule_exceptions.json") as f:
    EXCEPTIONS = json.load(f)


def is_exception(program_name, now):
    date_str = now.strftime("%Y-%m-%d")
    if date_str in EXCEPTIONS:
        if EXCEPTIONS[date_str].get("global_closed"):
            return True
        return program_name in EXCEPTIONS[date_str].get("closed", [])
    return False


def is_happening_now(program, now):
    if is_exception(program["name"], now):
        return False

    weekday = now.strftime("%A")
    current_time = now.time()

    # Window-based programs
    if program["type"] == "window":
        if "days" in program and weekday not in program["days"]:
            return False

        schedule = program["schedule"]

        if isinstance(schedule, dict):
            schedule = schedule["weekend"] if weekday in ["Saturday", "Sunday"] else schedule["weekday"]

        for start, end in schedule:
            if start <= current_time <= end:
                return True

    # Fixed-time programs
    if program["type"] == "fixed":
        duration = program.get("duration_minutes", 30)

        for t in program["times"]:
            start_dt = datetime.combine(now.date(), t, tzinfo=TIMEZONE)
            end_dt = start_dt + timedelta(minutes=duration)

            if start_dt <= now <= end_dt:
                return True

    return False


def get_next_occurrence(program, from_time):
    for day_offset in range(7):
        check_date = from_time + timedelta(days=day_offset)
        weekday = check_date.strftime("%A")

        if is_exception(program["name"], check_date):
            continue

        if program["type"] == "window":
            if "days" in program and weekday not in program["days"]:
                continue

            schedule = program["schedule"]

            if isinstance(schedule, dict):
                schedule = schedule["weekend"] if weekday in ["Saturday", "Sunday"] else schedule["weekday"]

            for start, _ in schedule:
                dt = datetime.combine(check_date.date(), start, tzinfo=TIMEZONE)
                if dt > from_time:
                    return dt

        if program["type"] == "fixed":
            for t in program["times"]:
                dt = datetime.combine(check_date.date(), t, tzinfo=TIMEZONE)
                if dt > from_time:
                    return dt

    return None


def get_current_schedule(now):
    live = []
    upcoming = []

    for program in SCHEDULE:
        if is_happening_now(program, now):
            live.append(program["name"])
        else:
            next_time = get_next_occurrence(program, now)
            if next_time:
                diff = (next_time - now).total_seconds()
                if diff <= 7200:
                    upcoming.append((program["name"], next_time))

    upcoming.sort(key=lambda x: x[1])

    return {
        "live": live,
        "upcoming": upcoming
    }


def get_full_day_schedule(date):
    result = []

    for program in SCHEDULE:
        if is_exception(program["name"], date):
            continue

        weekday = date.strftime("%A")

        if program["type"] == "window":
            if "days" in program and weekday not in program["days"]:
                continue

            schedule = program["schedule"]

            if isinstance(schedule, dict):
                schedule = schedule["weekend"] if weekday in ["Saturday", "Sunday"] else schedule["weekday"]

            for start, end in schedule:
                result.append({
                    "name": program["name"],
                    "start": start.strftime("%H:%M"),
                    "end": end.strftime("%H:%M")
                })

        if program["type"] == "fixed":
            for t in program["times"]:
                result.append({
                    "name": program["name"],
                    "time": t.strftime("%H:%M")
                })

    return sorted(result, key=lambda x: x.get("start", x.get("time")))
