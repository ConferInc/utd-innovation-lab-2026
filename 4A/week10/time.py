

from datetime import time



SCHEDULE = [
    {
        "name": "Darshan",
        "type": "window",
        "schedule": {
            "weekday": [(time(9, 30), time(13, 0)), (time(17, 30), time(20, 30))],
            "weekend": [(time(9, 30), time(20, 30))]
        }
    },
    {
        "name": "Aarti",
        "type": "fixed",
        "times": [time(12, 15), time(19, 0)],
        "duration_minutes": 30
    },
    {
        "name": "Bhog",
        "type": "fixed",
        "times": [time(11, 30)],
        "duration_minutes": 30
    },
    {
        "name": "Sunday Satsang",
        "type": "window",
        "days": ["Sunday"],
        "schedule": [(time(10, 30), time(12, 30))]
    },
    {
        "name": "Daily Bhajans",
        "type": "window",
        "schedule": [(time(19, 0), time(20, 0))]
    },
    {
        "name": "Mahaprasad",
        "type": "window",
        "days": ["Sunday"],
        "schedule": [(time(12, 30), time(14, 0))]
    }
]
