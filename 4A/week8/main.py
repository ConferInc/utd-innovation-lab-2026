import os
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv

from intent_classifier import classify, warm_up as _warm_up_gemini
from response_builder import build_response

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Week 12 fix (Bug 5): Warm Gemini on startup so the first real WhatsApp
    # message does not pay the 25–30s TLS / model-cold-start cost. Twilio's
    # webhook timeout is 15s; without warm-up, students see "no response".
    if os.getenv("GEMINI_WARMUP", "1") == "1":
        try:
            ok = _warm_up_gemini()
            logger.info("Gemini warm-up: %s", "ok" if ok else "skipped/failed")
        except Exception as exc:  # pragma: no cover — safety net
            logger.warning("Gemini warm-up raised: %s", exc)
    yield


app = FastAPI(title="JKYog WhatsApp Bot", lifespan=lifespan)

ACTIVE_SESSIONS = {}

def send_whatsapp_message(to: str, body: str) -> str:
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    formatted_to = to if to.startswith("whatsapp:") else f"whatsapp:{to if to.startswith('+') else '+' + to}"
    
    msg = client.messages.create(
        from_=os.environ.get("TWILIO_WHATSAPP_FROM", ""),
        body=body,
        to=formatted_to,
    )
    return getattr(msg, "sid", "")

def process_message_background(body_text: str, sender_phone: str) -> None:
    start_time = time.monotonic()
    
    # Simple greeting bypass
    if body_text.lower().strip() in ["hi", "hello", "hey", "namaste", "start"]:
        send_whatsapp_message(to=sender_phone, body="Namaste! 🙏 Welcome to the JKYog Temple bot. You can ask me about upcoming events, parking info, or specific schedules like Sunday Satsang.")
        return

    # 1. AI Classification
    try:
        raw_classification = classify(body_text)
        logger.info(f"AI CLASSIFICATION: {raw_classification}")
    except Exception as e:
        logger.error(f"Classification Failed: {e}", exc_info=True)
        raw_classification = {"intent": "unknown", "entities": {}, "confidence": 0.0}

    # 2. WEEK 11 TASK 4: Bounded Session Management (Max 1000)
    MAX_SESSIONS = 1000
    
    if sender_phone not in ACTIVE_SESSIONS:
        # Evict the oldest session if we hit the limit to prevent memory leaks
        if len(ACTIVE_SESSIONS) >= MAX_SESSIONS:
            oldest_session_key = next(iter(ACTIVE_SESSIONS))
            del ACTIVE_SESSIONS[oldest_session_key]
            logger.warning(f"Session limit reached. Evicted oldest session: {oldest_session_key}")

        ACTIVE_SESSIONS[sender_phone] = {
            "user_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "last_intent": None,
            "selected_event_id": None,
            "last_shown_event_ids": [],
        }

    session_data = ACTIVE_SESSIONS[sender_phone]
    session_data.setdefault("last_shown_event_ids", [])
    session_data["last_intent"] = raw_classification.get("intent")

    # Bugfix (Round-3, R3-1): clear the session's selected_event_id when
    # the current message brings any fresh entity / query of its own.
    # Without this clear, a numbered selection ("2") would leak its event
    # id into every subsequent turn — so "where is the temple?" or
    # "when is the holi event?" would silently target the previously
    # selected event instead of the one the user just asked about.
    fresh_entities = (raw_classification.get("entities") or {}) if isinstance(raw_classification.get("entities"), dict) else {}
    if any(fresh_entities.get(k) for k in ("event_name", "program_name", "timeframe")) or len(body_text.split()) > 4:
        session_data["selected_event_id"] = None

    # Bugfix (post-Week-12 audit): support bare numeric replies like "2" as a
    # follow-up to a previously shown event list. The list response says
    # "Reply with: 1, 2, or 3 for full details" — if the previous turn pushed
    # 5 events into session.last_shown_event_ids, "2" should resolve to the
    # second of those event IDs and re-enter build_response with intent
    # event_detail. Done here in main.py so the classifier doesn't have to
    # learn list-position grammar.
    selected_id_override = None
    stripped = body_text.strip()
    if stripped.isdigit():
        idx = int(stripped) - 1
        prev_ids = session_data.get("last_shown_event_ids") or []
        if 0 <= idx < len(prev_ids):
            selected_id_override = prev_ids[idx]
            logger.info(f"NUMBERED FOLLOW-UP: '{stripped}' -> event_id={selected_id_override}")
            raw_classification = {
                "intent": "single_event_detail",
                "confidence": 1.0,
                "entities": {},
                "event_id": selected_id_override,
            }
            session_data["last_intent"] = "single_event_detail"
            session_data["selected_event_id"] = selected_id_override

    context = {
        "phone_number": sender_phone,
        "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
        "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN"),
        "user_id": session_data["user_id"],
        "conversation_id": session_data["conversation_id"],
        "last_intent": session_data["last_intent"],
        "selected_event_id": session_data["selected_event_id"],
        "last_shown_event_ids": list(session_data.get("last_shown_event_ids") or []),
        # Week 12 fix (Bug 2): Pass raw user message so the response builder
        # can use it as a fallback search query when neither the LLM nor the
        # entity extractor produced an event_name / query string.
        "user_message": body_text,
    }

    # 3. Build Response
    intent_str = raw_classification.get("intent")

    # Week 12 fix (Bug 4): For clarification / ambiguous / unknown we never
    # call build_response — go straight to the clarification prompt.
    if intent_str in ("clarification_needed", "ambiguous", "unknown"):
        reply_text = (
            "I'm not sure I caught that. You can ask me about:\n"
            "- *upcoming events* (e.g. \"what's happening this weekend?\")\n"
            "- a *specific event* (e.g. \"tell me about Holi\")\n"
            "- *recurring temple schedule* (e.g. \"when is Sunday Satsang?\")\n"
            "- *parking / logistics* for an event\n"
            "- *donations / seva*"
        )
    else:
        try:
            reply_text = build_response(raw_classification, context)
        except Exception as e:
            logger.error(f"Response Builder Failed: {e}", exc_info=True)
            reply_text = ""

        # 4. Graceful Fallback for empty replies only.
        if not reply_text or len(reply_text.strip()) == 0:
            reply_text = (
                "I'm having trouble understanding that right now. "
                "Try: 'What events are happening this weekend?'"
            )

        # Persist any list-of-event-IDs the response builder showed so the
        # next bare-digit reply ("2") can resolve to one of them.
        if "last_shown_event_ids" in context:
            session_data["last_shown_event_ids"] = list(context.get("last_shown_event_ids") or [])

    # 5. Send Message
    try:
        send_whatsapp_message(to=sender_phone, body=reply_text)
        elapsed = int((time.monotonic() - start_time) * 1000)
        logger.info(f"Message processed and sent successfully in {elapsed}ms to {sender_phone}")
    except Exception as e:
        logger.error(f"Failed to send Twilio message: {e}", exc_info=True)

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "JKYog Bot is online",
        "environment": os.getenv("ENV", "development"),
    }

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    body_text = form_data.get("Body", "").strip()
    sender_phone = form_data.get("From", "")
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if os.getenv("ENV") == "production":
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
        if not validator.validate(url, dict(form_data), signature):
            logger.warning("Invalid Twilio Signature dropped.")
            return JSONResponse(status_code=403, content={"error": "Invalid signature"})

    background_tasks.add_task(process_message_background, body_text, sender_phone)
    
    return JSONResponse(status_code=200, content={"status": "accepted"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
