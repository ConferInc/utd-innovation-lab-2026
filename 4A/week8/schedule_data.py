from datetime import time

SCHEDULE = {
    "Darshan": {
        "weekday": [
            (time(9, 30), time(13, 0)),
            (time(17, 30), time(20, 30))
        ],
        "weekend": [
            (time(9, 30), time(20, 30))
        ]
    },
    "Aarti": {
        "daily": [
            time(12, 15),
            time(19, 0)
        ]
    },
    "Bhajans": {
        "daily": [
            (time(19, 0), time(20, 0))
        ]
    },
    "Sunday Satsang": {
        "weekly": {
            "Sunday": (time(10, 30), time(12, 30))
        }
    },
    "Mahaprasad": {
        "weekly": {
            "Friday": time(19, 30),
            "Sunday": time(13, 0)
        }
    }
}
