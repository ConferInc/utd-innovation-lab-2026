# Task 6: Research Process Log (Perplexity Research Session)

**Project:** JKYog Multi-Channel Engagement Platform  
**Consultant:** Nikita Pal  
**Focus Area:** Task 4 — Dual-Site Integration Architecture  
**Date:** Feb 19 – Feb 20, 2026  

---

# Phase I: Problem Framing — The Dual-Site Context Challenge

## Goal
Design a unified bot architecture capable of serving:

- radhakrishnatemple.net (Local Temple Operations – Dallas)
- jkyog.org (Global Spiritual Organization)

Without:
- Cross-contaminating knowledge
- Mixing branding
- Sharing unintended user data
- Increasing infrastructure cost unnecessarily

---

## Initial Strategic Query

> What architectural patterns are used in modern multi-tenant AI chatbot systems to support multiple domains with shared infrastructure but isolated contextual knowledge?

---

## Research Direction

Explored:
- Multi-tenant SaaS AI systems
- Domain-based routing architectures
- Context injection patterns in LLM systems
- Vector database partitioning strategies
- Knowledge isolation in RAG pipelines

---

## Key Insight

Modern AI systems follow this pattern:

- Shared LLM core
- Context injection layer
- Namespaced or partitioned vector knowledge base
- Metadata-based routing

This avoids duplicating AI infrastructure while maintaining contextual separation.

---

## Early Decision

Rejected:
- Fully separate bot instances per site (high cost + duplicated effort)

Adopted:
- Shared AI Core + Context Routing Layer

---

# Phase II: Domain-Based Context Routing Strategy

## Goal

Determine how the system programmatically identifies which site context to apply across:

- Web Chat
- WhatsApp
- Voice Calls

---

## Strategic Query

> What are the most reliable context detection mechanisms across multi-channel conversational systems?

---

## Findings

Identified 3 reliable routing mechanisms:

1. Domain-based routing (HTTP Origin Header for web)
2. Channel-based routing (WhatsApp phone number ID)
3. Campaign-based routing (Voice campaign metadata)

---

## Routing Implementation Design

### Website Example

Request:

```json
POST /chat/init
{
  "site": "jkyog",
  "session_id": "uuid",
  "message": "How do I enroll in Gita course?"
}
