import logging
import os
import re
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client

from database import (
    SessionLocal,
    check_database_health,
    get_or_create_active_conversation,
    get_or_create_user,
    init_database,
    log_message,
    normalize_twilio_phone,
    update_message,
)
from conversational_reply import (
    build_clarification_context_block,
    build_conversational_clarification_reply,
    conversational_providers_configured,
)
from grounded_reply import build_grounded_whatsapp_reply
from intent_classifier import (
    _is_pure_greeting,
    _is_temple_personnel_roster_question,
    classify,
    pastoral_guidance_kind,
    warm_up as _warm_up_gemini,
)
from response_builder import build_response, build_response_with_facts

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

load_dotenv()


def _llm_routing_available() -> bool:
    """Use LLM for replies when a provider is configured.

    Set ``DISABLE_LLM_ROUTING=1`` to force template-only responses (ops / debug).
    """
    if os.getenv("DISABLE_LLM_ROUTING") == "1":
        return False
    return conversational_providers_configured()


REQUIRED_RUNTIME_ENV = (
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_FROM",
    "EVENTS_API_BASE_URL",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init = init_database()
    if db_init.get("enabled"):
        logger.info(
            "Database bootstrap status=%s columns_added=%s",
            db_init.get("status"),
            ",".join(db_init.get("columns_added") or []) or "none",
        )
    else:
        logger.warning("Database logging disabled: %s", db_init.get("reason"))

    missing_env = _missing_env_vars(REQUIRED_RUNTIME_ENV)
    if missing_env:
        logger.warning("Missing runtime environment variables: %s", ", ".join(missing_env))

    if _signature_validation_enabled() and not os.getenv("TWILIO_AUTH_TOKEN"):
        logger.warning(
            "Twilio signature validation is enabled for production but TWILIO_AUTH_TOKEN is missing."
        )

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


def _missing_env_vars(names) -> list[str]:
    return [name for name in names if not os.getenv(name)]


def _signature_validation_enabled() -> bool:
    return os.getenv("ENV") == "production"


def _database_snapshot() -> Dict[str, Any]:
    snapshot = check_database_health()
    if not snapshot.get("enabled"):
        return snapshot
    return snapshot


def _readiness_snapshot() -> Dict[str, Any]:
    db = _database_snapshot()
    missing_env = _missing_env_vars(REQUIRED_RUNTIME_ENV)
    signature_validation = {
        "enabled": _signature_validation_enabled(),
        "configured": bool(os.getenv("TWILIO_AUTH_TOKEN")),
    }
    ready = not missing_env and (not db.get("enabled") or db.get("healthy"))
    return {
        "ready": ready,
        "environment": os.getenv("ENV", "development"),
        "missing_env": missing_env,
        "signature_validation": signature_validation,
        "database": db,
    }


def _get_or_create_session(sender_phone: str) -> Dict[str, Any]:
    max_sessions = 1000
    if sender_phone not in ACTIVE_SESSIONS:
        if len(ACTIVE_SESSIONS) >= max_sessions:
            oldest_session_key = next(iter(ACTIVE_SESSIONS))
            del ACTIVE_SESSIONS[oldest_session_key]
            logger.warning("Session limit reached. Evicted oldest session: %s", oldest_session_key)

        ACTIVE_SESSIONS[sender_phone] = {
            "user_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "last_intent": None,
            "selected_event_id": None,
            "last_shown_event_ids": [],
        }

    session_data = ACTIVE_SESSIONS[sender_phone]
    session_data.setdefault("last_shown_event_ids", [])
    return session_data


def _persist_message_update(db, message, **kwargs) -> None:
    if not db or message is None:
        return
    try:
        update_message(db, message, **kwargs)
    except Exception as exc:
        logger.warning("Database message update failed: %s", exc, exc_info=True)
        db.rollback()


_LIST_SELECTION_PATTERNS = (
    re.compile(r"(?:register|sign\s*up)\s+for\s+(\d+)", re.I),
    re.compile(r"(?:detail|details|info|information|more)\s+(?:on|about|for)\s+(\d+)", re.I),
    re.compile(r"#\s*(\d+)\b"),
    re.compile(r"\b(?:option|choice|event)\s*#?\s*(\d+)\b", re.I),
)


def _extract_shown_list_index_1based(body_text: str) -> Optional[int]:
    """1-based row index from phrases like 'register for 1' or '#2', or None."""
    t = body_text.strip()
    for rx in _LIST_SELECTION_PATTERNS:
        m = rx.search(t)
        if m:
            return int(m.group(1))
    return None


def _build_pastoral_guru_contact_reply() -> str:
    return (
        "Namaste!\n\n"
        "To connect with the Pujari or Pandit Ji, you can visit the temple during darshan hours "
        "or inquire at the front desk. They can guide you on the best times to speak with them.\n\n"
        "You can also reach out to the temple office at +1 (469) 444-7173 during their operating hours "
        "to schedule a conversation or ask about other temple services."
    )


def _build_pastoral_spiritual_peace_reply() -> str:
    return (
        "Dear devotee, finding peace is a journey many seek. Our temple offers various programs "
        "and practices that can help guide you.\n\n"
        "You can explore our services by visiting our website at jkyog.org. We also have recurring "
        "events like Sunday Satsang, which many find brings a sense of calm and spiritual connection. "
        "If you'd like to know more about our schedule or how you can get involved, please feel free to ask!"
    )


def _build_out_of_scope_reply() -> str:
    return (
        "Sorry — I don't have that information. This assistant only has access to "
        "the *event calendar*, *recurring program times*, *practical logistics* for named events, "
        "*temple address / hours / parking*, and *donations*.\n\n"
        "Ask me in your own words about any of those, and I'll do my best to help."
    )


def _build_clarification_reply(*, pure_greeting: bool = False) -> str:
    topics = (
        "Tell me what you're looking for! For example:\n"
        "- *upcoming events* (e.g. \"what's happening this weekend?\")\n"
        "- a *specific event* (e.g. \"tell me about Holi\")\n"
        "- *recurring temple schedule* (e.g. \"when is Sunday Satsang?\")\n"
        "- *parking / logistics* for an event\n"
        "- *donations / seva*"
    )
    if pure_greeting:
        return f"Hi there — happy to help.\n\n{topics}"
    return f"Sorry, I couldn't understand what you meant.\n\n{topics}"


def send_whatsapp_message(to: str, body: str) -> str:
    missing_env = _missing_env_vars(("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"))
    if missing_env:
        raise RuntimeError(
            "Missing Twilio environment variables: " + ", ".join(missing_env)
        )

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    formatted_to = to if to.startswith("whatsapp:") else f"whatsapp:{to if to.startswith('+') else '+' + to}"

    msg = client.messages.create(
        from_=os.environ["TWILIO_WHATSAPP_FROM"],
        body=body,
        to=formatted_to,
    )
    return getattr(msg, "sid", "")


def process_message_background(
    body_text: str,
    sender_phone: str,
    profile_name: Optional[str] = None,
    *,
    inbound_message_sid: Optional[str] = None,
    twilio_identifiers: Optional[Dict[str, Any]] = None,
    webhook_received_at: Optional[float] = None,
    correlation_id: Optional[str] = None,
) -> None:
    db = SessionLocal() if SessionLocal else None
    start_time = time.monotonic()
    correlation_id = correlation_id or inbound_message_sid or uuid.uuid4().hex[:12]
    queue_delay_ms = int((start_time - webhook_received_at) * 1000) if webhook_received_at else 0
    api_metrics: list[Dict[str, Any]] = []
    session_data = _get_or_create_session(sender_phone)
    inbound_message = None
    conv_for_log = None

    try:
        if db:
            try:
                phone_key = normalize_twilio_phone(sender_phone)
                user = get_or_create_user(db, phone_key, name=profile_name)
                conv = get_or_create_active_conversation(db, user.id)
                conv_for_log = conv.id
                session_data["user_id"] = str(user.id)
                session_data["conversation_id"] = str(conv.id)
                inbound_message = log_message(
                    db,
                    conv_for_log,
                    "inbound",
                    body_text,
                    status="received",
                    twilio_message_sid=inbound_message_sid,
                    correlation_id=correlation_id,
                    metadata_json={
                        "queue_delay_ms": queue_delay_ms,
                        "profile_name": profile_name,
                        "twilio_identifiers": dict(twilio_identifiers or {}),
                    },
                )
            except Exception as exc:
                logger.warning("Database logging (inbound) failed; continuing: %s", exc, exc_info=True)
                db.rollback()
                conv_for_log = None
                inbound_message = None

        logger.info(
            "message_flow_start correlation_id=%s inbound_sid=%s sender=%s queue_delay_ms=%s",
            correlation_id,
            inbound_message_sid or "",
            sender_phone,
            queue_delay_ms,
        )

        # 1. AI Classification
        classification_started = time.monotonic()
        classification_error = None
        try:
            raw_classification = classify(body_text)
            logger.info("AI CLASSIFICATION correlation_id=%s result=%s", correlation_id, raw_classification)
        except Exception as exc:
            classification_error = str(exc)
            logger.error("Classification failed: %s", exc, exc_info=True)
            raw_classification = {"intent": "unknown", "entities": {}, "confidence": 0.0}
        classification_latency_ms = int((time.monotonic() - classification_started) * 1000)
        session_data["last_intent"] = raw_classification.get("intent")

        # Bugfix (Round-3, R3-1): clear the session's selected_event_id when
        # the current message brings any fresh entity / query of its own.
        # Without this clear, a numbered selection ("2") would leak its event
        # id into every subsequent turn — so "where is the temple?" or
        # "when is the holi event?" would silently target the previously
        # selected event instead of the one the user just asked about.
        fresh_entities = (
            (raw_classification.get("entities") or {})
            if isinstance(raw_classification.get("entities"), dict)
            else {}
        )
        if any(fresh_entities.get(k) for k in ("event_name", "program_name", "timeframe")) or len(body_text.split()) > 4:
            session_data["selected_event_id"] = None

        # Bugfix (post-Week 12 audit): support bare numeric replies like "2" as a
        # follow-up to a previously shown event list. The list footer says
        # "1-n for full details" — if the previous turn pushed five IDs into
        # session.last_shown_event_ids, "2" (or "register for 2") should resolve
        # to the second ID. Done here so the classifier does not need list
        # grammar. List-index resolution runs after the selected_event_id clear
        # above so long polite sentences still clear stale picks, then repopulate
        # from the list when a row index is detected.
        stripped = body_text.strip()
        prev_ids = session_data.get("last_shown_event_ids") or []
        selected_id_override: Optional[int] = None
        if stripped.isdigit():
            idx = int(stripped) - 1
            if 0 <= idx < len(prev_ids):
                selected_id_override = prev_ids[idx]
        elif prev_ids:
            pick = _extract_shown_list_index_1based(body_text)
            if pick is not None:
                idx = pick - 1
                if 0 <= idx < len(prev_ids):
                    selected_id_override = prev_ids[idx]
        if selected_id_override is not None:
            logger.info(
                "NUMBERED FOLLOW-UP correlation_id=%s body=%r -> event_id=%s",
                correlation_id,
                body_text,
                selected_id_override,
            )
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
            "api_observer": api_metrics.append,
            "correlation_id": correlation_id,
        }

        # 3. Build Response
        intent_str = raw_classification.get("intent")
        build_latency_ms = 0
        build_error = None

        # Week 12 fix (Bug 4): For clarification / ambiguous / unknown we never
        # call build_response — go straight to the clarification prompt.
        if intent_str in ("clarification_needed", "ambiguous", "unknown"):
            clar_started = time.monotonic()
            ent = raw_classification.get("entities") or {}
            entities_map = ent if isinstance(ent, dict) else {}
            pure_greeting = _is_pure_greeting(body_text, entities_map)
            staff_roster_q = _is_temple_personnel_roster_question(body_text, entities_map)
            pastoral = pastoral_guidance_kind(body_text, entities_map)
            if staff_roster_q:
                reply_text = _build_out_of_scope_reply()
            elif pastoral == "guru_contact":
                reply_text = _build_pastoral_guru_contact_reply()
            elif pastoral == "spiritual_peace":
                reply_text = _build_pastoral_spiritual_peace_reply()
            else:
                reply_text = _build_clarification_reply(pure_greeting=pure_greeting)
            if _llm_routing_available() and not staff_roster_q and pastoral is None:
                try:
                    generated = build_conversational_clarification_reply(
                        body_text,
                        intent_str,
                        raw_classification.get("confidence"),
                        build_clarification_context_block(),
                        pure_greeting=pure_greeting,
                        out_of_scope=False,
                    )
                    if generated and generated.strip():
                        reply_text = generated.strip()
                except Exception as exc:
                    logger.warning("Conversational clarification LLM failed: %s", exc, exc_info=True)
            build_latency_ms = int((time.monotonic() - clar_started) * 1000)
        else:
            build_started = time.monotonic()
            try:
                if _llm_routing_available():
                    built = build_response_with_facts(raw_classification, context)
                    draft = built.draft
                    facts = built.facts or {}
                    try:
                        rewritten = build_grounded_whatsapp_reply(
                            body_text,
                            str(intent_str or ""),
                            raw_classification.get("confidence"),
                            facts,
                        )
                    except Exception as rw_exc:
                        logger.warning("Grounded rewrite failed; using template draft: %s", rw_exc)
                        rewritten = None
                    reply_text = (rewritten or "").strip() or draft
                else:
                    reply_text = build_response(raw_classification, context)
            except Exception as exc:
                build_error = str(exc)
                logger.error("Response Builder Failed: %s", exc, exc_info=True)
                reply_text = ""
            finally:
                build_latency_ms = int((time.monotonic() - build_started) * 1000)

            # 4. Graceful Fallback for empty replies only.
            if not reply_text or len(reply_text.strip()) == 0:
                if build_error is None:
                    build_error = "empty_response"
                reply_text = (
                    "I'm having trouble understanding that right now. "
                    "Try: 'What events are happening this weekend?'"
                )

            # Persist any list-of-event-IDs the response builder showed so the
            # next bare-digit reply ("2") can resolve to one of them.
            if "last_shown_event_ids" in context:
                session_data["last_shown_event_ids"] = list(context.get("last_shown_event_ids") or [])

        # 5. Send Message
        send_started = time.monotonic()
        outbound_sid = None
        send_error = None
        try:
            outbound_sid = send_whatsapp_message(to=sender_phone, body=reply_text)
        except Exception as exc:
            send_error = str(exc)
            logger.error("Failed to send Twilio message: %s", exc, exc_info=True)
        send_latency_ms = int((time.monotonic() - send_started) * 1000)
        total_latency_ms = int((time.monotonic() - start_time) * 1000)
        upstream_api_latency_ms = sum(int(metric.get("elapsed_ms") or 0) for metric in api_metrics)

        if send_error:
            inbound_status = "send_failed"
        elif build_error or classification_error:
            inbound_status = "fallback_sent"
        else:
            inbound_status = "processed"

        _persist_message_update(
            db,
            inbound_message,
            intent=intent_str,
            status=inbound_status,
            failure_reason=send_error or build_error or classification_error,
            total_latency_ms=total_latency_ms,
            metadata_json={
                "queue_delay_ms": queue_delay_ms,
                "classification_latency_ms": classification_latency_ms,
                "response_build_latency_ms": build_latency_ms,
                "upstream_api_latency_ms": upstream_api_latency_ms,
                "send_latency_ms": send_latency_ms,
                "api_calls": api_metrics,
            },
        )

        if db and conv_for_log:
            try:
                log_message(
                    db,
                    conv_for_log,
                    "outbound",
                    reply_text,
                    intent=intent_str,
                    twilio_message_sid=outbound_sid,
                    status="sent" if not send_error else "send_failed",
                    failure_reason=send_error,
                    correlation_id=correlation_id,
                    metadata_json={
                        "send_latency_ms": send_latency_ms,
                        "upstream_api_latency_ms": upstream_api_latency_ms,
                    },
                    total_latency_ms=send_latency_ms,
                )
            except Exception as exc:
                logger.warning("Database logging (outbound) failed: %s", exc, exc_info=True)
                db.rollback()

        logger.info(
            "message_flow_done correlation_id=%s inbound_sid=%s outbound_sid=%s intent=%s queue_delay_ms=%s classify_ms=%s build_ms=%s upstream_api_ms=%s send_ms=%s total_ms=%s api_call_count=%s status=%s",
            correlation_id,
            inbound_message_sid or "",
            outbound_sid or "",
            intent_str,
            queue_delay_ms,
            classification_latency_ms,
            build_latency_ms,
            upstream_api_latency_ms,
            send_latency_ms,
            total_latency_ms,
            len(api_metrics),
            inbound_status,
        )
    finally:
        if db:
            db.close()


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "JKYog Bot is online",
        "environment": os.getenv("ENV", "development"),
    }


