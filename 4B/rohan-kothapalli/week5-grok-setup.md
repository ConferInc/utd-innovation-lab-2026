## Week 5 — Grok (xAI) + Gemini Switchable LLM Setup

This bot supports **two LLM providers** for response generation:

- **Gemini** (Google) — default
- **Grok** (xAI) — optional

You can switch providers using environment variables on Render.

---

### What changed (code)

- LLM provider switching is implemented in:
  - `4B/week4/bot/response_builder.py`
- Gemini model defaults were set back to **Gemini 2.5**:
  - `GEMINI_MODEL_RESPONSE` default: `gemini-2.5-flash`
  - `GEMINI_MODEL_INTENT` default: `gemini-2.5-flash-lite`
- Grok support uses xAI’s chat-completions-style endpoint with:
  - default model: `grok-3-mini`

---

### Environment variables (Render)

#### Required (Twilio + DB)
Keep your existing required vars (DB + Twilio), including:

- `DATABASE_URL`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`

#### Choose ONE LLM provider

##### Option A — Gemini (default)

- `LLM_PROVIDER=gemini`
- `GOOGLE_API_KEY=<your_google_api_key>`

Optional overrides:
- `GEMINI_MODEL_RESPONSE=gemini-2.5-flash`
- `GEMINI_MODEL_INTENT=gemini-2.5-flash-lite`
- `LLM_TIMEOUT_S=15`

Intent classification notes:
- By default, intent uses **keyword fallback** (no Gemini call) to keep overall requests at **1 LLM call per message**.
- If you want Gemini to classify intent too (2 LLM calls total), set:
  - `ENABLE_GEMINI_INTENT=1`

##### Option B — Grok (xAI)

- `LLM_PROVIDER=grok`
- `XAI_API_KEY=<your_xai_api_key>`

Optional overrides:
- `XAI_MODEL=grok-3-mini`
- `XAI_BASE_URL=https://api.x.ai/v1/chat/completions`
- `LLM_TIMEOUT_S=15`

---

### Expected behavior on Render logs

When a message arrives, you should see:

- `Webhook ack ... ack_ms=...` (fast HTTP closure to Twilio)
- `Message received_at=... queue_delay_ms=...` (background task start)
- `Message sent_at=... send_ms=... total_ms=... twilio_sid=...` (outbound send + end-to-end time)

---

### Troubleshooting

- **Gemini 404 model not found**
  - Set `GEMINI_MODEL_RESPONSE` to a model your key supports (e.g. `gemini-2.5-flash`).
- **Grok errors**
  - Confirm `XAI_API_KEY` is set and valid.
  - Confirm `XAI_MODEL=grok-3-mini` is available for your account.

