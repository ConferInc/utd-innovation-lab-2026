## Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant VoiceBot
    participant HandoffService
    participant SessionStore
    participant WhatsAppAPI
    participant WhatsAppBot

    User->>VoiceBot: Calls temple assistant
    VoiceBot->>User: Greets user and asks for request
    User->>VoiceBot: Requests directions

    VoiceBot->>User: Offers WhatsApp continuation
    User->>VoiceBot: Accepts handoff

    VoiceBot->>HandoffService: Create handoff session
    HandoffService->>SessionStore: Store context payload
    SessionStore-->>HandoffService: Return session ID

    HandoffService->>WhatsAppAPI: Send WhatsApp message
    WhatsAppAPI-->>User: Deliver WhatsApp message

    User->>WhatsAppBot: Sends "Hi"
    WhatsAppBot->>SessionStore: Retrieve stored context
    SessionStore-->>WhatsAppBot: Return session context

    WhatsAppBot->>User: Resume conversation with context
