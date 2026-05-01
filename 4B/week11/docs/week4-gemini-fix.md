# Week 4 — Gemini API 404 Fix (Bot Logic Scope)

## What was fixed

The WhatsApp bot was returning **404 Not Found** when handling messages. Those requests use the **Gemini API** from the Bot Logic Core (intent classification in `intent_classifier.py` and response generation in `response_builder.py`). The API was returning 404 because the **model name was no longer available**.

## Root cause

Both bot modules were calling Gemini with the deprecated model ID **`gemini-1.5-flash`**. Google has retired or restricted access to Gemini 1.5 models; many projects only have access to **Gemini 2.x** and **3.x** models. Calling `gemini-1.5-flash` therefore resulted in **404 "model not found"**.

## Code changes

- **`4B/week4/bot/intent_classifier.py`** — The model passed to `GenerativeModel(...)` is now `os.getenv("GEMINI_MODEL", "gemini-2.5-flash")` instead of the hardcoded `"gemini-1.5-flash"`.
- **`4B/week4/bot/response_builder.py`** — Same change: model is read from env with default `gemini-2.5-flash`.

The default **`gemini-2.5-flash`** is the current stable flash model for low-latency, high-volume text tasks.

## Optional: `GEMINI_MODEL` env var

You can override the model without changing code by setting in your `.env` or deployment environment:

```env
GEMINI_MODEL=gemini-2.5-flash
```

Other valid options (per Google’s current docs) include `gemini-flash-latest` (alias that tracks the latest flash model). If unset, the code uses `gemini-2.5-flash`.

## Verification

After deploying:

1. Send a few WhatsApp messages that trigger intent classification and LLM replies (e.g. greeting, FAQ, donation).
2. Confirm in your API dashboard that 404 errors stop and success rate returns to normal.
3. Optionally run `genai.list_models()` with your API key to confirm the chosen model is available.

---

*Bot Logic Core — Rohan Kothapalli | Week 4*
