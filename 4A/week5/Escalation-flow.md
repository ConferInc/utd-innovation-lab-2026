# Week 5 Task Submission — Chanakya Alluri

## Task
**Bot-to-Human Escalation Flow**

## Deliverables
- JSON flow definition
- Mermaid sequence diagram (**371 lines**, satisfying the **361+ line** requirement)

## Working Assumptions
- Shared bearer token is used for backend-to-backend authentication.
- Payload and response fields follow the Team 4B expectations shared during coordination.
- Exact endpoint names, enum values, and timeout values are treated as working assumptions where Team 4B has not yet finalized the API contract.

---

## 1) JSON Flow Definition

```json
{
  "task": {
    "week": 5,
    "owner": "Chanakya Alluri",
    "deliverable": "Bot-to-Human Escalation Flow",
    "version": "v1.0-working-assumption"
  },
  "objective": "Escalate from bot to human volunteer when trigger conditions are met, keep the user informed while queued, support active handoff, and safely return the conversation to the bot.",
  "integration_contract": {
    "auth_method": "Shared bearer token for backend-to-backend authentication",
    "request_endpoint": "/escalations",
    "request_method": "POST",
    "request_content_type": "application/json",
    "response_content_type": "application/json"
  },
  "working_assumptions": [
    "Exact endpoint URL and enum names were not formally confirmed by Team 4B, so reasonable placeholder values are used here.",
    "The bot owns trigger detection, payload assembly, user-facing waiting messages, and return-to-bot state restoration.",
    "The escalation service owns ticket creation, queue placement, volunteer assignment, and response metadata.",
    "Sensitive or profanity cases are treated as higher priority than repeated fallback cases.",
    "A cancelled or disconnected session may be returned to the bot without deleting the historical ticket record."
  ],
  "actors": {
    "user": "End user asking for support",
    "bot_orchestrator": "Primary bot controller that evaluates escalation rules and manages state",
    "intent_classifier": "Intent and confidence detector",
    "safety_filter": "Sensitive/profanity detection layer",
    "session_store": "Conversation memory and state store",
    "escalation_api": "Team 4B handoff API",
    "ticket_service": "Stores escalation tickets and audit trail",
    "volunteer_queue": "Queue for waiting tickets",
    "volunteer_router": "Finds the best available volunteer",
    "volunteer_portal": "Human-facing interface used during the handoff",
    "notification_service": "Sends waiting, assignment, and return-to-bot updates"
  },
  "trigger_conditions": [
    {
      "id": "TRIGGER_EXPLICIT_HUMAN_REQUEST",
      "condition": "User explicitly asks to talk to a human",
      "examples": [
        "talk to a human",
        "connect me to a person",
        "I want an agent"
      ],
      "priority": "high",
      "escalation_reason": "user_requested_human"
    },
    {
      "id": "TRIGGER_REPEATED_FALLBACK",
      "condition": "3 or more failed or fallback intents in the same session",
      "threshold": 3,
      "priority": "medium",
      "escalation_reason": "repeated_fallback"
    },
    {
      "id": "TRIGGER_SENSITIVE_OR_PROFANITY",
      "condition": "Sensitive, abusive, or profanity-heavy case flagged by the safety layer",
      "priority": "urgent",
      "escalation_reason": "sensitive_or_profanity"
    }
  ],
  "request_payload": {
    "required_fields": {
      "user_id": "string|null",
      "phone": "string|null",
      "conversation_id": "string",
      "session_id": "string",
      "latest_user_message": "string",
      "short_transcript": "string",
      "detected_intent": "string",
      "escalation_reason": "string",
      "timestamp": "ISO-8601 string"
    },
    "optional_fields": {
      "user_name": "string|null",
      "fallback_count": "integer",
      "safety_flags": [
        "string"
      ],
      "priority": "urgent|high|medium|low",
      "channel": "whatsapp|web|voice|other",
      "locale": "string"
    },
    "validation_rules": [
      "At least one of user_id or phone should be present.",
      "conversation_id, session_id, latest_user_message, short_transcript, detected_intent, escalation_reason, and timestamp are mandatory.",
      "timestamp should be recorded by the bot in ISO-8601 format.",
      "short_transcript should summarize recent context rather than contain the full raw transcript."
    ]
  },
  "response_payload": {
    "required_fields": {
      "success": "boolean",
      "ticket_id": "string|null",
      "queue_status": "queued|assigned|waiting|failed|closed|cancelled",
      "assigned_volunteer": "string|null",
      "next_state": "WAITING_FOR_VOLUNTEER|ACTIVE_HANDOFF|BOT_ACTIVE|ESCALATION_FAILED|RETURNING_TO_BOT",
      "message_for_user": "string"
    },
    "recommended_extensions": {
      "estimated_wait_seconds": "integer|null",
      "priority": "urgent|high|medium|low",
      "errors": [
        "string"
      ]
    }
  },
  "state_machine": [
    {
      "state": "BOT_ACTIVE",
      "description": "Normal automated bot operation",
      "on_enter": [
        "Read session context",
        "Classify intent",
        "Run safety checks",
        "Evaluate escalation rules"
      ],
      "transitions": [
        {
          "event": "EXPLICIT_HUMAN_REQUEST",
          "target_state": "ESCALATION_REQUESTED"
        },
        {
          "event": "FALLBACK_THRESHOLD_REACHED",
          "target_state": "ESCALATION_REQUESTED"
        },
        {
          "event": "SENSITIVE_CASE_DETECTED",
          "target_state": "ESCALATION_REQUESTED"
        },
        {
          "event": "NO_TRIGGER",
          "target_state": "BOT_ACTIVE"
        }
      ]
    },
    {
      "state": "ESCALATION_REQUESTED",
      "description": "Bot has decided to escalate and prepares the contract payload",
      "on_enter": [
        "Capture reason",
        "Capture latest user message",
        "Fetch transcript summary",
        "Set temporary next_state"
      ],
      "transitions": [
        {
          "event": "AUTH_OR_VALIDATION_FAILURE",
          "target_state": "ESCALATION_FAILED"
        },
        {
          "event": "TICKET_CREATED_AND_QUEUED",
          "target_state": "WAITING_FOR_VOLUNTEER"
        },
        {
          "event": "TICKET_CREATED_AND_ASSIGNED",
          "target_state": "ACTIVE_HANDOFF"
        }
      ]
    },
    {
      "state": "WAITING_FOR_VOLUNTEER",
      "description": "Ticket exists and the user is waiting in queue",
      "on_enter": [
        "Store ticket_id",
        "Store queue_status",
        "Send waiting message",
        "Start queue timer"
      ],
      "transitions": [
        {
          "event": "VOLUNTEER_ASSIGNED",
          "target_state": "ACTIVE_HANDOFF"
        },
        {
          "event": "USER_CANCELLED",
          "target_state": "BOT_ACTIVE"
        },
        {
          "event": "QUEUE_FAILED",
          "target_state": "ESCALATION_FAILED"
        }
      ]
    },
    {
      "state": "ACTIVE_HANDOFF",
      "description": "A human volunteer is actively handling the conversation",
      "on_enter": [
        "Lock bot takeover",
        "Sync handoff transcript",
        "Expose summary to volunteer"
      ],
      "transitions": [
        {
          "event": "VOLUNTEER_RESOLVED",
          "target_state": "RETURNING_TO_BOT"
        },
        {
          "event": "VOLUNTEER_PARTIAL",
          "target_state": "RETURNING_TO_BOT"
        },
        {
          "event": "VOLUNTEER_DISCONNECTED",
          "target_state": "WAITING_FOR_VOLUNTEER"
        },
        {
          "event": "USER_DISCONNECTED",
          "target_state": "BOT_ACTIVE"
        },
        {
          "event": "SUPERVISOR_OR_SPECIALIST_NEEDED",
          "target_state": "WAITING_FOR_VOLUNTEER"
        }
      ]
    },
    {
      "state": "RETURNING_TO_BOT",
      "description": "Human conversation has ended and control is being restored to the bot",
      "on_enter": [
        "Save resolution summary",
        "Reset fallback counter",
        "Clear volunteer linkage",
        "Preserve ticket history"
      ],
      "transitions": [
        {
          "event": "RETURN_COMPLETE",
          "target_state": "BOT_ACTIVE"
        }
      ]
    },
    {
      "state": "ESCALATION_FAILED",
      "description": "Escalation could not be completed due to auth, payload, or routing failure",
      "on_enter": [
        "Log failure",
        "Keep audit trail",
        "Offer graceful fallback or retry path"
      ],
      "transitions": [
        {
          "event": "USER_RETRIES",
          "target_state": "ESCALATION_REQUESTED"
        },
        {
          "event": "USER_CONTINUES_WITH_BOT",
          "target_state": "BOT_ACTIVE"
        }
      ]
    }
  ],
  "queue_rules": {
    "priority_order": [
      "urgent",
      "high",
      "medium",
      "low"
    ],
    "assignment_logic": [
      "Prefer volunteers already marked available.",
      "Prefer skill match when a skill tag exists.",
      "Prefer lower active load when multiple volunteers qualify.",
      "Allow immediate assignment or queued assignment."
    ],
    "user_updates": [
      "Send one acknowledgement when ticket is created.",
      "Send a second message when a volunteer is assigned.",
      "Send occasional waiting updates without spamming the user."
    ]
  },
  "handoff_rules": {
    "during_handoff": [
      "Volunteer sees latest_user_message, detected_intent, escalation_reason, transcript summary, and prior bot attempts.",
      "Bot should not interrupt an active volunteer session.",
      "Bot may provide summary context to the volunteer if requested, without taking control back automatically.",
      "All volunteer messages should be mirrored into the ticket or transcript store for continuity."
    ],
    "end_of_handoff": [
      "Volunteer marks resolved, partial, cancelled, or supervisor_needed.",
      "A resolution summary should be saved before returning the conversation to the bot.",
      "The fallback counter should be reset on successful or partial return to avoid immediate re-escalation.",
      "The ticket remains available for audit even after the bot resumes."
    ]
  },
  "return_to_bot_rules": {
    "cleanup": [
      "Clear assigned volunteer reference",
      "Archive queue_status",
      "Reset transient escalation flags",
      "Keep resolution summary for continuity"
    ],
    "bot_resume_message": "The bot should acknowledge the handoff completion and offer the next automated step instead of restarting the conversation from scratch."
  },
  "error_handling": [
    {
      "case": "invalid_or_missing_bearer_token",
      "system_action": [
        "Reject request",
        "Log auth failure",
        "Keep user in graceful fallback path"
      ],
      "user_message_goal": "Explain that human handoff is temporarily unavailable and offer retry"
    },
    {
      "case": "payload_validation_failure",
      "system_action": [
        "Return validation error",
        "Log missing fields",
        "Allow bot-side retry after correction"
      ],
      "user_message_goal": "Inform user there was a handoff problem without exposing internal details"
    },
    {
      "case": "no_volunteer_available",
      "system_action": [
        "Keep ticket queued",
        "Start wait timer",
        "Send queue updates"
      ],
      "user_message_goal": "Confirm the user is still in line and that someone will join when available"
    },
    {
      "case": "volunteer_disconnect",
      "system_action": [
        "Mark interrupted",
        "Requeue or replace",
        "Notify user"
      ],
      "user_message_goal": "Tell the user a replacement is being connected"
    },
    {
      "case": "user_disconnect_or_cancel",
      "system_action": [
        "Close or pause ticket",
        "Return conversation to bot state",
        "Keep history for audit"
      ],
      "user_message_goal": "Confirm cancellation or safe closure"
    }
  ],
  "audit_fields": [
    "ticket_id",
    "conversation_id",
    "session_id",
    "user_id_or_phone",
    "escalation_reason",
    "priority",
    "queue_status",
    "assigned_volunteer",
    "trigger_source",
    "handoff_started_at",
    "handoff_ended_at",
    "return_to_bot_at",
    "final_state"
  ]
}
```

