
# Nikita Pal Task 4 --- Dual-Site Integration Architecture

Team 4A --- Bot Architecture & Integration\
Owner: Nikita Pal

------------------------------------------------------------------------

## Goal

Design how the bot system integrates with:

-   radhakrishnatemple.net
-   jkyog.org

The architecture must support:

-   Website chat widgets\
-   WhatsApp Business API\
-   Voice bot platform\
-   CRM / marketing automation\
-   Event, donation, and contact workflows

------------------------------------------------------------------------

## What "Dual-Site Integration" Means

Both websites share:

-   Same backend bot intelligence
-   Same orchestration logic
-   Same API infrastructure

But differ in:

-   Content (Temple vs Global org)
-   Event types
-   User journeys
-   Tone and branding

Solution: Shared Bot Core + site_context routing

------------------------------------------------------------------------

## High-Level System Architecture

    [Users]
      ├── Web (radhakrishnatemple.net)
      ├── Web (jkyog.org)
      ├── WhatsApp
      └── Voice Call

            ↓

    [Channel Layer]
      - Web Chat SDK
      - WhatsApp Webhook
      - Voice Bot Connector

            ↓

    [Automation / Orchestration Layer]

            ↓

    [Bot Core Engine]
      - LLM / NLU
      - Dialog Manager
      - Knowledge Base Router
      - Session Store

            ↓

    [Backend APIs]
      - Events
      - Donations
      - Contact Forms
      - Newsletter
      - CRM (Go High Level or equivalent)

------------------------------------------------------------------------

## Shared vs Separate Bot Instances

### Decision: Shared Bot Core

  ------------------------------------------------------------------------
  Approach                         Pros                Cons
  -------------------------------- ------------------- -------------------
  Separate bots                    Full isolation      Double maintenance

  Shared bot + site_context        Unified learning +  Requires strict
                                   lower cost          routing
  ------------------------------------------------------------------------

Implementation:

    site_context = "rkt" | "jkyog"

Used to:

-   Route to correct knowledge base
-   Load correct FAQ data
-   Trigger correct event APIs
-   Apply site-specific branding

------------------------------------------------------------------------

## Data Flow -- Website Chat (Temple)

    [User opens chat]
          ↓
    [Web Chat sends payload]
          ↓
    { text, channel="web", site_context="rkt" }
          ↓
    [Orchestration Layer]
          ↓
    [Bot Core]
          ↓
    [Temple Knowledge Base]
          ↓
    [Response returned]

------------------------------------------------------------------------

## Data Flow -- WhatsApp → Event Registration

    [User sends WhatsApp message]
          ↓
    [Webhook → Channel Adapter]
          ↓
    [Orchestration Layer]
          ↓
    [Bot detects: event_registration]
          ↓
    [Collect name + email]
          ↓
    POST /api/events/register
    POST /api/crm/lead
          ↓
    [Send confirmation message]

------------------------------------------------------------------------

## API Endpoints Needed

### Contact Submission

    POST /api/contact/submit

Fields:

-   site
-   channel
-   name
-   email
-   message

------------------------------------------------------------------------

### Events

    GET /api/events/upcoming
    POST /api/events/register

------------------------------------------------------------------------

### Donations (Intent Capture)

    POST /api/donations/intent

Initial model: capture interest → follow up via CRM.

------------------------------------------------------------------------

### Marketing Opt-In

    POST /api/marketing/subscribe

Tracks:

-   WhatsApp consent
-   Email consent

------------------------------------------------------------------------

## Caching + Session Strategy

Session Key:

    (channel_type + channel_user_id)

Stored:

-   site_context
-   conversation state
-   partial form inputs
-   last N messages

Storage:

-   Redis (fast)
-   Persistent DB backup

------------------------------------------------------------------------

## Security Considerations

-   HTTPS everywhere
-   JWT between services
-   IP restriction for internal APIs
-   Rate limiting on webhooks
-   Encrypt PII at rest
-   Consent tracking for WhatsApp/email

------------------------------------------------------------------------

## Web Integration Strategy

Each site embeds:

-   Lightweight chat widget
-   Passes hidden field: site_context
-   Connects via HTTPS to orchestration layer

No duplication of bot logic required.

------------------------------------------------------------------------

## Scalability Model

Designed to scale from:

-   1K users (pilot)
-   10K users (regional)
-   100K users (global)

Primary cost drivers:

-   WhatsApp conversations
-   Voice minutes
-   LLM usage

Architecture supports:

-   Stateless services
-   Horizontal scaling
-   Container deployment

------------------------------------------------------------------------

## Example End-to-End Workflow

    [Website Form Submit]
          ↓ (Webhook)
    [Orchestration Layer]
          ↓
    [Parse + Validate]
          ↓
    [Upsert Contact + Tag (rkt vs jkyog)]
          ↓
    [Send WhatsApp Confirmation]
          ↓
    [Wait 24h]
       ├── If replied → Log outcome → End
       └── If no reply → Trigger Voice Call → Log → End

------------------------------------------------------------------------

## Summary

The proposed architecture:

-   Uses a shared intelligence layer\
-   Separates context using site_context\
-   Supports WhatsApp + Voice + Web\
-   Is scalable, secure, and modular\
-   Avoids duplicate infrastructure across both websites
