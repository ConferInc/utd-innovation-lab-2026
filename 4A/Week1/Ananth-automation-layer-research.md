# Ananth Vangala Task 3 — Automation / Orchestration Layer Research
Team 4A — Bot Architecture & Integration  
Owner: Ananth Vangala

## Goal
Evaluate orchestration tools that can connect **Website forms + WhatsApp + Voice bots** into a single workflow system that can:
- Receive inbound events (form submits, WhatsApp inbound, voice callbacks)
- Run workflow logic (if/else, routing, delays)
- Trigger outbound actions (WhatsApp send, voice call trigger)
- Log outcomes for analytics and follow-up

---

## Tools Compared
- **n8n** (open-source workflow automation)
- **Make.com** (formerly Integromat)
- **Vellum AI** (AI workflow/orchestration platform)
- **Lyzr** (agentic automation platform)

---

## What “Orchestration” Means 
Orchestration is the **middle layer** that controls the workflow:
1) Website form comes in  
2) Send WhatsApp confirmation  
3) Wait for reply  
4) If no reply → trigger voice call  
5) Log everything

---

## Connector Availability (high-level)
> Note: If a tool doesn’t have a “native connector,” it can still integrate using **HTTP/API requests + webhooks**.

- **n8n:** Strong general integration coverage via nodes + HTTP request support; commonly used for custom integrations.
- **Make:** Very strong library of prebuilt connectors; great for fast plug-and-play.
- **Vellum AI:** More focused on AI workflow building; typical integrations are API-driven rather than huge connector libraries.
- **Lyzr:** Focused on agent-driven automations; integrations are primarily API/enterprise workflow oriented.

---

## Webhooks + API Capabilities
What we need:
- **Inbound:** tool can receive events (webhook/trigger)
- **Outbound:** tool can call APIs (HTTP requests) to send WhatsApp / trigger voice calls

| Tool | Receive Webhooks (Inbound Triggers) | Call APIs (Outbound HTTP) | Notes |
|---|---|---|---|
| n8n | Yes | Yes | Flexible orchestration; good for custom integrations |
| Make | Yes | Yes | Fast setup; works well with connectors + HTTP module |
| Vellum AI | Yes (platform webhooks/integrations) | Yes (API-based) | Better as AI workflow layer; may sit beside core automation |
| Lyzr | Yes (via API/event workflows) | Yes (API-based) | Agentic automation; depends on use case + enterprise integration style |

---

## Self-hosted vs Cloud
| Tool | Hosting Model |
|---|---|
| n8n | **Cloud + Self-hosted** (open-source option gives long-term control) |
| Make | **Cloud-only** |
| Vellum AI | **Cloud** |
| Lyzr | **Cloud / Enterprise deployment options** (varies by plan) |

---

## Pricing Model (how costs grow)


| Tool | Pricing “shape” | What grows the bill? | Scalability takeaway |
|---|---|---|---|
| n8n | execution / instance-based | workflow runs or hosting cost | more predictable at scale; self-host can control cost |
| Make | operation-based | each module/step per run adds cost | can get expensive at high volume/complex workflows |
| Vellum AI | usage-based (AI workflow) | AI usage + workflow activity | good for AI logic; may add cost per interaction |
| Lyzr | usage/enterprise-based | agent usage + workflows | good for agent automation; pricing depends on enterprise scope |

---

## Example Workflow Diagram (text-based)
```text
[Website Form Submit]
      ↓ (Webhook Trigger)
[Orchestration Layer]
      ↓
[Parse + Validate Payload]
      ↓
[Upsert Contact + Tag (site_id = jkyog vs temple)]
      ↓
[Send WhatsApp Confirmation (API)]
      ↓
[Wait 24h]
   ├── If replied → [Log outcome] → End
   └── If no reply → [Trigger Voice Call (API)] → [Log outcome] → End
