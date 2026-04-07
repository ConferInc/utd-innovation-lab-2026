# Week 8/9 Assignment — Consolidated Demo Sprint
## Ship the Working Bot

**Deadline:** Wednesday, April 15, 2026 at 11:59 PM CST  
**Sprint:** April 7 – April 15, 2026 (10 days)  
**Theme:** Integration — From Design to Working Demo

---

## 🎯 What This Sprint Is

Seven weeks of design, architecture, scraping, database engineering, intent modeling, and API contracts. This sprint is the payoff.

**The goal:** A user sends a WhatsApp message to the bot. The bot classifies the intent, calls Team 4B's live events API, and sends back a real, formatted WhatsApp response with real temple event data scraped from radhakrishnatemple.net and jkyog.org.

That's the demo. Not a mockup. Not a Postman screenshot. A real WhatsApp conversation with real data, deployed and running.

You have 10 days. You have AI coding tools. You have seven weeks of specs. Use all of it.

---

## 🎉 Mandatory Event — April 15, 2026

### Swami Mukundananda at UTD

📅 **Date:** Wednesday, April 15, 2026  
⏰ **Time:** 6:15 PM – 8:30 PM  
📍 **Location:** SSA Auditorium, University of Texas at Dallas

All 10 students are required to attend. This is the same event referenced in Week 5 — your RSVP is already expected. The demo deadline aligns with this event date intentionally: you build it, then you celebrate it.

🔗 **RSVP:** https://jkyog.live/yuva-utd

---

## 🤝 Mandatory Cross-Team Sync — April 9, 2026

**Schedule:** Thursday, April 9, 2026 at 7:00 PM CST  
**Attendees:** All 10 students  
**Duration:** 45 minutes

### Agenda

1. **Schema Alignment (20 min)**
   - Chanakya (4A) + Chakradhar (4B) present current field definitions side-by-side
   - Agree on final sponsorship tier schema: `tier_name/price_usd` or `name/amount`
   - Agree on event ID strategy: slug or integer PK
   - Agree on `source_site` enum values: `jkyog.org` or `jkyog`
   - Lock the schema. No changes after April 9.

2. **API Endpoint Alignment (15 min)**
   - Rohan (4B) confirms live Render URL and final endpoint paths
   - Team 4A confirms they can call the API from their local setup
   - Demo: `curl` the live `/api/v2/events/today` from Team 4A's machine

3. **Blocker Review (10 min)**
   - Any integration blockers that will prevent the demo?
   - Assign resolution owners with a 24-hour SLA

**Deliverable:** Meeting notes pushed to repo under `assignments/week-08-09-sync-notes.md` by April 9 at 9:00 PM CST

---

## 📋 Group 4A — Week 8/9 Tasks

**Theme:** Implement the Bot — Turn 7 Weeks of Design into Running Code

See `4A/week8/ASSIGNMENT.md` for individual breakdowns.

---

## 📋 Group 4B — Week 8/9 Tasks

**Theme:** Deploy, Fix & Support Integration

See `4B/week8/ASSIGNMENT.md` for individual breakdowns.

---

## 🎬 Joint Deliverable — Demo Video

**Owners:** All 10 students collaboratively  
**Due:** April 15, 2026 alongside the PRs  
**Length:** 3–5 minutes

The demo video must show:

1. A real WhatsApp message sent to the bot number (e.g., "What's happening at the temple this weekend?")
2. The message flowing through Team 4A's intent classifier and response builder
3. A visible call (log or trace) to Team 4B's deployed events API
4. A real WhatsApp response returned to the user with actual event data

Minimum intent coverage for the demo:
- Time-based query ("What's happening this weekend?")
- Event-specific query ("Tell me about Hanuman Jayanti")
- Recurring schedule query ("What time is Sunday Satsang?")
- No-results case ("Is there anything at 3 AM tonight?")

No slides. No mockups. No hardcoded responses. If you can't get all 4 working, record as far as you can and document in the PR what is blocking the rest.

---

## 📊 Submission Requirements

Each student must submit by **Wednesday, April 15, 2026 at 11:59 PM CST**:

1. Individual branch pushed to GitHub (`4[A/B]-week8-[your-name]`)
2. Merge into your team's shared branch
3. Team submits **ONE Pull Request to main** (draft by Monday April 13, final by Wednesday April 15)
4. Individual summary email to `students@mail.confersolutions.ai`:
   - What you implemented
   - What you used AI tools for (be specific — which tool, what prompt, what output)
   - What still doesn't work and why
   - Time spent
5. Demo video link included in the PR description

---

## 🚨 Critical Flags Going Into This Sprint

| Flag | Flagged Since | Owner |
|------|--------------|-------|
| Stripe webhook import error (runtime crash) | Week 7 | Leena |
| Events router at `/events` vs `/api/v2/events` | Week 7 | Rohan |
| SQLite local dev fallback — STILL missing | Week 3 | Chakradhar |
| Sponsorship tier schema mismatch | Week 7 | Chanakya + Chakradhar |
| Nikita's individual branch not traceable | Week 6, 7 | Nikita |
| Harshith no individual branch — 2nd week | Week 7 | Harshith |

Every one of these must be resolved by April 15.

---

## Questions?

Reach out in #utd-innovation-lab Slack or email `students@mail.confersolutions.ai`

This is the sprint that determines whether you built a bot or a collection of documents. Build the bot. 🚀
