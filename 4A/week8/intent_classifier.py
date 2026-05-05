import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from entity_extractor import extract_entities

load_dotenv()

log = logging.getLogger("intent_classifier")

try:
    from google import genai
    from google.genai import types as genai_types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


# Week 12 fix (Bug 5): Reuse one Gemini client across requests to eliminate
# the 25–30 second TLS / DNS / handshake cost on every cold call. The client
# itself is thread-safe per the google-genai docs, so a module-level singleton
# is appropriate. Setting the API key env var late (via load_dotenv) means we
# build the singleton lazily on first use.
_GEMINI_CLIENT: "Optional[genai.Client]" = None


def _get_gemini_client():
    """Lazy-init module-level Gemini client. Returns None if Gemini is not
    available (SDK missing or no API key)."""
    global _GEMINI_CLIENT
    if not GOOGLE_AVAILABLE:
        return None
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    if _GEMINI_CLIENT is None:
        try:
            _GEMINI_CLIENT = genai.Client(api_key=api_key)
            log.info("Gemini client initialised (singleton).")
        except Exception as exc:  # pragma: no cover — defensive
            log.warning("Gemini client init failed: %s", exc)
            _GEMINI_CLIENT = None
    return _GEMINI_CLIENT


def warm_up() -> bool:
    """Pre-warm the Gemini connection so the first real classification does
    not pay the cold-start cost. Called once at FastAPI startup. Returns
    True on success, False otherwise.
    """
    client = _get_gemini_client()
    if client is None:
        return False
    try:
        # Tiny throwaway call. Single token output keeps cost negligible.
        client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_INTENT", "gemini-2.5-flash-lite"),
            contents="ping",
            config=genai_types.GenerateContentConfig(
                system_instruction="Reply with the single word: pong.",
                temperature=0,
                max_output_tokens=4,
            ),
        )
        log.info("Gemini warm-up OK.")
        return True
    except Exception as exc:
        log.warning("Gemini warm-up failed: %s", exc)
        return False


# -------------------------------
# INTENT KEYWORDS (ALL 8 INTENTS)
# -------------------------------
INTENT_KEYWORDS = {
    "logistics": {
        "parking", "where", "address", "location", "directions",
        "map", "how to get", "route", "food", "prasad"
    },
    "sponsorship": {
        "donate", "donation", "sponsor", "sponsorship",
        "contribute", "seva", "fund", "support",
        # Week 12 fix: include common seva variants
        "annadaan", "annadan", "seva opportunity",
    },
    "discovery": {
        "events", "happening", "going on", "any events",
        "upcoming", "what's happening", "what is happening",
        # Week 12 fix: cover "what's coming up", "anything coming up"
        "coming up", "what's coming", "what is coming", "any upcoming",
        "show me", "list",
    },
    "no_results_check": {
        "3am", "2am", "4am", "midnight", "overnight",
        "late night", "after midnight", "before dawn"
    },
    "time_based": {
        "today", "tomorrow", "tonight", "this week", "this weekend",
        "next week", "date", "time", "when", "schedule",
        "timing", "start time", "end time"
    },
    "event_specific": {
        "event", "program", "festival", "session",
        "workshop", "celebration", "celebrations",
        "retreat", "seminar", "shivir", "yatra",
        # Week 12 fix: classic temple program names that appear as proper
        # event titles ("Sunday Satsang Special", "Aarti Mahotsav")
        "ltp", "life transformation",
    },
    "recurring_schedule": {
        "daily", "every day", "weekly", "every week",
        "every monday", "every tuesday", "every weekend",
        "recurring", "regular", "routine",
        "hours", "open hours", "closing time", "timings",
        # Week 12 fix: common recurring queries
        "temple hours", "schedule today", "what time",
    },
    "ambiguous": {
        "info", "information", "details", "tell me more",
        "help", "something", "stuff", "things",
        "not sure", "anything"
    }
}


# -------------------------------
# SYSTEM PROMPT (LLM)
# -------------------------------
_SYSTEM_PROMPT = """You are an intent classifier for a WhatsApp bot for JKYog Radha Krishna Temple.

Classify the user message into exactly one of these intents:
- time_based
- event_specific
- recurring_schedule
- logistics
- sponsorship
- discovery
- no_results_check
- ambiguous

Respond ONLY with JSON:
{"intent": "<intent>", "confidence": <float>}
"""


# -------------------------------
# HELPERS
# -------------------------------
def tokenize(text: str) -> set:
    """Lowercase, split, and strip surrounding punctuation from each token.

    Week 12 fix (Bug 4 cont'd): Previously `set(text.lower().split())` left
    trailing punctuation attached to words (e.g. "donate?" instead of
    "donate"), so the Jaccard intersection with keyword sets always missed
    when the user ended their message with a question mark. The bot then
    reported confidence 0 for valid messages like "How can I donate?" and
    routed them to clarification.
    """
    import re as _re
    cleaned = _re.sub(r"[^\w\s]", " ", text.lower())
    return {tok for tok in cleaned.split() if tok}