@app.get("/health")
async def health():
    snapshot = _readiness_snapshot()
    return {
        "status": "ok",
        "environment": snapshot["environment"],
        "signature_validation": snapshot["signature_validation"],
        "database": snapshot["database"],
    }


@app.get("/ready")
async def ready():
    snapshot = _readiness_snapshot()
    status_code = 200 if snapshot["ready"] else 503
    return JSONResponse(status_code=status_code, content=snapshot)


@app.get("/health/db")
async def health_db():
    snapshot = _database_snapshot()
    status_code = 200 if snapshot.get("healthy") or not snapshot.get("enabled") else 503
    return JSONResponse(status_code=status_code, content=snapshot)


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    webhook_started = time.monotonic()
    form_data = await request.form()
    body_text = form_data.get("Body", "").strip()
    sender_phone = form_data.get("From", "")
    raw_profile = form_data.get("ProfileName")
    profile_name = raw_profile.strip() if isinstance(raw_profile, str) else None
    if profile_name == "":
        profile_name = None
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    inbound_message_sid = form_data.get("MessageSid") or form_data.get("SmsSid")
    correlation_id = inbound_message_sid or uuid.uuid4().hex[:12]
    twilio_identifiers = {
        key: value
        for key in ("MessageSid", "SmsSid", "WaId", "AccountSid")
        if (value := form_data.get(key))
    }

    if _signature_validation_enabled():
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if not auth_token:
            logger.warning(
                "Twilio signature validation misconfigured correlation_id=%s: missing TWILIO_AUTH_TOKEN",
                correlation_id,
            )
            return JSONResponse(
                status_code=503,
                content={"error": "Webhook signature validation is misconfigured"},
            )
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        validator = RequestValidator(auth_token)
        if not validator.validate(url, dict(form_data), signature):
            logger.warning("Invalid Twilio Signature dropped. correlation_id=%s", correlation_id)
            return JSONResponse(status_code=403, content={"error": "Invalid signature"})

    background_tasks.add_task(
        process_message_background,
        body_text,
        sender_phone,
        profile_name,
        inbound_message_sid=inbound_message_sid,
        twilio_identifiers=twilio_identifiers,
        webhook_received_at=webhook_started,
        correlation_id=correlation_id,
    )

    ack_elapsed_ms = int((time.monotonic() - webhook_started) * 1000)
    logger.info(
        "webhook_accepted correlation_id=%s inbound_sid=%s sender=%s ack_ms=%s",
        correlation_id,
        inbound_message_sid or "",
        sender_phone,
        ack_elapsed_ms,
    )
    return JSONResponse(status_code=200, content={"status": "accepted", "correlation_id": correlation_id})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
