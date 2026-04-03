# Event Query Intent Design  
**Rujul Shukla**  

## Overview  
This document outlines event-related user intents, conversation flows, edge cases, and clarification strategies for a conversational event assistant.

---

# 1. Event-Related User Intents (8)

## 1. Time-Based Intent  
**User:** “What events are happening this weekend?”

```mermaid
flowchart TD
A[User asks for events by time] --> B[Identify time range]
B --> C[Search events within range]
C --> D{Events found?}
D -->|Yes| E[Sort by date/time]
E --> F[Return list with key details]
D -->|No| G[Expand search slightly]
G --> H{Alternatives found?}
H -->|Yes| I[Suggest nearby events]
H -->|No| J[Return no events message]
```

---

## 2. Event-Specific Intent  
**User:** “Tell me about Holi Festival”

```mermaid
flowchart TD
A[User asks about specific event] --> B[Identify event name]
B --> C[Search for event]
C --> D{Match found?}
D -->|Exact| E[Return full event details]
D -->|Partial| F[Show closest matches]
F --> G[Ask user to confirm]
D -->|None| H[Suggest similar events]
```

---

## 3. Recurring Schedule Intent  
**User:** “When is yoga class?”

```mermaid
flowchart TD
A[User asks about recurring event] --> B[Identify event type]
B --> C[Find recurring schedule]
C --> D[Determine next occurrence]
D --> E[Return next date + frequency]
```

---

## 4. Logistics / Parking Intent  
**User:** “Where do I park for the event?”

```mermaid
flowchart TD
A[User asks logistics question] --> B[Check if event specified]
B --> C{Event provided?}
C -->|Yes| D[Retrieve logistics info]
C -->|No| E[Ask for clarification]
D --> F[Return parking + directions]
```

---

## 5. Sponsorship / Donation Intent  
**User:** “How can I sponsor an event?”

```mermaid
flowchart TD
A[User asks about sponsorship] --> B[Check if event-specific]
B --> C{Specific event?}
C -->|Yes| D[Provide event options]
C -->|No| E[Provide general options]
D --> F[Return next steps]
E --> F
```

---

## 6. Discovery Intent  
**User:** “What fun events are happening?”

```mermaid
flowchart TD
A[User asks for recommendations] --> B[Classify as discovery]
B --> C[Select popular/upcoming events]
C --> D[Optional filtering]
D --> E[Return curated list]
```

---

## 7. Ambiguous Intent  
**User:** “What’s happening?”

```mermaid
flowchart TD
A[User gives vague query] --> B[Ask clarifying question]
B --> C{User response}
C -->|Time| D[Filter by date]
C -->|Type| E[Filter by category]
C -->|Location| F[Filter by place]
D --> G[Return results]
E --> G
F --> G
```

---

## 8. No-Results Intent  
**User:** “Events at 3 AM tonight?”

```mermaid
flowchart TD
A[User query] --> B[Search events]
B --> C{Results found?}
C -->|No| D[Suggest nearby times]
D --> E[Offer similar categories]
C -->|Yes| F[Return events]
```

---

# 2. Edge Cases (5)

## 9. Multi-Day Events  
**User:** “What’s happening during the retreat?”

```mermaid
flowchart TD
A[User asks about multi-day event] --> B[Identify duration]
B --> C[Retrieve schedule]
C --> D[Break into days]
D --> E[Return structured itinerary]
```

---

## 10. Overlapping Events  
**User:** “What’s happening Friday evening?”

```mermaid
flowchart TD
A[User asks for time slot] --> B[Search events]
B --> C{Multiple events?}
C -->|Yes| D[Display all options clearly]
C -->|No| E[Return single event]
```

---

## 11. Past Events  
**User:** “What happened last weekend?”

```mermaid
flowchart TD
A[User asks about past events] --> B[Identify timeframe]
B --> C[Retrieve past events]
C --> D[Return summary]
```

---

## 12. Cross-Source Events  
**User:** “Show events from all platforms”

```mermaid
flowchart TD
A[User query] --> B[Fetch from multiple sources]
B --> C[Merge results]
C --> D[Remove duplicates]
D --> E[Return unified list]
```

---

## 13. Event Not Found  
**User:** “Is there a Diwali Gala today?”

```mermaid
flowchart TD
A[User asks for event] --> B[Search database]
B --> C{Event found?}
C -->|No| D[Suggest similar events]
D --> E[Ask clarification]
C -->|Yes| F[Return details]
```

---

# 3. Clarification Flows

## Vague Query Handling  
**User:** “What’s going on?”

```mermaid
flowchart TD
A[User vague query] --> B[Ask: When are you interested?]
B --> C{User response}
C -->|Time| D[Filter by date]
C -->|Category| E[Filter by type]
C -->|Location| F[Filter by place]
D --> G[Return events]
E --> G
F --> G
```

---

## Multi-Step Clarification  
**User:** “Any events?”

```mermaid
flowchart TD
A[User vague query] --> B[Ask for time]
B --> C[User provides time]
C --> D[Ask for type]
D --> E[User provides type]
E --> F[Return filtered events]
```

---

# Summary  
This design:
- Covers diverse real-world intents  
- Handles ambiguity and edge cases effectively  
- Keeps flows simple, structured, and implementable  
