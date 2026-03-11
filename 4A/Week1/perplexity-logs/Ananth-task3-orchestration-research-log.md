# Perplexity Flow Research Log - Ananth Vangala — Task 3 (Automation / Orchestration)

Owner: Ananth SV  
Team: 4A  
Date: Feb 19, 2026  

---

## Research Goal

Compare orchestration tools capable of connecting:

- Website Forms  
- WhatsApp APIs  
- Voice Bots  

Tools evaluated:
- n8n  
- Make.com  
- Vellum AI  
- Lyzr  

---

## Initial Questions / Confusions

- What exactly is an orchestration layer in this architecture?
- Do I need to manually test webhooks for Week 1?
- How do I compare tools consistently?
- What does “pricing scales” actually mean?
- What is the difference between operation-based and execution-based pricing?

---

## Queries I Ran

### Query 1
**Search:** what is orchestration layer in bot architecture  
**Purpose:** Understand the role of orchestration in a multi-channel system.  
**Outcome:** Defined orchestration as receiving events, running logic, triggering APIs, and logging data.

---

### Query 2
**Search:** n8n webhook trigger documentation  
**Purpose:** Confirm inbound webhook support.  
**Outcome:** Verified webhook trigger capability.

---

### Query 3
**Search:** n8n HTTP request node call external API  
**Purpose:** Confirm outbound API support.  
**Outcome:** Verified HTTP/API call capability.

---

### Query 4
**Search:** n8n conditional logic if else wait delay  
**Purpose:** Confirm workflow logic capability.  
**Outcome:** Verified conditional routing + delay nodes.

---

### Query 5
**Search:** n8n pricing workflow executions self hosted  
**Purpose:** Understand pricing structure and hosting options.  
**Outcome:** Identified execution-based model + self-hosted option.

---

### Query 6
**Search:** Make.com webhook module documentation  
**Purpose:** Confirm webhook trigger capability.  
**Outcome:** Verified webhook support.

---

### Query 7
**Search:** Make.com HTTP module API call  
**Purpose:** Confirm outbound API capability.  
**Outcome:** Verified HTTP module exists.

---

### Query 8
**Search:** Make.com router filter if else delay  
**Purpose:** Confirm conditional workflow logic.  
**Outcome:** Verified branching and delay support.

---

### Query 9
**Search:** Make.com pricing operations definition  
**Purpose:** Understand what increases cost.  
**Outcome:** Identified operation-based pricing model.

---

### Query 10
**Search:** Vellum AI orchestration integrations webhooks  
**Purpose:** Evaluate AI-native workflow capability.  
**Outcome:** Positioned as AI workflow layer with API integrations.

---

### Query 11
**Search:** Lyzr agentic automation API integration  
**Purpose:** Evaluate event-driven and API capabilities.  
**Outcome:** Identified agent-based automation approach.

---

## Dead Ends Encountered

1. Exact pricing numbers were unclear or sales-driven for AI-native tools.
   - Resolution: Documented pricing model type instead of exact dollar values.

2. Connector lists varied between marketing pages and documentation.
   - Resolution: Focused on webhook + HTTP support as universal integration fallback.

3. Confusion about whether testing was required.
   - Resolution: Determined Week 1 requires capability validation, not live deployment.

---

## How I Refined My Thinking

- Moved from vague comparison → fixed 5-question framework:
  - Webhook support
  - API call capability
  - Conditional logic
  - Hosting model
  - Pricing scale impact

- Shifted from exact cost numbers → pricing structure comparison.
- Separated traditional automation tools (n8n, Make) from AI-native workflow tools (Vellum, Lyzr).
- Focused on scalability implications rather than feature marketing.

---

## Final Research Output

Produced:
- automation-layer-research.md  
- Comparison table  
- Workflow diagram  
- Preliminary orchestration recommendation  
