# Week 5 Assignment — Cross-Team Integration Sprint

**Deadline:** Wednesday, March 18, 2026 at 11:59 PM CST  
**Theme:** Human Escalation, Performance, Security & Joint Integration

---

## 🎯 Mandatory Event — All 10 Students Required

### Swami Mukundananda at UTD

📅 **Date:** Wednesday, April 15, 2026  
⏰ **Time:** 6:15 PM – 8:30 PM  
📍 **Location:** SSA Auditorium, University of Texas at Dallas

**Event Highlights:**
- Campus Tour
- Enlightening Talk by Swamiji
- Panel Discussion
- Student Q&A
- Meet & Greet
- Dinner Prasad

Swamiji is an IIT–IIM alumnus, global spiritual leader, bestselling author, and founder of JKYog, known for blending ancient wisdom with practical life guidance.

🔗 **RSVP:** https://jkyog.live/yuva-utd

**Requirements:**
1. ALL 10 students must register and attend this event
2. Each student must bring at least ONE additional guest (friend, classmate, etc.)
3. Help with outreach and publicity on campus — this supports our client relationship
4. Confirmation of registration due by Wednesday, March 18 (same as weekly deliverables)

This is a professional obligation as part of the Confer-UTD Innovation Lab partnership.

---

## 🎯 Mandatory: Cross-Team Sync Meeting

**Schedule:** Monday, March 16, 2026 at 7:00 PM CST  
**Attendees:** All 10 students + leads from both teams  
**Duration:** 30 minutes max

### Agenda:

1. **API Contract Alignment (15 min)**
   - Team 4A presents current Meta Cloud API format (JSON webhook body, session_id)
   - Team 4B presents Twilio format (form-encoded: From, Body, ProfileName)
   - Agree on unified format for joint testing
   - Nikita & Harshith (4A) + Rohan (4B) to update shared contract post-meeting

2. **Week 5 Integration Goals (10 min)**
   - Define end-to-end test scenario: WhatsApp message → bot → API → response
   - Assign integration testing pairs

3. **Blocker Resolution (5 min)**
   - Confirm human escalation flow requirements
   - Clarify auth/Twilio signature verification ownership

**Deliverable:** Meeting notes posted to #utd-innovation-lab Slack by 8:00 PM Monday

---

## 📋 Group 4A — Week 5 Tasks

**Theme:** Human Escalation & API Refinement

### Chanakya Alluri — Bot-to-Human Escalation Flow

- Build complete human volunteer escalation sequence:
  - Trigger conditions (3+ failed intents, explicit "talk to human", profanity)
  - Volunteer queue system (available volunteers, busy status)
  - Ticket creation with conversation context
  - Handoff protocol (volunteer accepts → user notified → chat transferred)
  - Return-to-bot trigger (volunteer closes ticket → user notified → resume flow)
- **Deliver:** JSON flow definition + Mermaid sequence diagram (361+ lines)
- **Dependency:** Coordinate with Sysha on auth requirements for volunteer portal
- **Branch:** `feature/week5-escalation-flow`

### Ananth Vangala — Error Handling & Fallback States

- Extend state machine diagrams to include:
  - Error recovery flows (API timeout, invalid input, service down)
  - Fallback to human escalation path
  - State rollback on failure
- **Deliver:** 3 updated Mermaid diagrams + 2 new error-handling diagrams
- **Branch:** `feature/week5-error-states`

### Rujul Shukla — Multi-Scenario Conversation Testing

- Create test script with 20+ conversation scenarios:
  - Happy paths (donation, directions, event inquiry)
  - Edge cases (partial inputs, interruptions, language switches)
  - Error cases (timeouts, invalid data)
- Map each scenario to Team 4B's API endpoints
- **Deliver:** Markdown test script + expected request/response pairs
- **Branch:** `feature/week5-test-scenarios`

### Nikita Pal & Harshith Bharathbhushan — API Contract v2.0

**POST-SYNC TASK** (after Monday meeting):
- Update shared API contract to agreed unified format
- Version control the contract (v1.0 = Meta, v2.0 = Unified)
- Document breaking changes and migration guide
- Create Postman collection with example requests for both formats
- **Deliver:** Updated contract markdown + Postman collection
- **Branch:** `feature/week5-api-contract-v2`