def jaccard_similarity(set1: set, set2: set) -> float:
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def compute_entity_score(entities: dict) -> float:
    entity_values = [
        entities.get("timeframe"),
        entities.get("event_name"),
        entities.get("program_name"),
    ]
    extracted = sum(1 for v in entity_values if v)
    return extracted / len(entity_values)


# -------------------------------
# GEMINI CLASSIFIER (OPTIONAL)
# -------------------------------
def _classify_with_gemini(user_message: str) -> Dict | None:
    """Single Gemini classify call using the singleton client.

    Week 12 fix (Bug 5): Use module-level Gemini singleton instead of
    creating a fresh `genai.Client` on every WhatsApp message. Combined with
    the startup `warm_up()` call, this eliminates the 25-second cold start
    that was breaking Twilio's 15-second webhook timeout.
    """
    client = _get_gemini_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_INTENT", "gemini-2.5-flash-lite"),
            contents=user_message,
            config=genai_types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=60,
            ),
        )

        # Strip markdown fences if Gemini wraps the JSON in ```json ... ```
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].lstrip()

        result = json.loads(raw)
        return {
            "intent": result.get("intent", "ambiguous"),
            "confidence": float(result.get("confidence", 0.0)),
        }

    except Exception as exc:
        log.debug("Gemini classify failed; falling back to Jaccard. %s", exc)
        return None


# -------------------------------
# FIXED JACCARD CLASSIFIER
# -------------------------------
def _classify_with_jaccard(message: str, entities: dict) -> Dict:
    """Keyword + entity heuristic classifier (used as fallback when Gemini
    is unavailable, rate-limited, or returns invalid JSON).

    Returns a dict with `intent`, `confidence`, and `has_signal` — the latter
    is True when at least one keyword or entity match drove the routing
    decision (i.e. we are not in the "guessed ambiguous" branch). Downstream
    logic uses `has_signal` instead of the numeric confidence to decide
    whether to redirect to clarification, because Jaccard's similarity ratio
    against small keyword sets routinely yields scores under 0.20 even on
    correct classifications.
    """
    msg = message.lower()
    tokens = tokenize(message)

    has_signal = True

    # Week 12 fix (Bug 2 cont'd): override clues that flip a program_name
    # match into an event_specific match. The entity extractor's PROGRAM_NAMES
    # list overlaps event titles ("Kirtan" appears in both "Bhakti Kirtans &
    # Satsang" and the recurring program list). When the user adds words like
    # "retreat", "festival", "celebration", "this year", they almost certainly
    # mean a one-off event, not the recurring program.
    EVENT_OVERRIDE_TOKENS = {
        "retreat", "festival", "celebration", "celebrations",
        "yatra", "shivir", "program", "programs", "event", "events",
        "tell", "about",
    }
    msg_tokens = tokens
    has_event_context = any(t in msg_tokens for t in EVENT_OVERRIDE_TOKENS)

    # -------- Intent Routing --------
    # Week 12 fix: program_name (e.g. "Satsang") beats timeframe (e.g.
    # "Sunday") because the entity extractor's date regex over-greedily
    # extracts day-of-week names as timeframes. "When is Sunday Satsang?"
    # had program_name="Satsang" + timeframe="<next sunday>" — without
    # this re-ordering it routed to time_based and queried events for that
    # date instead of the recurring satsang schedule.
    if entities.get("event_name"):
        intent = "event_specific"
    elif entities.get("program_name") and has_event_context:
        # Program-name match but user is asking about a one-off event variant.
        intent = "event_specific"
    elif entities.get("program_name"):
        intent = "recurring_schedule"
    elif entities.get("timeframe"):
        intent = "time_based"
    elif any(word in msg for word in INTENT_KEYWORDS["sponsorship"]):
        intent = "sponsorship"
    elif any(word in msg for word in INTENT_KEYWORDS["no_results_check"]):
        intent = "no_results_check"
    elif any(word in msg for word in INTENT_KEYWORDS["recurring_schedule"]):
        # "daily bhajans" / "temple hours" via keyword path.
        intent = "recurring_schedule"
    elif any(word in msg for word in INTENT_KEYWORDS["discovery"]):
        # Week 12 fix: discovery checked BEFORE event_specific because
        # "events" (plural / general listing) is in the discovery set, while
        # event_specific has "event" (singular). Without this order plurals
        # like "What events are coming up?" would route to event_specific.
        intent = "discovery"
    elif any(word in msg for word in INTENT_KEYWORDS["event_specific"]):
        # Catch "Life Transformation Program", "Spiritual Retreat", "What is
        # the LTP" etc. via the event-name keyword set.
        intent = "event_specific"
    elif any(word in msg for word in INTENT_KEYWORDS["logistics"]):
        intent = "logistics"
    elif any(word in msg for word in INTENT_KEYWORDS["time_based"]):
        # Backstop — "today" / "tomorrow" / "this week".
        intent = "time_based"
    else:
        intent = "ambiguous"
        has_signal = False

    # -------- Scores --------
    keyword_score = jaccard_similarity(tokens, INTENT_KEYWORDS.get(intent, set()))
    entity_score = compute_entity_score(entities)

    if intent in ["event_specific", "time_based", "recurring_schedule"]:
        confidence = 0.6 * entity_score + 0.4 * keyword_score
    elif intent in ["logistics", "sponsorship"]:
        confidence = 0.4 * entity_score + 0.6 * keyword_score
    else:
        confidence = 0.2 * entity_score + 0.8 * keyword_score

    # Week 12 fix: floor non-ambiguous confidence at 0.5 so the downstream
    # threshold gate doesn't kick a *correctly-classified* Jaccard hit to
    # clarification just because the keyword set is small.
    if has_signal:
        confidence = max(confidence, 0.5)

    return {
        "intent": intent,
        "confidence": round(confidence, 2),
        "has_signal": has_signal,
    }


