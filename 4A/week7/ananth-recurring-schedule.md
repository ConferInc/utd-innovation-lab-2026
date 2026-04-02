# Ananth Subramaniam Vangala | Recurring Schedule Model & "What’s Happening Now?" Logic

## Overview
This module powers time-based queries by determining **what is happening now** and **what event is next**, using recurring schedules, real-time inputs, and exception handling.

---

## 1. Recurring Schedule Data Model

```json
[
  {
    "name": "Darshan",
    "type": "daily",
    "schedule": {
      "weekday": [["09:30", "13:00"], ["17:30", "20:30"]],
      "weekend": [["09:30", "20:30"]]
    },
    "exceptions": {}
  },
  {
    "name": "Aarti",
    "type": "daily",
    "times": ["12:15", "19:00"],
    "exceptions": {}
  },
  {
    "name": "Bhajans",
    "type": "daily",
    "start": "19:00",
    "end": "20:00",
    "exceptions": {}
  },
  {
    "name": "Sunday Satsang",
    "type": "weekly",
    "days": ["Sunday"],
    "start": "10:30",
    "end": "12:30",
    "exceptions": {}
  }
]
```

---

## 2. Decision Logic (Now & Next)

This module determines **what is happening now** and **what event is next** based on real-time inputs.

### Logic Steps
- Get current time and day  
- Select applicable schedule (weekday/weekend)  
- Check if current time falls within any event range → mark as **NOW**  
- Identify the next upcoming event based on time  

### Pseudocode

```
current_time = getCurrentTime()
current_day = getCurrentDay()

events_today = filterEventsByDay(schedule, current_day)

current_event = null
next_event = null

for event in events_today:
    for time_range in event.time_ranges:
        if current_time within time_range:
            current_event = event

future_events = sortEventsAfter(current_time)

if future_events not empty:
    next_event = future_events[0]
```

---

## 3. Exception Handling

This module supports dynamic overrides for special conditions.

### Examples
- Temple closures  
- Festivals  
- Eclipses  

### Example Exception

```json
"exceptions": {
  "2026-04-08": {
    "closed": true,
    "reason": "Solar Eclipse"
  }
}
```

### Behavior
- Overrides default schedule  
- Prevents incorrect responses  
- Returns user-friendly messages  

---

## 4. Time Zone Handling

- Supports CST/CDT transitions  
- Uses system-local timezone for accurate calculations  
- Ensures consistency across all time-based queries  

---

## 5. Natural Language Time Interpretation

The system interprets user-friendly time expressions:

- "this morning" → 6:00 AM – 12:00 PM  
- "this evening" → 5:00 PM – 8:00 PM  
- "tonight" → 8:00 PM – 11:59 PM  
- "later today" → current time to end of day  

---

## 6. Example

**Input:**  
What’s happening now?

**Output:**  
- Current Event: Darshan (9:30 AM – 1:00 PM)  
- Next Event: Aarti (12:15 PM)  

---

## 7. Why This Matters

This logic enables real-time, context-aware responses, improving user experience and reducing ambiguity in schedule-based queries.
