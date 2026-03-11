# Task 6: Research Process Log (Gemini AI Research Session)
**Project:** JKYog Multi-Channel Engagement Platform
**Consultant:** Harshith Bharathbhushan
**Focus Area:** Task 5 - GoHighLevel (GHL) Platform Deep Dive
**Date:** Feb 19 - Feb 20, 2026

---

## 1. Phase I: Operational Environment Setup
**Goal:** Provision a localized testing environment for the Radha Krishna Temple sub-account.

* **Initial Query:** "How should I structure a GoHighLevel sub-account to serve JKYog’s dual-site requirement? What are the implications of choosing a physical location for AI timezone syncing?"
* **Action & Logic:** Provisioned the trial account and mapped it to the **Radha Krishna Temple of Dallas** using the native Google Maps API search. 
* **Verification Step:** I specifically audited the **Primary Contact** naming convention. 
    * *Conclusion:* Established myself as the "Technical Admin" to test the `{{user.first_name}}` merge tags in automated responses. This was a critical step to verify how the "AI Employee" identifies itself to users in a 2026 production environment.

---

## 2. Phase II: Technical Feature Audit (The "2026 Benchmark")
**Goal:** Verify 2026-specific feature updates to solve the dual-site context problem.

* **Strategic Query:** "Does the 2026 'AI Employee' update support Federated Knowledge Bases? I need to separate JKYog global philosophy from local Temple event logistics without cross-contaminating responses."
* **Research Findings:** * Discovered the **Tabbed Knowledge Base** update (Jan 2026). 
    * Confirmed support for **Table Search (CSV)** which allows the bot to query structured data (like donation tiers) with natural language, rather than just reading static PDFs.
* **Risk Assessment:** Benchmarked GHL’s **AI Image Recognition** (released Dec 2025). This feature was identified as a key "Pro" for JKYog, allowing the bot to process WhatsApp-sent donation receipts automatically.

---

## 3. Phase III: Data Engineering & Medallion Architecture Mapping
**Goal:** Evaluate GHL's fit within a production-grade Snowflake/dbt/Airflow pipeline.

* **Inquiry:** "How does GHL’s API V2 (OAuth 2.0) handle high-volume data extraction? Can I build a Bronze-Silver-Gold Medallion pipeline using their native webhooks?"
* **Technical Stress Test:** * Audited the **API V2 Rate Limits** (100 requests per 10 seconds). 
    * Identified a **Critical Blocker:** GHL’s "LeadConnector" bridge acts as a data abstraction layer. While it simplifies setup, it obscures raw metadata (like original Meta Message IDs) required for deep-tier "Bronze" ingestion.
* **Conclusion:** Determined that for JKYog's 100K user goal, the "Vendor Lock-in" of a proprietary CRM creates a significant ETL bottleneck for our Snowflake data lake.

---

## 4. Phase IV: Performance & Latency Benchmarking
**Goal:** Compare the "All-in-One" speed vs. specialized "Best-of-Breed" latency.

* **Investigation:** "Why is the observed latency in GHL's Voice AI Receptionist (~1.5s) higher than specialized tools like Retell AI (<0.8s)?"
* **Technical Root Cause Analysis:** * Traced the routing path through the **LeadConnector middleware**. 
    * Confirmed that "Multi-Hop" routing is an inherent trade-off for the platform’s ease-of-use. 
* **Outcome:** This led to my recommendation for a **Hybrid Approach**: Use GHL for the CRM and Web Widget, but bypass its native voice engine for a direct API integration with a low-latency provider to meet the "human-instant" 2026 conversational standard.

---

## 5. Phase V: Final Verdict & Source Verification
**Goal:** Cross-referencing 2026 market data to finalize the "Build vs. Buy" recommendation.

* **Final Query Flow:** "Verify the 2026 WhatsApp per-message utility rates for India and the US to build a 100K user scalability model."
* **Final Synthesis:** * Fact-checked the **$97/mo Unlimited AI** add-on fee.
    * Integrated the findings into a 3-tier scalability model. 
* **Research Conclusion:** The sprint moved from a general exploration to a high-level architectural audit. By questioning the "Sources" and "Blockers" at every step, I arrived at a conclusion that prioritizes **Speed-to-Market** for the Pilot while protecting **Data Sovereignty** for the long-term production phase.
