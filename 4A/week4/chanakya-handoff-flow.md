# JKYog WhatsApp Bot — Voice-to-WhatsApp Handoff Flow
Owner: Chanakya Alluri  
Team: 4A — Conversational UX & Design  
Week: 4 Deliverable  
File: `week4/chanakya-handoff-flow.md`

---

## 1. Purpose

This document defines the **complete voice-to-WhatsApp handoff flow** for the JKYog temple conversational assistant. The goal is to allow users who begin their interaction through a **voice call (IVR or voice bot)** to seamlessly continue the interaction through **WhatsApp chat** when messaging provides a better experience.

Voice interactions are useful for quick questions, but WhatsApp enables richer communication such as:

- Sending links
- Directions and maps
- Structured menus
- Follow-up information
- Multi-step assistance

The handoff flow ensures that users can move from voice to chat **without losing the context of their conversation**.

This document includes:

- Trigger conditions
- Data payload structure
- Context preservation logic
- Session matching logic
- Error handling
- Logging and analytics
- Mermaid sequence diagram

---

## 2. Assumptions

The system is designed with the following assumptions:

- The voice assistant runs through a telephony platform integrated with a conversational AI system.
- The caller's phone number is available through the telephony provider.
- The system integrates with a **WhatsApp Business API provider**.
- A **session store or context store** is available for temporary conversation storage.
- Handoff sessions remain valid for a limited period (typically **30–60 minutes**).
- The WhatsApp bot can retrieve stored sessions using a **phone number, token, or short code**.

---

## 3. System Components

The handoff process involves the following components.

### User
Temple visitor interacting with the system.

### Voice Bot / IVR
Handles incoming calls and determines when to initiate a WhatsApp handoff.

### Handoff Service
Creates a handoff session and packages the conversation context.

### Session Store
Stores temporary conversation context so that it can be restored later.

### WhatsApp API
Sends and receives WhatsApp messages.

### WhatsApp Bot
Resumes the conversation once the user enters the WhatsApp channel.

### Human Support Layer
Handles escalation when a user requests assistance from a volunteer.

---

## 4. Trigger Conditions

A voice-to-WhatsApp handoff should occur when continuing the interaction through chat improves the user experience.

### 4.1 Functional Triggers

Examples include:

- User requests **links**
- User asks for **directions**
- User needs **structured menu options**
- User requires **step-by-step instructions**
- User asks for **documents or receipts**

Example interaction:

User:  
"How do I get to the temple?"

Voice Bot:  
"I can send the directions and parking information to you on WhatsApp."

---

### 4.2 Experience Triggers

These triggers occur when voice becomes inefficient.

Examples:

- Response is too long for voice
- User appears confused
- User repeats questions
- The interaction requires multiple steps

Switching to chat improves clarity.

---

### 4.3 System Triggers

Technical conditions may also initiate a handoff.

Examples:

- Voice session approaching timeout
- Backend systems responding slowly
- Information only available through links

---

### 4.4 User Consent

The system must ask the user for permission before switching channels.

Example prompt:

> “I can continue this conversation on WhatsApp and send the details there. Would you like me to do that?”

The handoff proceeds only if the user agrees.

---

## 5. Handoff Flow Overview

Typical handoff steps:

1. User calls the voice assistant.
2. Voice bot identifies a handoff trigger.
3. Voice bot asks for consent.
4. Handoff service creates a session.
5. Conversation context is stored.
6. User receives a WhatsApp entry point.
7. User opens WhatsApp.
8. WhatsApp bot retrieves the stored session.
9. Conversation continues in chat.

---

## 6. Handoff Modes

### 6.1 Outbound WhatsApp Message

If proactive messaging is allowed:

1. Voice bot confirms the user's phone number.
2. Handoff service creates a session.
3. WhatsApp API sends a message.
4. User responds to the message.
5. WhatsApp bot restores the context.

---

### 6.2 User-Initiated WhatsApp

If proactive messaging is not permitted:

