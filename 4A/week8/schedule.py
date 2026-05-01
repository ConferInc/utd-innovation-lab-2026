from datetime import datetime
from zoneinfo import ZoneInfo
from recurring_handler import get_current_schedule



TIMEZONE = ZoneInfo("America/Chicago")





def handle_recurring_schedule():
    now = datetime.now(TIMEZONE)
    schedule = get_current_schedule(now)



    response = "Here’s what’s happening at the temple right now:\n\n"



    if schedule["live"]:
        response += "🔴 Live Now:\n"
        for item in schedule["live"]:
            response += f"• {item}\n"
        response += "\n"
    else:
        response += "No programs are live right now.\n\n"



    if schedule["upcoming"]:
        response += "🕒 Starting Soon:\n"
        for name, time in schedule["upcoming"]:
            response += f"• {name} at {time.strftime('%I:%M %p')}\n"
    else:
        response += "No programs starting in the next 2 hours.\n"



    return response



