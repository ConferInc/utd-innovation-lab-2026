# Task 5: Conversation Analytics Specification (JKYog WhatsApp Bot)
**Editor:** Harshith Bharathbhushan  
**Team:** 4A — Conversational UX & Design  
**Project:** JKYog Multi-Channel Engagement Platform 

---

## 1. Executive Summary
This document defines the technical framework for measuring bot performance and user engagement for JKYog. By aligning our metrics with the exact `node_id` hierarchy in the JSON trees and the `log_` event triggers in the fallback scripts, we ensure that every interaction is trackable from initialization to resolution.

---

## 2. Key Performance Indicators (KPIs)

### A. Business & Mission Success
* **Donation Inquiry Completion:** Percentage of sessions that reach terminal donation info nodes (`DR_4` or `DR_5`).
* **Event Registration Interest:** Total hits on `VI_6` (Event Details) following an event inquiry.
* **Volunteer Lead Generation:** Number of successful completions of the volunteer FAQ path.

### B. User Experience (UX) Quality
* **Goal Completion Rate (GCR):** Percentage of users who reach a designated "Resolution Node" (e.g., `VI_9`, `DR_5`, or `TD_4`) vs. those who exit prematurely.
* **Average Path Depth:** The number of unique nodes visited per session (e.g., `VI_1` -> `VI_2` -> `VI_3` = 3 nodes).
* **Language Switch Frequency:** Tracking `record_lang_switch` events to identify the demand for Hindi vs. English content.

### C. Technical Reliability
* **Intent Match Rate:** Ratio of successful intent resolutions to total `log_intent_fail` events.
* **Handoff Rate:** Percentage of users escalated to a human volunteer via the `log_human_escalation_fail` path.
* **Service Stability:** Frequency of `log_fallback_timeout` events indicating backend API or connectivity issues.

---

## 3. Funnel Analysis & Interaction Tracking
To identify friction points, we map the user journey to the specific `node_id` values found in the team's conversation trees.

| Target Funnel | Entry Node | Success/Goal Node | Failure Condition |
| :--- | :--- | :--- | :--- |
| **Donations** | `node_id: DR_1` | `node_id: DR_5` (Tax Receipts) | Session timeout before `DR_2-5` |
| **Visitor Info** | `node_id: VI_1` | `node_id: VI_9` (Final Resolution) | Triggering `node_id: VI_8` (Inactivity) |
| **Temple Directions**| `node_id: TD_1` | `node_id: TD_4` (Parking) or `TD_5` | Exit after `TD_1` without selection |

### Data Integrity Warning:
*The current Visitor Inquiries JSON contains a duplicate ID (`VI_3` is used for both Festival Timings and Events). For accurate tracking, these must be unique (e.g., `VI_3` and `VI_4`).*

---

## 4. Effectiveness & Sentiment Tracking
* **Sentiment Analysis:** We will monitor the tone of the final message before the `end` node (`VI_9`) to determine if the user's needs were met.
* **Deflection Rate:** Calculated as sessions that end at a "Success Node" without ever triggering a `log_human_escalation` event.
* **Inactivity Abandonment:** Tracking triggers of `node_id: VI_8` to identify if the 45-second timeout is too aggressive for JKYog’s demographic.

---

## 5. Metadata Integration (Team Alignment)
This specification relies on the following data points being captured at the orchestration layer:

1. **Session Context (Ananth):** Every log must include `session_id`, `user_id`, and `detected_intent`.
2. **Error Telemetry (Chanakya):** Fallback paths must emit the following specific strings for the analytics engine:
    * `log_intent_fail`
    * `log_fallback_timeout`
    * `log_context_loss`
    * `log_human_escalation_fail`
3. **Linguistic Preferences (Nikita):** Every language transition must trigger a `record_lang_switch` event capturing the source and target languages.

---

## 6. Data Lifecycle & Infrastructure
Interaction data flows through a structured three-tier process:
1. **Raw Ingestion:** Immediate capture of WhatsApp webhooks and system event logs.
2. **Refinement:** Use of automated transformation tools to clean logs, calculate session duration, and map `node_id` paths to human-readable labels.
3. **Visualization:** Aggregated metrics are served via the JKYog Performance Dashboard for stakeholder review.