---

## 2) Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant CH as Client Channel
    participant BOT as Bot Orchestrator
    participant NLP as Intent Classifier
    participant SAF as Safety Filter
    participant SES as Session Store
    participant ESC as Escalation API
    participant AUT as Auth Validator
    participant TKT as Ticket Service
    participant QUE as Volunteer Queue
    participant ROT as Volunteer Router
    participant VOL as Volunteer Portal
    participant NOT as Notification Service
    %% Intake
    U->>CH: Send latest message
    CH->>BOT: Forward user message
    BOT->>SES: Read session context
    SES-->>BOT: Return session_id, conversation_id, fallback_count
    BOT->>NLP: Detect intent
    NLP-->>BOT: Return detected_intent, confidence
    BOT->>SAF: Scan content for sensitive or profanity signals
    SAF-->>BOT: Return safety flags
    BOT->>BOT: Evaluate escalation rules
    Note right of BOT: Rule 1 = explicit request for human
    Note right of BOT: Rule 2 = fallback_count >= 3
    Note right of BOT: Rule 3 = sensitive or profanity case
    alt Explicit human request detected
        BOT->>SES: Store escalation_reason = user_requested_human
        BOT->>SES: Store escalation_source = explicit_request
        BOT->>SES: Store escalation_priority = high
        BOT->>SES: Store detected_intent
        BOT->>SES: Store latest_user_message
        SES-->>BOT: Session updated
        BOT->>BOT: Set should_escalate = true
        BOT->>BOT: Set next_state = WAITING_FOR_VOLUNTEER
        Note right of BOT: User explicitly asked to talk to a human
        Note right of BOT: Bot should not continue normal automation
        Note right of BOT: Bot prepares escalation payload immediately
    else Fallback threshold reached
        BOT->>SES: Increment fallback counter
        BOT->>SES: Store escalation_reason = repeated_fallback
        BOT->>SES: Store escalation_source = fallback_threshold
        BOT->>SES: Store escalation_priority = medium
        BOT->>SES: Store detected_intent = unknown_or_low_confidence
        BOT->>SES: Store latest_user_message
        SES-->>BOT: Session updated
        BOT->>BOT: Set should_escalate = true
        BOT->>BOT: Set next_state = WAITING_FOR_VOLUNTEER
        Note right of BOT: Trigger occurs after 3 or more failed intents
        Note right of BOT: This prevents endless fallback loops
        Note right of BOT: The transcript summary is attached for context
    else Sensitive or profanity case detected
        BOT->>SES: Store escalation_reason = sensitive_or_profanity
        BOT->>SES: Store escalation_source = safety_layer
        BOT->>SES: Store escalation_priority = urgent
        BOT->>SES: Store detected_intent
        BOT->>SES: Store latest_user_message
        BOT->>SES: Store safety_flags
        SES-->>BOT: Session updated
        BOT->>BOT: Set should_escalate = true
        BOT->>BOT: Set next_state = WAITING_FOR_VOLUNTEER
        Note right of BOT: Safety-sensitive cases bypass standard retry loops
        Note right of BOT: Bot can send a calm holding response
        Note right of BOT: Urgent cases go to the front of the queue
    else No escalation trigger
        BOT->>BOT: Set should_escalate = false
        BOT->>BOT: Set next_state = BOT_ACTIVE
        BOT->>SES: Reset transient escalation candidate flags
        SES-->>BOT: Session updated
        BOT-->>CH: Send normal bot response
        CH-->>U: Deliver automated reply
        Note right of BOT: Normal automation continues here
    end
    alt should_escalate = true
        BOT-->>CH: Tell user a human handoff is starting
        CH-->>U: Display waiting message
        BOT->>SES: Fetch short transcript summary
        SES-->>BOT: Return short transcript and metadata
        BOT->>ESC: POST /escalations with bearer token
        activate ESC
        ESC->>AUT: Validate shared bearer token
        AUT-->>ESC: Auth result
        alt Token invalid or missing
            ESC-->>BOT: 401 unauthorized
            BOT->>SES: Store escalation_status = auth_failed
            BOT->>SES: Store next_state = ESCALATION_FAILED
            SES-->>BOT: Session updated
            BOT-->>CH: Apologize and ask user to retry shortly
            CH-->>U: Deliver failure notice
            Note right of ESC: Escalation request is rejected before ticket creation
        else Token valid
            ESC->>ESC: Parse payload
            ESC->>ESC: Validate required fields
            Note right of ESC: Required fields come from Team 4B contract
            Note right of ESC: user_id or phone must be present
            Note right of ESC: conversation_id and session_id must be present
            Note right of ESC: latest_user_message must be present
            alt Payload invalid
                ESC-->>BOT: 400 bad_request with validation errors
                BOT->>SES: Store escalation_status = payload_failed
                BOT->>SES: Store next_state = ESCALATION_FAILED
                BOT->>SES: Store validation_errors
                SES-->>BOT: Session updated
                BOT-->>CH: Send fallback message and retry option
                CH-->>U: Deliver retry prompt
                Note right of BOT: Bot may reformat payload and retry once
            else Payload valid
                ESC->>TKT: Create escalation ticket
                TKT->>TKT: Generate ticket_id
                TKT->>TKT: Persist escalation payload
                TKT->>TKT: Persist escalation_reason
                TKT->>TKT: Persist detected_intent
                TKT->>TKT: Persist transcript summary
                TKT->>TKT: Persist timestamp
                TKT-->>ESC: ticket_id created
                ESC->>QUE: Enqueue ticket
                QUE->>QUE: Determine queue based on priority
                QUE->>QUE: Determine queue based on language if needed
                QUE->>QUE: Determine queue based on skill if needed
                QUE-->>ESC: queue_status = queued
                ESC->>ROT: Request volunteer routing
                ROT->>ROT: Fetch available volunteers
                ROT->>ROT: Check current load
                ROT->>ROT: Check required skills
                ROT->>ROT: Check escalation priority
                ROT-->>ESC: Routing candidates or none
                alt Volunteer immediately available
                    ESC->>ROT: Reserve best volunteer
                    ROT->>VOL: Push new ticket alert
                    VOL-->>ROT: Volunteer acknowledges alert
                    ROT-->>ESC: assigned_volunteer candidate
                    ESC->>NOT: Send user waiting update
                    NOT-->>CH: Waiting update
                    CH-->>U: Inform user someone is joining
                    Note over ESC,ROT: Immediate assignment path keeps wait time low
                else No volunteer immediately available
                    ESC->>NOT: Send queue placement update
                    NOT-->>CH: Queue placement message
                    CH-->>U: Inform user they are in queue
                    ESC->>QUE: Keep ticket in waiting state
                    QUE->>QUE: Start SLA wait timer
                    Note over ESC,QUE: Ticket remains open until volunteer accepts
                end
                ESC-->>BOT: 200 success with ticket_id, queue_status, assigned_volunteer, next_state, message_for_user
                BOT->>SES: Store ticket_id
                BOT->>SES: Store queue_status
                BOT->>SES: Store assigned_volunteer if available
                BOT->>SES: Store next_state from response
                BOT->>SES: Store message_for_user
                SES-->>BOT: Session updated
                BOT-->>CH: Send message_for_user
                CH-->>U: Deliver escalation acknowledgement
                Note right of BOT: User is now either queued or in active handoff preparation
                alt next_state = WAITING_FOR_VOLUNTEER
                    BOT->>SES: Mark conversation mode = waiting
                    SES-->>BOT: Waiting mode stored
                    loop While no volunteer is assigned
                        QUE->>QUE: Check oldest waiting urgent tickets first
                        QUE->>ROT: Ask for latest availability snapshot
                        ROT-->>QUE: Return free volunteers
                        alt Volunteer becomes available
                            QUE->>ROT: Offer next eligible ticket
                            ROT->>VOL: Notify volunteer of queued ticket
                            VOL-->>ROT: Accept or reject
                            alt Volunteer accepts
                                ROT->>TKT: Attach assigned_volunteer
                                TKT-->>ROT: Ticket updated
                                ROT->>NOT: Send assignment update
                                NOT-->>CH: Volunteer found message
                                CH-->>U: Tell user a volunteer is joining now
                                BOT->>SES: Update queue_status = assigned
                                BOT->>SES: Update next_state = ACTIVE_HANDOFF
                                SES-->>BOT: Session updated
                            else Volunteer declines
                                ROT->>QUE: Return ticket to pending queue
                                QUE->>QUE: Keep wait timer running
                                NOT-->>CH: Still waiting message
                                CH-->>U: Inform user handoff is still in progress
                            end
                        else No volunteer available yet
                            QUE->>NOT: Send periodic wait update
                            NOT-->>CH: Still waiting notification
                            CH-->>U: Show please stay connected message
                            Note right of QUE: Frequency should avoid user spam
                        end
                        alt User cancels while waiting
                            U->>CH: Cancel request
                            CH->>BOT: Forward cancellation
                            BOT->>TKT: Mark ticket cancelled_by_user
                            TKT-->>BOT: Ticket closed
                            BOT->>SES: Set next_state = BOT_ACTIVE
                            BOT->>SES: Clear queue_status
                            BOT->>SES: Clear assigned_volunteer
                            SES-->>BOT: Session updated
                            BOT-->>CH: Confirm return to bot
                            CH-->>U: Deliver cancellation confirmation
                        else User stays in queue
                            BOT->>BOT: Keep waiting state alive
                        end
                    end
                else next_state = ACTIVE_HANDOFF
                    BOT->>SES: Mark conversation mode = human_handoff
                    SES-->>BOT: Human handoff mode stored
                end
                alt queue_status = assigned
                    TKT->>VOL: Open ticket in volunteer portal
                    VOL->>VOL: Load transcript summary
                    VOL->>VOL: Load latest user message
                    VOL->>VOL: Load escalation reason
                    VOL->>VOL: Load prior bot attempts
                    VOL->>VOL: Review conversation context
                    VOL->>NOT: Signal ready_to_join
                    NOT-->>CH: Volunteer joined notice
                    CH-->>U: Show volunteer connected
                    BOT->>SES: Store handoff_started_at
                    BOT->>SES: Store next_state = ACTIVE_HANDOFF
                    SES-->>BOT: Session updated
                    Note over U,VOL: Active human handoff starts here
                    loop During active handoff
                        U->>CH: Send message to human
                        CH->>VOL: Deliver user message
                        VOL-->>CH: Send human reply
                        CH-->>U: Deliver volunteer reply
                        VOL->>TKT: Append conversation note
                        TKT-->>VOL: Note saved
                        BOT->>SES: Mirror handoff transcript events
                        SES-->>BOT: Transcript event stored
                        alt Volunteer requests bot context
                            VOL->>BOT: Ask for bot summary
                            BOT->>SES: Read current context snapshot
                            SES-->>BOT: Return structured context
                            BOT-->>VOL: Provide summary without taking control
                        else No bot context needed
                            VOL->>VOL: Continue human conversation
                        end
                        alt User becomes inactive
                            VOL->>NOT: Send inactivity reminder
                            NOT-->>CH: Reminder to user
                            CH-->>U: Ask if they still need help
                        else Conversation continues
                            VOL->>VOL: Continue troubleshooting
                        end
                    end
                    alt Volunteer resolves issue
                        VOL->>TKT: Mark resolution = resolved
                        VOL->>TKT: Add resolution summary
                        TKT-->>VOL: Ticket updated
                        VOL->>BOT: Return conversation to bot
                        BOT->>SES: Set next_state = RETURNING_TO_BOT
                        BOT->>SES: Store handoff_outcome = resolved
                        BOT->>SES: Store resolution_summary
                        SES-->>BOT: Session updated
                        BOT-->>CH: Tell user bot is back for follow-up
                        CH-->>U: Deliver return-to-bot message
                        BOT->>SES: Reset fallback counter
                        BOT->>SES: Clear escalation candidate flags
                        BOT->>SES: Keep resolution summary for continuity
                        SES-->>BOT: Session updated
                        BOT->>BOT: Set next_state = BOT_ACTIVE
                        BOT-->>CH: Offer next automated step
                        CH-->>U: Deliver post-handoff support
                    else Volunteer cannot resolve but wants bot to continue
                        VOL->>TKT: Mark resolution = partial
                        VOL->>TKT: Add summary and next recommended step
                        TKT-->>VOL: Ticket updated
                        VOL->>BOT: Return with partial summary
                        BOT->>SES: Store handoff_outcome = partial
                        BOT->>SES: Store resolution_summary
                        BOT->>SES: Set next_state = BOT_ACTIVE
                        BOT->>SES: Reset fallback counter
                        SES-->>BOT: Session updated
                        BOT-->>CH: Continue with best next action
                        CH-->>U: Receive automated continuation
                    else Volunteer escalates again internally
                        VOL->>TKT: Mark escalation = supervisor_needed
                        TKT-->>VOL: Ticket updated
                        VOL->>QUE: Requeue for higher tier
                        QUE->>ROT: Route to specialist volunteer
                        ROT-->>QUE: Specialist candidate
                        NOT-->>CH: Extended wait message
                        CH-->>U: Inform user case is moving to specialist
                        BOT->>SES: Store next_state = WAITING_FOR_VOLUNTEER
                        SES-->>BOT: Session updated
                    end
                else queue_status = queued
                    BOT->>BOT: Remain in waiting state until assignment
                    Note right of BOT: Handoff not yet active because no volunteer is attached
                else queue_status = failed
                    BOT->>SES: Store next_state = ESCALATION_FAILED
                    SES-->>BOT: Session updated
                    BOT-->>CH: Inform user no volunteer could be reached
                    CH-->>U: Deliver graceful fallback
                end
                alt Volunteer disconnects unexpectedly
                    VOL->>TKT: Mark handoff_interrupted
                    TKT-->>VOL: Ticket updated
                    BOT->>SES: Store interruption_reason = volunteer_disconnect
                    BOT->>SES: Set next_state = WAITING_FOR_VOLUNTEER
                    SES-->>BOT: Session updated
                    QUE->>ROT: Find replacement volunteer
                    ROT-->>QUE: Replacement candidate or none
                    NOT-->>CH: Reassignment message
                    CH-->>U: Tell user a new volunteer is being connected
                else User disconnects unexpectedly
                    CH->>BOT: Channel timeout event
                    BOT->>TKT: Mark user_disconnected
                    TKT-->>BOT: Ticket updated
                    BOT->>SES: Store next_state = BOT_ACTIVE
                    SES-->>BOT: Session updated
                    NOT-->>CH: Session closed message
                else Handoff completes normally
                    BOT->>BOT: No interruption handling required
                end
            end
        end
        deactivate ESC
    else should_escalate = false
        BOT->>BOT: Stay in automated experience
    end
    %% Return-to-bot safeguards
    BOT->>SES: Read final state snapshot
    SES-->>BOT: Return current state, ticket_id, and counters
    alt next_state = BOT_ACTIVE
        BOT->>SES: Ensure fallback counter reset policy applied
        SES-->>BOT: Reset confirmed
        BOT->>SES: Ensure active volunteer reference removed
        SES-->>BOT: Cleanup confirmed
        BOT->>SES: Ensure queue_status archived
        SES-->>BOT: Archive confirmed
        BOT->>SES: Ensure resolution summary retained
        SES-->>BOT: Continuity confirmed
        Note right of BOT: Bot resumes with preserved context but without stale queue data
    else next_state = WAITING_FOR_VOLUNTEER
        BOT->>SES: Keep waiting flags active
        SES-->>BOT: Waiting flags confirmed
        BOT->>SES: Preserve ticket_id for later polling
        SES-->>BOT: Ticket linkage confirmed
        BOT->>SES: Preserve assigned_volunteer if already known
        SES-->>BOT: Assignment linkage confirmed
        Note right of BOT: Conversation remains in handoff pipeline
    else next_state = ESCALATION_FAILED
        BOT->>SES: Mark fallback recovery path
        SES-->>BOT: Failure path confirmed
        BOT->>SES: Keep incident for audit
        SES-->>BOT: Audit record confirmed
        BOT->>SES: Allow user to retry later
        SES-->>BOT: Retry flag confirmed
        Note right of BOT: Failure should still be graceful to the user
    else next_state = ACTIVE_HANDOFF
        BOT->>SES: Keep bot responses suppressed
        SES-->>BOT: Suppression confirmed
        BOT->>SES: Keep human transcript sync enabled
        SES-->>BOT: Sync confirmed
        BOT->>SES: Keep volunteer association locked
        SES-->>BOT: Association confirmed
        Note right of BOT: Bot should not interrupt a live volunteer session
    end
    %% Audit and observability
    BOT->>TKT: Write final orchestration event
    TKT-->>BOT: Event stored
    BOT->>TKT: Write state transition trail
    TKT-->>BOT: Transition stored
    BOT->>TKT: Write trigger condition used
    TKT-->>BOT: Trigger stored
    BOT->>TKT: Write final next_state
    TKT-->>BOT: Final state stored
    BOT->>TKT: Write timestamps for wait and handoff
    TKT-->>BOT: Timing stored
    Note over BOT,TKT: These records support SLA tracking, debugging, and reporting
```

---

## Submission Note
This flow fully covers the Week 5 escalation requirements based on the currently shared 4A and 4B specifications, with a few implementation-level fields kept as working assumptions until Team 4B finalizes the exact API contract.
