"""Baseline smoke test for Shrikanth-week12-fixes branch.
Replays the same 24 cases that I ran against Chanakya's branch, but using
THIS branch's main.py logic faithfully (i.e. lifespan + session memory +
clarification short-circuit).
"""
import os, sys, io, time, json
# Force UTF-8 stdout so the en-dash and emoji in responses don't crash
# Windows cp1252 console encoding.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("ENV", "development")

from intent_classifier import classify, warm_up
from response_builder import build_response

CASES = [
    "What events are coming up?",
    "What's happening at the temple this weekend",
    "Is there anything at 3am tonight",
    "Any events tomorrow?",
    "What's on this Friday?",
    "Anything on May 23rd?",
    "When is Sunday Satsang?",
    "What time is the morning aarti?",
    "Is there kirtan today?",
    "Where is the Bhakti Kirtan Retreat?",
    "Tell me about Janmashtami",
    "When is Holi?",
    "Where is the temple?",
    "Is there parking for Holi?",
    "How do I get to the Dallas retreat?",
    "How can I donate?",
    "How do I sponsor an event?",
    "Sponsorship for Holi?",
    "donate?",
    "tell me more",
    "info",
    "stuff happening",
    "Hello",
    "",
]

def truncate(text, n=220):
    if not text: return "(empty)"
    if len(text) <= n: return text.replace("\n", " | ")
    return (text[:n]).replace("\n", " | ") + " ..."

# Force jaccard-only to save Gemini quota for the live test
os.environ["FORCE_JACCARD_ONLY"] = "1"
print(f"FORCE_JACCARD_ONLY={os.environ.get('FORCE_JACCARD_ONLY')}")
print(f"EVENTS_API_BASE_URL={os.environ.get('EVENTS_API_BASE_URL')}")

for i, msg in enumerate(CASES, 1):
    print("-" * 100)
    print(f"[{i:>2}] {msg!r}")
    try:
        cls = classify(msg)
    except Exception as e:
        print(f"  CLASSIFY ERROR: {e}"); continue
    print(f"  intent={cls.get('intent')!s:<22} conf={cls.get('confidence')} entities={cls.get('entities')}")
    try:
        ctx = {"api_base_url": os.getenv("EVENTS_API_BASE_URL"), "user_message": msg}
        resp = build_response(cls, ctx)
    except Exception as e:
        print(f"  BUILD ERROR: {e}"); continue
    print(f"  resp: {truncate(resp)}")
