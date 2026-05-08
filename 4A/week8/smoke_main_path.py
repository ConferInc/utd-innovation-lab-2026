"""Test the actual main.py code path (greeting + clarification short-circuit)."""
import os, sys, io, asyncio
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("ENV", "development")

# Stub Twilio's send so it doesn't really send
class StubMessage:
    sid = "STUB-SID-12345"
class StubMessages:
    def create(self, **kw):
        print(f"  >> WOULD SEND TO {kw['to']}:")
        for line in kw['body'].split("\n")[:8]:
            print(f"  >> {line}")
        if len(kw['body'].split("\n")) > 8:
            print(f"  >> ... ({len(kw['body'].split(chr(10)))} lines total)")
        return StubMessage()
class StubClient:
    messages = StubMessages()
    def __init__(self, *a, **kw): pass

import twilio.rest
twilio.rest.Client = StubClient

import main as bot_main

CASES = [
    "Hi",
    "Hello",
    "info",
    "tell me more",
    "What events are coming up?",
    "How can I donate?",
    "When is Sunday Satsang?",
    "Anything on May 23rd?",
    "",
]

async def run():
    for msg in CASES:
        print("=" * 80)
        print(f"INBOUND: {msg!r}")
        bot_main.process_message_background(msg, "+15555550100")
        print()

asyncio.run(run())
