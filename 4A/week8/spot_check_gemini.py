"""
Tiny Gemini spot-check (uses 4 quota units total: 1 warmup + 3 messages).

Demonstrates that the singleton client + warmup eliminate cold-start latency
on the first real classification.
"""
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
log = logging.getLogger("spot")

from intent_classifier import classify, warm_up

log.info("Pre-warm: calling warm_up()")
t0 = time.monotonic()
warm_up()
warmup_ms = int((time.monotonic() - t0) * 1000)
log.info("warm_up() took %d ms", warmup_ms)

cases = [
    "What events are coming up?",
    "When is Sunday Satsang?",
    "How can I donate?",
]

for msg in cases:
    t0 = time.monotonic()
    result = classify(msg)
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    log.info(
        "msg=%r intent=%s conf=%s elapsed=%dms",
        msg, result["intent"], result["confidence"], elapsed_ms,
    )
