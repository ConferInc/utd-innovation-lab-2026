# JKYog WhatsApp Bot Voice to WhatsApp
Owner: Chanakya Alluri  
Due: March 6, 2026 (11:59 PM CST)

## Purpose
These scripts handle:
1) Transition from a **voice call** (IVR/voice bot) into **WhatsApp chat** with the JKYog bot  
2) Five **error/fallback scenarios** (user-safe messaging + recovery prompts)

Tone: respectful, calm, devotional-friendly, minimal friction.

---

# Five Error / Fallback Scenarios (User Messages + Recovery)

## Error 1: Intent Not Understood

**Event Trigger:** `log_intent_fail`

**Description:**  
Triggered when the user input cannot be confidently mapped to any supported intent (timings, directions, donations).

**VOICE**
> “Sorry, I didn’t fully understand that.  
Are you asking about **timings/events**, **directions**, or **donations**?”

**WhatsApp**
> “Sorry—I may have missed that. 🙏  
Please choose one:  
1) Timings & events  
2) Directions & parking  
3) Donations & receipts  
Or type **Menu**.”

**Recovery Logic**
- Retry intent classification once
- Log event `log_intent_fail`
- Offer example prompts if still unclear

---

## Error 2: API Timeout

**Event Trigger:** `log_fallback_timeout`

**Description:**  
Triggered when backend services such as Maps API, CRM, or donation systems fail to respond within the expected time.

**VOICE**
> “One moment—our system is taking longer than usual.  
I can try again, or continue on WhatsApp for faster help.”

**WhatsApp**
> “I’m having trouble reaching our system right now. 🙏  
Please try again in a moment.  
Type **Retry**, **Menu**, or **Human**.”

**Recovery Logic**
- Retry request once after delay
- If timeout persists → escalate to fallback
- Log `log_fallback_timeout`

---

## Error 3: Confusing User Input

**Event Trigger:** `log_ambiguous_input`

**Description:**  
Occurs when the user message contains multiple intents or unclear phrasing.

Example:  
“Parking tomorrow donation receipt”

**VOICE**
> “I heard a few things together. Let’s do one at a time.  
What would you like first: **directions**, **timings**, or **donations**?”

**WhatsApp**
> “There are a few things in your message. 🙏  
What should we do first?  
1) Timings/events  
2) Directions/parking  
3) Donations/receipt”

**Recovery Logic**
- Ask user to choose one clear option
- Log event `log_ambiguous_input`

---

## Error 4: Context Lost

**Event Trigger:** `log_context_loss`

**Description:**  
Triggered when the conversation session resets or the system loses conversation state.

**VOICE**
> “Welcome back. I may have lost our earlier context.  
Please tell me what you need now: timings, directions, or donations.”

**WhatsApp**
> “Welcome back 🙏 I may have lost the last step.  
Please type:  
Timings  
Directions  
Donations  
Or type **Start** to begin again.”

**Recovery Logic**
- Reset conversation state
- Provide restart option
- Log event `log_context_loss`

---

## Error 5: Failed Escalation to Human

**Event Trigger:** `log_human_escalation_fail`

**Description:**  
Triggered when the system attempts to transfer the conversation to a volunteer but no agent is available.

**VOICE**
> “I’m sorry—no volunteer is available right now.  
I can still help here, or you can try again during {HOURS}.”

**WhatsApp**
> “Our volunteer team isn’t available right now. 🙏  
Meanwhile, choose:  
1) Timings/events  
2) Directions/parking  
3) Donations/receipt  
Or type **Leave a message**.”

**Recovery Logic**
- Offer async message capture
- Provide fallback menu
- Log event `log_human_escalation_fail`

---

# Analytics Note

These **event triggers** allow the analytics system to measure key performance metrics such as:

- Fallthrough Rate
- Intent Recognition Failures
- Backend Reliability
- Conversation Recovery Success
- Human Escalation Availability

Each trigger should be logged in the system telemetry layer whenever the corresponding fallback path is executed.
