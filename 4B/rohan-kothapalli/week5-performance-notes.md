## Week 5 — Performance Notes (Rohan Kothapalli)

---

### 1. Architecture Overview (Week 5)

- **Webhook** returns `200 OK` to Twilio immediately after authentication, before any LLM or DB work.
- All heavy processing (intent, LLM response, Twilio send, DB logging) runs in a **FastAPI BackgroundTask**.
- Only **one** LLM call is made per inbound message (intent uses keyword fallback by default).

---

### 2. Observed Render Log Metrics

The following numbers are drawn from real production logs on Render.

#### Webhook Ack Time (`ack_ms`)
Time from receiving the Twilio webhook to returning HTTP 200 OK:

| Sample | ack_ms |
|--------|--------|
| 1      | 257 ms |
| 2      | 51 ms  |
| 3      | 38 ms  |
| 4      | 38 ms  |
| 5      | 57 ms  |
| 6      | 63 ms  |

**Average: ~84 ms** (well within Twilio's 15-second timeout)

---

#### Background Queue Delay (`queue_delay_ms`)
Time between webhook receipt and when the background task actually starts:

| Sample | queue_delay_ms |
|--------|----------------|
| 1      | 258 ms         |
| 2      | 52 ms          |
| 3      | 39 ms          |
| 4      | 39 ms          |
| 5      | 58 ms          |
| 6      | 63 ms          |

**Average: ~85 ms** (fast pickup, negligible overhead)

---

#### Twilio Send Time (`send_ms`)
Time taken for the outbound Twilio REST API call to complete:

| Sample | send_ms |
|--------|---------|
| 1      | 919 ms  |
| 2      | 386 ms  |
| 3      | 411 ms  |
| 4      | 300 ms  |
| 5      | 407 ms  |
| 6      | 400 ms  |

**Average: ~470 ms**

---

#### End-to-End Total Time (`total_ms`) — Fallback Mode (No Gemini/Grok)
Time from webhook receipt to Twilio send confirmed (user receives reply) when the LLM is **not** used (hardcoded responses only):

| Sample | total_ms |
|--------|----------|
| 1      | 2512 ms  |
| 2      | 1166 ms  |
| 3      | 1192 ms  |
| 4      | 980 ms   |
| 5      | 823 ms   |
| 6      | 848 ms   |

**Average: ~1254 ms (~1.25 seconds)**

Sample 1 was higher (2512 ms) — this was the first message after deploy, likely due to cold-start overhead. Steady-state fallback is consistently under ~1.2 seconds.

---

#### Gemini 2.5 Runs (`total_ms`) — LLM Enabled
With `LLM_PROVIDER=gemini` and `GEMINI_MODEL_RESPONSE=gemini-2.5-flash`, the LLM call adds extra latency. From the logs:

| Sample | ack_ms | queue_delay_ms | send_ms | total_ms |
|--------|--------|----------------|---------|----------|
| G1     | 48 ms  | 56 ms          | 875 ms  | 3530 ms  |
| G2     | 43 ms  | 44 ms          | 474 ms  | 3577 ms  |
| G3     | 43 ms  | 44 ms          | 329 ms  | 2219 ms  |

- **Average total_ms (Gemini 2.5 enabled): ~3109 ms (~3.1 seconds)**  
- Webhook ack and queue delay remain small; the extra time is almost entirely LLM + Twilio send.

---

### 3. Default Fallback Behavior (When LLM Fails)

When the LLM (Gemini or Grok) is unavailable or returns an error, the bot falls back to **hardcoded responses** built into each handler in `response_builder.py`. This ensures the bot always replies to the user regardless of LLM status.

Observed fallback scenarios from logs:

- **Gemini 429 RESOURCE_EXHAUSTED** (free tier quota exceeded):
  - Intent falls back to keyword matching.
  - Response falls back to hardcoded template.
  - Bot still replies successfully via Twilio (`201 Created`).

- **Gemini 404 NOT_FOUND** (invalid model name):
  - Same fallback path; bot responds with canned text.

- **Grok 403 Forbidden** (wrong endpoint or API key issue):
  - Bot falls back to hardcoded response.
  - Twilio send still succeeds.

**In all fallback cases, Twilio received a `201` and the user got a reply.**

The fallback responses are:
- `greeting` → standard welcome message listing bot capabilities
- `faq_query` → top KB result raw text, or temple contact info
- `event_query` → KB events, or calendar fallback, or temple contact info
- `donation_request` → Stripe link + canned donation message
- `directions_request` → temple address + GPS instructions
- `unknown` → list of bot capabilities + temple contact number

---

### 4. LLM Provider Summary

| Provider | Env var          | Default model        | Status as of Week 5   |
|----------|------------------|----------------------|-----------------------|
| Gemini   | `LLM_PROVIDER=gemini` | `gemini-2.5-flash` | Active (requires valid billing/quota) |
| Grok     | `LLM_PROVIDER=grok`   | `grok-3-mini`      | Active (requires `XAI_API_KEY`) |

Switch providers in Render via:
- `LLM_PROVIDER=gemini` + `GOOGLE_API_KEY`
- `LLM_PROVIDER=grok` + `XAI_API_KEY`

---

### 5. Summary

- Webhook ack is **fast and stable** (~38–257 ms), well within Twilio's 15-second window.
- End-to-end user reply latency is **~1.25 seconds** in steady-state fallback mode (no LLM), and **~2.2–3.6 seconds** when Gemini 2.5 is enabled.
- The fallback system ensures **100% reply rate** regardless of LLM provider status.
- Reducing from 2 Gemini calls to 1 LLM call per message improves quota usage and reduces latency.

*Bot Logic Core — Rohan Kothapalli | Week 5*