---

## 📋 Group 4B — Week 5 Tasks

**Theme:** Performance, Security & Integration Readiness

### Rohan Kothapalli — Background Tasks & Gemini Optimization

- Implement BackgroundTasks for Twilio webhook processing
  - Acknowledge webhook immediately (200 OK)
  - Process intent + generate response asynchronously
  - Handle Twilio 15-second timeout gracefully
- Refactor Gemini calls to single invocation per message
  - Pass intent result to response_builder instead of re-calling
  - Document latency improvement (before/after metrics)
- **Deliver:** Updated main.py + response_builder.py + performance notes
- **Branch:** `feature/week5-performance`
- **Priority:** Critical for production stability

### Chakradhar Gummakonda — Database Connection Hardening

- Implement connection pooling for Render free tier
  - SQLAlchemy connection pool configuration
  - Idle timeout handling
  - Connection retry logic with exponential backoff
- Add database health check endpoint (/health/db)
- **Deliver:** Updated database.py + health endpoint + stress test results
- **Branch:** `feature/week5-db-hardening`

### Leena Hussein — Integration Test Documentation

- Create end-to-end integration test guide:
  - How to test against Team 4A's API contract
  - Mock server setup for offline testing
  - Expected vs actual response comparison
- Document environment setup for cross-team testing
- **Deliver:** integration-testing.md + mock server config
- **Branch:** `feature/week5-integration-docs`

### Subodh Krishna Nikumbh — Service Wrappers Completion

- Complete class-based wrappers for all services:
  - Stripe: payment intent, webhook handling, error codes
  - Maps: geocoding, directions, distance matrix
  - Calendar: event creation, availability checking, timezone handling
- Add comprehensive error handling and retry logic
- **Deliver:** Completed service_wrappers/ module + unit tests
- **Branch:** `feature/week5-service-wrappers`

### Sysha Sharma — Authentication & Security Layer

**MANDATORY FOCUS** — No exceptions this week:
- Implement Twilio webhook signature verification
  - Verify X-Twilio-Signature header
  - Reject requests with invalid signatures (401 response)
  - Document security rationale
- Create auth middleware for protected endpoints
- **Deliver:** auth.py with signature verification + middleware + documentation
- **Branch:** `feature/week5-auth` (INDIVIDUAL — no shared branch)
- **Coordinate:** Sync with Chanakya (4A) on volunteer portal auth requirements
- **Note:** This is a catch-up week. Missing this deliverable will require direct conversation with Yatin on Friday.

---

## 🤝 Joint Deliverable — Cross-Team Integration Test

**ALL STUDENTS** (collaborative, pairs assigned Monday):

By Wednesday EOD, demonstrate ONE working end-to-end flow:
1. User sends WhatsApp message to Team 4B's bot
2. Team 4B's bot calls Team 4A's API endpoint
3. Team 4A's API returns appropriate response
4. Team 4B's bot delivers response to user

**Document:**
- Screenshot of successful test (WhatsApp conversation)
- API request/response logs
- Any issues encountered and resolutions

**Post to Slack #utd-innovation-lab by Wednesday 11:59 PM with tag @channel**

---

## 📊 Submission Requirements (Per Student)

Each student must submit by **Wednesday, March 18, 2026 at 11:59 PM CST**:

1. Individual branch pushed to GitHub (`feature/week5-<task-name>`)
2. Merge into your team's shared branch (Group 4A or Group 4B)
3. Team submits **ONE Pull Request to main** (draft by Tuesday, final by Wednesday)
4. Individual summary email to students@mail.confersolutions.ai:
   - What you built this week
   - Blockers encountered (and how you resolved them)
   - Screenshots or demo links
   - Time spent
5. Confirmation of Swami Mukundananda event registration (screenshot acceptable)

---

## 🚨 Escalation Flags for Yatin's Friday Call

- **Sysha Sharma:** 2nd consecutive week without individual contribution — needs direct check-in
- **API contract mismatch:** Risk to Week 5 integration if Monday sync doesn't resolve
- **Chanakya's missing escalation flow:** Must complete this week (was Week 4 gap)

---

## Questions?

Reach out in #utd-innovation-lab Slack or email students@mail.confersolutions.ai

Good luck! Let's make Week 5 the week everything comes together. 🚀