# -------------------------------
# MAIN CLASSIFIER
# -------------------------------

# Week 12 fix (Bug 4): Re-broaden the low-confidence safety net.
#
# Week 11 narrowed clarification to *only* fire when the intent was
# `ambiguous`. That meant a message like "info" classified as `sponsorship`
# at confidence 0.04 still proceeded into the sponsorship branch and returned
# event lists — confusing nonsense.
#
# Replacement strategy: trust the *signal* (did Jaccard / Gemini find a real
# match?) rather than the absolute numeric confidence. Jaccard scores are
# intrinsically small (0.05–0.20) even on correct classifications because the
# similarity ratio is computed against compact keyword sets.
#
# Rules:
#   1. If the classifier returned `intent == "ambiguous"` it found no
#      keyword/entity match — redirect to clarification.
#   2. If Gemini returned an `ambiguous` label with low confidence, redirect
#      to clarification (Gemini knows it doesn't know).
#   3. Otherwise trust the intent — Jaccard / Gemini found real signal.
CLARIFY_THRESHOLD = 0.60


def classify(message: str) -> Dict:
    entities = extract_entities(message)

    ai_result = _classify_with_gemini(message)

    used_jaccard = False
    if not ai_result or ai_result["confidence"] < CLARIFY_THRESHOLD:
        result = _classify_with_jaccard(message, entities)
        used_jaccard = True
    else:
        result = ai_result

    intent = result["intent"]
    confidence = result["confidence"]

    # Rule 1 / 2: route to clarification when the classifier itself signals
    # ambiguity — either Jaccard fell into the "no keyword match" bucket, or
    # Gemini explicitly returned `ambiguous` with low confidence.
    is_ambiguous = (intent == "ambiguous") or (
        not used_jaccard and intent == "ambiguous" and confidence < CLARIFY_THRESHOLD
    )
    if is_ambiguous:
        intent = "clarification_needed"
    elif used_jaccard and not result.get("has_signal", True):
        # Defensive: Jaccard reported no signal but didn't label ambiguous.
        intent = "clarification_needed"

    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "api_call": map_to_api(intent, entities),
    }


# -------------------------------
# API MAPPING
# -------------------------------
def map_to_api(intent: str, entities: dict) -> dict:
    event_name = entities.get("event_name")
    timeframe = entities.get("timeframe")

    if intent == "time_based":
        if timeframe == "today":
            return {
                "endpoint": "/api/v2/events/today",
                "method": "GET",
                "params": {},
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"start_date": timeframe},
        }

    elif intent == "event_specific":
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "resolve_event_id_and_fetch_details",
        }

    elif intent == "recurring_schedule":
        return {
            "endpoint": "/api/v2/events/recurring",
            "method": "GET",
            "params": {},
        }

    elif intent == "logistics":
        if not event_name:
            return {"action": "clarification_needed"}
        return {
            "endpoint": "/api/v2/events/search",
            "method": "GET",
            "params": {"q": event_name},
            "follow_up": "fetch_event_details_for_logistics",
        }

    elif intent == "sponsorship":
        if event_name:
            return {
                "endpoint": "/api/v2/events/search",
                "method": "GET",
                "params": {"q": event_name},
                "follow_up": "extract_sponsorship_tiers",
            }
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5},
        }

    elif intent == "discovery":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 5},
        }

    elif intent == "no_results_check":
        return {
            "endpoint": "/api/v2/events",
            "method": "GET",
            "params": {"limit": 3},
        }

    return {"action": "clarification_needed"}
