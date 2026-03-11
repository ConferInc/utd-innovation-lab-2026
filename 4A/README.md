# Team 4A — Bot Architecture & Integration

**Project Lead:** Rujul Shukla  
**Focus:** Technical Infrastructure, WhatsApp/Voice Bots, System Integration  
**Members:** Rujul (Lead), Nikita, Chanakya, Ananth, Harshith

---

## Mission

Research, design, and prototype the technical architecture for a multi-channel engagement platform integrating WhatsApp Business API, AI voice bots, and website systems — serving JKYog's dual web presence.

---

## Week 1 Assignment: Bot Platform Research Sprint

**Due:** Thursday EOD (Feb 20, 2026)  
**Format:** All deliverables as Markdown files in this folder (`4A/`)

---

### Task 1: WhatsApp API Deep Dive

Compare the following platforms:
- **Meta Business Platform** (direct API)
- **Twilio**
- **MessageBird**
- **Find 2 NEW providers** (not listed above) — research emerging WhatsApp API providers

**Deliverable:** `whatsapp-api-comparison.md`  
Include: pricing models, rate limits, India vs US support, conversation-based vs session-based pricing, webhook capabilities, ease of integration

---

### Task 2: Voice Bot Platforms

Compare the following:
- **VAPI** (existing Confer account/experience)
- **ElevenLabs Conversational AI**
- **Bland.ai**
- **Find 2 NEW voice AI platforms** — discover emerging voice bot tools

**Deliverable:** `voice-bot-comparison.md`  
Include: latency (ms), cost per minute, multi-language support, webhook/API capabilities, use case fit

---

### Task 3: Automation/Orchestration Layer

Research workflow automation tools that can connect WhatsApp + Voice + Website forms:
- **n8n** (open-source)
- **Make.com** (formerly Integromat)
- **Find 2 NEW workflow automation tools** — emerging players in the space

**Deliverable:** `automation-layer-research.md`  
Include: connector availability, pricing, self-hosted vs cloud, example workflow diagram (text-based)

---

### Task 4: Dual-Site Integration Architecture

Design how the bot system integrates with BOTH:
- https://www.radhakrishnatemple.net
- https://jkyog.org

**Deliverable:** `integration-architecture.md`  
Include:
- System architecture diagram (ASCII or markdown)
- Data flow for user interactions
- API endpoints needed
- Shared vs separate bot instances decision
- Caching/session strategy
- Security considerations

---

### Task 5: Go High Level Deep Dive

Set up a Go High Level trial account and explore:
1. Conversational AI features
2. WhatsApp integration capabilities
3. Voice/SMS features
4. Website chat widget
5. API availability

**Deliverable:** `go-high-level-analysis.md`  
Include: feature gap analysis vs standalone bot approach, when to use GHL vs custom build, pricing breakdown

---

### Task 6: Perplexity Flow Research Log

Document your research process, not just conclusions.

**Deliverable:** `perplexity-logs/` folder  
Export your Perplexity research sessions as Markdown files. Show:
- Queries you ran
- Dead-ends you encountered
- How you arrived at conclusions

---

### Final Deliverable: Stack Recommendations

**Deliverable:** `week1-recommendations.md`  

Present **3 complete architecture stacks** combining:
- WhatsApp API provider
- Voice bot platform
- Orchestration layer
- Website integration approach

For each stack, include:
- Architecture diagram
- Monthly cost at 1K / 10K / 100K user scale
- Implementation complexity (Low/Medium/High)
- Pros/cons
- Recommended use case

---

## Deliverable Standards

✅ All files in Markdown format  
✅ All research tracked in Perplexity (export logs)  
✅ Cost analysis at 3 scales (1K/10K/100K users)  
✅ At least 2 NEW tools discovered per category  
✅ Working prototypes/trials encouraged

---

## Checkpoints

| When | What |
|------|------|
| **Tuesday EOD** | Rujul posts progress update in team channel — what's found, what's blocked |
| **Thursday EOD** | All deliverables committed to GitHub AND individual email sent to students@mail.confersolutions.ai regarding your EOW update: What was accomplished, what are the blockers, what needs help, etc. |
| **Friday 11am** | Group 4A Meeting with Yatin — https://meetings.dialpad.com/room/marketingandsales/3szfht32px |

---

## Resources

- [VAPI Documentation](https://docs.vapi.ai/)
- [Meta WhatsApp Business API](https://business.whatsapp.com/products/business-platform)
- [n8n Documentation](https://docs.n8n.io/)
- [Go High Level](https://www.gohighlevel.com/)

---

Questions? Email: hermes@confersolutions.ai (include Rujul in CC)
