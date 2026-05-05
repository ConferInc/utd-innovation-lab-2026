"""
Local debug harness for the JKYog WhatsApp bot pipeline.

Bypasses Twilio + FastAPI — calls classify() and build_response() directly
on a list of representative user messages, then prints exactly what the
bot would send back. Hits Team 4B's live Render API for real event data.

Run from 4A/week8/:
    .venv/Scripts/python.exe debug_harness.py
"""
import os
import sys
import json
import logging
import traceback
from dotenv import load_dotenv

load_dotenv()

# Verbose logging so we see classifier / API / builder steps
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)-25s | %(message)s",
)

# httpx is chatty at DEBUG — keep it at INFO so the trace stays readable
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.INFO)

log = logging.getLogger("debug_harness")

from intent_classifier import classify
from response_builder import build_response

TEST_MESSAGES = [
    # discovery — generic "what's happening"
    "What events are coming up?",
    # time_based — today
    "Any events today?",
    # time_based — this weekend
    "What's happening this weekend?",
    # event_specific — by event name
    "Tell me about the Holi celebration",
    # recurring_schedule — local handler should serve this
    "When is Sunday Satsang?",
    # logistics — needs event context
    "Where is the Bhakti Kirtan Retreat?",
    # sponsorship
    "How can I donate to the temple?",
    # ambiguous — should clarify
    "info",
    # greeting (handled by main.py, not the pipeline — included for completeness)
    "hi",
]

CONTEXT_TEMPLATE = {
    "phone_number": "+10000000000",
    "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
    "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN") or None,
    "user_id": "debug-user-id",
    "conversation_id": "debug-conv-id",
    "last_intent": None,
    "selected_event_id": None,
}


def banner(msg: str) -> None:
    print("\n" + "=" * 80)
    print(f"  {msg}")
    print("=" * 80)


def run_one(message: str) -> dict:
    banner(f"USER MESSAGE: {message!r}")

    # 1. Classify
    try:
        classification = classify(message)
        log.info("CLASSIFIER OUTPUT: %s", json.dumps(classification, default=str, indent=2))
    except Exception as e:
        log.error("CLASSIFY FAILED: %s", e)
        traceback.print_exc()
        return {"message": message, "stage": "classify", "error": str(e)}

    # 2. Build response (this is where the API call into Team 4B happens)
    context = dict(CONTEXT_TEMPLATE)
    context["last_intent"] = classification.get("intent")

    try:
        reply = build_response(classification, context)
        log.info("BUILDER OUTPUT (%d chars):\n%s", len(reply or ""), reply)
    except Exception as e:
        log.error("BUILDER FAILED: %s", e)
        traceback.print_exc()
        return {
            "message": message,
            "stage": "build_response",
            "classification": classification,
            "error": str(e),
        }

    return {
        "message": message,
        "stage": "ok",
        "classification": classification,
        "reply": reply,
    }


def main() -> int:
    if not os.getenv("GOOGLE_API_KEY"):
        log.error("GOOGLE_API_KEY not set — Gemini path will return None and fall back to Jaccard.")
    log.info("EVENTS_API_BASE_URL=%s", os.getenv("EVENTS_API_BASE_URL"))

    results = []
    for msg in TEST_MESSAGES:
        results.append(run_one(msg))

    # Summary table
    banner("SUMMARY")
    for r in results:
        intent = r.get("classification", {}).get("intent", "—")
        conf = r.get("classification", {}).get("confidence", "—")
        reply = r.get("reply") or r.get("error") or ""
        reply_preview = (reply[:70].replace("\n", " ") + "...") if len(reply) > 70 else reply
        print(f"  [{r['stage']:>14}] intent={intent:<22} conf={conf!s:<5} | {reply_preview}")

    failures = [r for r in results if r["stage"] != "ok"]
    if failures:
        print(f"\n{len(failures)} stage(s) failed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
