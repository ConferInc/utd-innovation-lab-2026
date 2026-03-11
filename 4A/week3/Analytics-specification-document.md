# Task 5: Conversation Analytics Specification (JKYog WhatsApp Bot)
**Editor:** Harshith Bharathbhushan  
**Team:** 4A — Conversational UX & Design  

---

## 1. Executive Summary
This document defines the technical framework for measuring bot performance and user engagement for JKYog. By aligning our metrics with the exact `node_id` hierarchy in the JSON trees and the `log_` event triggers in the fallback scripts, we ensure that every interaction is trackable from initialization to final resolution.

---

## 2. Key Performance Indicators (KPIs)

### A. Business & Mission Success
* **Donation Flow Completion:** Percentage of sessions that reach the terminal donation information nodes (`DR_4` or `DR_5`).
* **Event Registration Interest:** Total hits on `VI_4` (Upcoming Events) and `VI_6` (Event Details) following an initial inquiry.
* **Volunteer Lead Generation:** Number of successful completions of the volunteer FAQ path within the general inquiries flow.

### B. User Experience (UX) Quality
* **Goal Completion Rate (GCR):** Percentage of users who reach a designated "Resolution Node" (`VI_9`, `DR_5`, or `TD_4`) vs. those who exit prematurely.
* **Average Interaction Depth:** The number of unique `node_id` transitions visited per session (Target: 3–5 turns for resolution).
* **Language Adoption Trends:** Tracking `record_lang_switch` events to identify the demand for English, Hindi, and Gujarati content.

### C. Technical Reliability
* **Fallthrough Rate:** Frequency of `log_intent_fail` events relative to total interactions.
* **Human Handoff Rate:** Percentage of users escalated to a live volunteer via the `log_human_escalation_fail` path.
* **Service Stability:** Frequency of `log_fallback_timeout` events indicating backend API or connectivity issues.

---

## 3. Funnel Analysis & Interaction Tracking
To identify friction points, we map the user journey to the specific `node_id` values found in the team's finalized conversation trees.

| Target Funnel | Entry Node | Success/Goal Node | Failure Condition |
| :--- | :--- | :--- | :--- |
| **Donations** | `node_id: DR_1` | `node_id: DR_5` (Final End) | Triggering Inactivity |
| **Visitor Info** | `node_id: VI_1` | `node_id: VI_9` (Final End) | Triggering `node_id: VI_8` (Inactivity) |
| **Temple Directions**| `node_id: TD_1` | `node_id: TD_4` (Parking) or `TD_5` | Exit after `TD_1` without selection |



**Friction Point Detection:** By monitoring the drop-off at the inactivity handlers (e.g., `VI_8`), we can determine if specific flows—such as the 45-second timeout for complex information—are too aggressive for the demographic and adjust the orchestration logic for the production build.

---

## 4. Effectiveness & Sentiment Tracking
* **Sentiment Analysis:** The system will monitor the tone of the final message before "End" nodes to determine if user needs were met successfully.
* **Deflection Efficiency:** Calculated as the percentage of sessions that end at a "Success Node" without ever triggering a `log_human_escalation` event.
* **Interaction Heatmap:** Visualizing the most frequently visited nodes (e.g., `VI_2` timings vs `VI_4` events) to help prioritize content updates for upcoming religious festivals.

---

## 5. Metadata Integration & Team Alignment
This specification is operationalized through the following "Data Hooks" integrated into the Team 4A deliverables:

1. **Session Context:** Every interaction log includes `session_id`, `user_id`, and `detected_intent`.
2. **Error Telemetry:** Fallback paths emit the following specific strings for the analytics engine:
    * `log_intent_fail`
    * `log_fallback_timeout`
    * `log_context_loss`
    * `log_human_escalation_fail`
3. **Linguistic Preferences:** Every language transition triggers a `record_lang_switch` event capturing the source and target languages.

---

## 6. Data Lifecycle & Infrastructure
Interaction data flows through a structured three-tier process:
1. **Raw Ingestion:** Immediate capture of WhatsApp webhooks and system event logs.
2. **Data Refinement:** Automated transformation processes to clean logs, calculate session duration, and map `node_id` paths to human-readable labels.
3. **Visualization:** Aggregated metrics are served via the Performance Dashboard for stakeholder review and planning.