1. Voice bot provides the WhatsApp number or link.
2. User sends a message such as "Hi".
3. WhatsApp bot retrieves the stored session.
4. Conversation resumes.

---

## 7. Data Payload Structure

When the handoff occurs, the system generates a **payload** to preserve the conversation context.

Example payload:

```json
{
  "case_id": "CASE_20260311_00125",
  "handoff_id": "HND_9A72X",
  "channel_from": "voice",
  "channel_to": "whatsapp",
  "user_phone": "+1XXXXXXXXXX",
  "consent_status": true,
  "trigger_reason": "directions_request",
  "last_detected_intent": "temple_directions",
  "intent_confidence": 0.91,
  "conversation_summary": "User asked for temple directions",
  "language": "en",
  "short_code": "4821",
  "session_created_at": "2026-03-11T14:22:18Z",
  "session_expiry_at": "2026-03-11T15:22:18Z"
  }
```

### Important Fields

The following fields are essential for restoring the conversation state:

- `case_id`
- `handoff_id`
- `user_phone`
- `last_detected_intent`
- `conversation_summary`
- `session_timestamps`

These fields allow the WhatsApp bot to correctly restore the conversation state.

---

## 8. Context Preservation Logic

The system must preserve key information when transitioning channels so that the user does not need to repeat their request.

### Context Elements

The following information should be stored:

- detected user intent  
- extracted entities  
- user language preference  
- conversation summary  
- session identifier  
- escalation eligibility  

### Context Restoration

When the user opens WhatsApp:

1. The bot retrieves the session using the phone number or session token.
2. The system loads the stored conversation state.
3. The conversation resumes at the correct step.

### Example

**Voice call**

User:  
“How do I reach the temple?”

**WhatsApp continuation**

> Namaste. Here are the directions and parking details. Would you also like the map link?

---

## 9. Session Matching Logic

Context restoration follows the priority below:

1. Deep-link token  
2. Short code  
3. Phone number match  
4. Recent session lookup  

---

## 10. Error Handling

Robust error handling ensures a smooth user experience even when failures occur.

### Error 1 — Intent Not Understood

**Event Trigger:** `log_intent_fail`

**Voice response**

> “Sorry, I didn’t fully understand that. Are you asking about timings, directions, or donations?”

**WhatsApp response**

> “Please choose one: Timings, Directions, or Donations.”

---

### Error 2 — API Timeout

**Event Trigger:** `log_fallback_timeout`

**Voice response**

> “Our system is taking longer than usual. I can try again or continue on WhatsApp.”

**WhatsApp response**

> “I’m having trouble reaching our system right now. Please try again.”

---

### Error 3 — Confusing User Input

**Event Trigger:** `log_ambiguous_input`

**Voice response**

> “I heard multiple requests. Let’s handle one at a time.”

**WhatsApp response**

> “What would you like first?”

---

### Error 4 — Context Lost

**Event Trigger:** `log_context_loss`

**Voice response**

> “I may have lost our earlier conversation context.”

**WhatsApp response**

> “Please start again or choose an option from the menu.”

---

### Error 5 — Failed Escalation to Human

**Event Trigger:** `log_human_escalation_fail`

**Voice response**

> “A volunteer is not available right now.”

**WhatsApp response**

> “Human support is currently unavailable. I can still help with general questions.”

---

## 11. Logging and Analytics

The following events should be tracked:

- `voice_handoff_offered`
- `voice_handoff_accepted`
- `voice_handoff_declined`
- `voice_handoff_restored`
- `log_intent_fail`
- `log_fallback_timeout`
- `log_context_loss`
- `log_human_escalation_fail`

These metrics help measure:

- system performance  
- handoff success rate  
- fallthrough rate  
- reliability of backend services  
## 12. Conclusion

The voice-to-WhatsApp handoff mechanism enables JKYog temple visitors to smoothly transition from voice interactions to chat-based support. By defining trigger conditions, payload structures, context restoration logic, and error recovery mechanisms, the system ensures a reliable and seamless user experience across communication channels.
