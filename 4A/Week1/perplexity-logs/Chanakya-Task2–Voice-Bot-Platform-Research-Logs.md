# Task 2 – Voice Bot Platform Evaluation

## Research Logs (Process Documentation)

---

## Research Session 1 – Understanding Real-Time Voice AI

**Initial Queries:**

* Best real-time voice AI agents 2026
* What is real-time AI voice
* How does latency work in conversational AI
* STT → LLM → TTS pipeline explanation
* What is acceptable latency for AI voice

**What I Was Trying to Understand:**

* What “real-time” technically means in a conversational context.
* Whether latency is a single metric or a combination of multiple components.
* Identifying the specific delay threshold that feels natural in a live support call.

**What I Learned:**

* **Pipeline Architecture:** Real-time voice relies on a streaming pipeline: `Speech-to-Text (STT)` $\rightarrow$ `Large Language Model (LLM)` $\rightarrow$ `Text-to-Speech (TTS)`.
* **Cumulative Latency:** Delay isn't just one thing; it's the sum of speech recognition, reasoning, synthesis, and telephony overhead.
* **The "Magic" Number:** A sub-2 second response time is the gold standard for natural human-like interaction.

**What Confused Me:**

* Vendors use the term “real-time” loosely without providing consistent benchmarks.
* There is a lack of standardized latency disclosure across different platforms.

**Dead End:**

* Many tools marketed as “voice AI” were actually just simple TTS (Text-to-Speech) engines without conversational brains.

**Refinement:**

* I need to strictly separate "voice engines" (voice only) from "full conversational voice agents" (brains + voice).

---

## Research Session 2 – Customer Support Readiness

**Initial Queries:**

* Which voice AI platforms can handle customer support
* Inbound AI receptionist comparison
* Voice AI interruption handling (barge-in)
* Retell vs. PolyAI vs. Cognigy

**What I Was Trying to Understand:**

* Which platforms can handle complex inbound support vs. simple outbound robocalls.
* The technical difference between outbound automation and structured support systems.

**What I Learned:**

* **Outbound $\neq$ Support:** Outbound platforms often lack the "barge-in" (interruption) handling and complex logic required for support.
* **Logic Requirements:** High-level support requires robust escalation logic and multi-turn reliability.

**What Confused Me:**

* It is difficult to assess "production readiness" purely from marketing pages.
* Most case studies lacked a deep technical breakdown of the actual integration.

**Dead End:**

* I spent too much time prioritizing how "human" the voice sounded rather than how well the platform handled complex workflows.

**Refinement:**

* Shifted focus to **Webhook capability**, **Escalation paths**, and **CRM integration**.

---

## Research Session 3 – Webhooks & Integration Capability

**Initial Queries:**

* Voice AI webhook API support
* Tool calling in voice agents
* CRM integration voice AI
* Twilio SIP integration AI voice

**What I Was Trying to Understand:**

* How voice agents connect to external databases (CRM) and messaging apps (WhatsApp).
* Whether platforms support structured action triggers (e.g., booking a calendar slot during a call).

**What I Learned:**

* **The Power of Webhooks:** Essential for structured flows like registrations and appointment confirmations.
* **Tool-Calling:** This is the bridge that allows an AI to log data into a CRM or trigger follow-up automations.
* **Telephony Variance:** Integration with providers like Twilio or Vonage varies significantly between vendors.

**What Confused Me:**

* API documentation often claimed "support" but lacked detailed JSON payload examples.
* Hard to verify if webhooks would stay reliable under the pressure of a real-time voice flow.

**Dead End:**

* Reviewing generic API landing pages without seeing practical, end-to-end flow testing.

**Refinement:**

* I will evaluate platforms using **structured test scenarios**: Name capture, language switching, and mid-sentence interruption.

---

## Research Session 4 – Multilingual Capability

**Initial Queries:**

* Multilingual voice AI Hindi support
* ElevenLabs Hindi support
* Retell AI multilingual
* Language switching voice AI

**What I Was Trying to Understand:**

* Is Hindi support truly conversational (STT), or just a translated voice (TTS)?
* Can the agent switch languages mid-conversation if the user does?

**What I Learned:**

* **The Gap:** Many platforms have great Hindi TTS but very weak Hindi comprehension (STT/LLM).
* **Context Loss:** Switching languages often causes the "brain" of the AI to lose the previous context of the conversation.

**What Confused Me:**

* Marketing feature lists rarely differentiate between language fluency for STT vs. TTS vs. LLM.

**Dead End:**

* Assuming that a "Supported Languages" list implies the agent is actually reliable for a complex conversation in that language.

**Refinement:**

* Added specific **multilingual stress testing** to the evaluation framework.

---

## Research Session 5 – Pricing Model Comparison

**Initial Queries:**

* Voice AI pricing: per-minute vs. character-based
* ElevenLabs character pricing conversion
* Blended cost voice AI stack
* How to estimate cost at 1k, 10k, and 100k users

**What I Was Trying to Understand:**

* How to create a "fair" comparison between wildly different billing models.
* How to project costs as the user base grows.

**What I Learned:**

* **Pricing Fragmentation:** Models vary from per-minute and character-based to enterprise flat rates.
* **The Hidden Stack:** Modular "Build-your-own" stacks have hidden costs (paying for STT, LLM, TTS, and Telephony separately).

**What Confused Me:**

* Enterprise-grade vendors rarely publish their rates, making competitive analysis difficult.
* Exact scaling requires many assumptions about average call duration.

**Dead End:**

* Trying to force all vendors into a single "cost per minute" metric—it's often apples to oranges.

**Refinement:**

* I will document the **pricing model type** and the **modeling assumptions** rather than just a single price point.

---

## Research Session 6 – Architecture & Orchestration Impact

**Initial Queries:**

* Voice agent architecture with orchestration layer
* n8n vs. Make integration for voice
* Voice-to-WhatsApp automation
* Session management voice bot

**What I Was Trying to Understand:**

* How to bridge the gap between a Voice Call and a WhatsApp follow-up.
* Where the "memory" (session state) of the conversation should be stored.

**What I Learned:**

* **Orchestration is King:** A middle layer (like n8n or a custom backend) is critical for multi-channel deployments.
* **Cross-Channel Triggers:** The voice interaction must be able to trigger external events (SMS, WhatsApp, Email).
* **Session Strategy:** If the session state isn't handled correctly, the user feels like they are talking to a stranger every time they switch channels.

**What Confused Me:**

* Should the "memory" live inside the AI voice platform or in my own external database?
* How to maintain a consistent user identity across a phone call and a WhatsApp chat.

**Dead End:**

* Initially treating "Voice" as an isolated silo rather than part of an omni-channel ecosystem.

**Refinement:**

* Evaluate platforms based on their **integration primitives** and how well they play with external orchestration layers.

---