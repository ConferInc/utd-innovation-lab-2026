import json
import logging
import os
import re
from typing import Any, Dict, Iterable, Mapping, Optional
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


# Messages that clearly ask for the event catalog (never treat as "spiritual only").
_EXPLICIT_EVENT_BROWSE = re.compile(
    r"\b("
    r"events?|upcoming|calendar|what'?s\s+on|what\s+is\s+on|any\s+events|"
    r"list\s+(of\s+)?events|show\s+me\s+events|happening|coming\s+up|"
    r"this\s+weekend|tonight|today|tomorrow|schedule"
    r")\b",
    re.IGNORECASE,
)

# Spiritual / counseling tone without an operational event request → do not browse GET /events.
_SPIRITUAL_NON_EVENT = re.compile(
    r"\b("
    r"inner\s+peace|achieve\s+peace|find\s+peace|world\s+peace|"
    r"enlightenment|atman|self\s+real|self[-\s]?realization|moksha|liberation|"
    r"purpose\s+of\s+life|meaning\s+of\s+life|"
    r"soul\b|spiritual\s+growth|spiritual\s+path|"
    r"peace\s+for\s+others|happiness\s+for\s+others|"
    r"how\s+do\s+i\s+achieve\s+peace|how\s+can\s+i\s+achieve\s+peace"
    r")\b",
    re.IGNORECASE,
)

# "Talk to baba / guru …" is not venue logistics when no event is in play.
_GURU_CONTACT_CHITCHAT = re.compile(
    r"\b(how|where)\s+(do|can)\s+i\s+(talk|speak|meet|see|reach|contact)\b"
    r".{0,48}\b(baba|guruji?|swami|maharaj|sadhguru|saint|guru)\b",
    re.IGNORECASE,
)


def _should_clarify_instead_of_event_catalog(message: str, entities: Mapping[str, Any]) -> bool:
    if entities.get("event_name") or entities.get("program_name"):
        return False
    if _EXPLICIT_EVENT_BROWSE.search(message):
        return False
    return bool(_SPIRITUAL_NON_EVENT.search(message))


def _should_clarify_guru_contact_without_event(message: str, intent: str, entities: Mapping[str, Any]) -> bool:
    if intent != "logistics":
        return False
    if entities.get("event_name"):
        return False
    lowered = message.lower()
    if any(h in lowered for h in ("parking", "food", "prasad", "address", "directions", "route", "map")):
        return False
    return bool(_GURU_CONTACT_CHITCHAT.search(message))


def _is_temple_personnel_roster_question(message: str, entities: Mapping[str, Any]) -> bool:
    """Staff / guru counts — not in API facts; must not trigger event listings."""
    if entities.get("event_name") or entities.get("program_name"):
        return False
    if _EXPLICIT_EVENT_BROWSE.search(message):
        return False
    lowered = message.lower()
    place = bool(
        re.search(r"\b(temple|allen|dallas|radha\s+krishna|jk\s*yog)\b", lowered)
        or re.search(r"\b(at|in)\s+the\s+temple\b", lowered)
    )
    if not place:
        return False
    if re.search(
        r"\bhow\s+many\b.{0,120}\b("
        r"gurus?|spiritual\s+teachers?|teachers?|swamis?|maharaj(?:as|es)?|"
        r"priests?|pandits?|monks?|acharyas?|saints?|leaders?|instructors?"
        r")\b",
        lowered,
    ):
        return True
    if re.search(
        r"\b(who\s+are|who\s+is)\b.{0,120}\b("
        r"gurus?|spiritual\s+teachers?|swamis?|maharaj|priests?|pandits?"
        r")\b",
        lowered,
    ):
        return True
    if re.search(
        r"\b(list|names?\s+of)\b.{0,80}\b("
        r"gurus?|spiritual\s+teachers?|swamis?|maharaj|staff|priests?"
        r")\b",
        lowered,
    ):
        return True
    return False


def pastoral_guidance_kind(message: str, entities: Mapping[str, Any]) -> Optional[str]:
    """Detect chit-chat that gets a fixed warm reply (no generic 'did not understand').

    Returns guru_contact, spiritual_peace, or None.
    """
    if entities.get("event_name") or entities.get("program_name"):
        return None
    if _EXPLICIT_EVENT_BROWSE.search(message):
        return None
    if _GURU_CONTACT_CHITCHAT.search(message):
        return "guru_contact"
    if _SPIRITUAL_NON_EVENT.search(message):
        return "spiritual_peace"
    lowered = message.lower()
    if re.search(r"\b(find(ing)?|seek(ing)?)\s+peace\b", lowered):
        return "spiritual_peace"
    if re.search(r"\bhow\s+can\s+i\s+find\s+peace\b", lowered):
        return "spiritual_peace"
    return None


# Standalone hi/hello/etc. must not hit discovery → generic event list (LLMs often over-label).
_PURE_GREETING_FORBIDDEN = frozenset(
    {
        "events",
        "event",
        "upcoming",
        "calendar",
        "parking",
        "donate",
        "donation",
        "sponsor",
        "sponsorship",
        "seva",
        "schedule",
        "logistics",
        "address",
        "directions",
        "temple",
        "when",
        "where",
        "weekend",
        "tonight",
        "tomorrow",
        "today",
        "week",
        "list",
        "show",
        "happening",
        "programs",
        "program",
        "festival",
        "time",
        "tell",
        "need",
        "want",
        "looking",
        "find",
        "info",
        "details",
        "help",
        "something",
        "coming",
        "this",
        "next",
        "maybe",
        "please",
        "pls",
        "can",
        "could",
        "would",
        "about",
        "park",
        "cost",
        "price",
        "much",
    }
)

_PURE_GREETING_ALLOWED = frozenset(
    {
        "hi",
        "hello",
        "hey",
        "hiya",
        "howdy",
        "yo",
        "sup",
        "gm",
        "gn",
        "good",
        "morning",
        "afternoon",
        "evening",
        "day",
        "there",
        "friend",
        "friends",
        "everyone",
        "ji",
        "namaste",
        "namaskar",
        "radhe",
        "jai",
        "shri",
        "krishna",
        "hari",
        "bol",
        "haribol",
        "how",
        "are",
        "you",
        "u",
        "your",
        "doing",
        "is",
        "it",
        "its",
        "a",
        "the",
        "to",
        "all",
        "ya",
        "yah",
        "yup",
        "nope",
        "yes",
        "no",
        "ok",
        "okay",
        "thanks",
        "thank",
        "very",
        "much",
        "sir",
        "madam",
        "whats",
        "up",
        "going",
        "hows",
        "again",
        "back",
        "here",
        "do",
        "i",
    }
)

_GREETING_STEMS = frozenset(
    {
        "hi",
        "hello",
        "hey",
        "hiya",
        "howdy",
        "yo",
        "sup",
        "gm",
        "gn",
        "good",
        "namaste",
        "namaskar",
        "radhe",
        "haribol",
        "jai",
        "shri",
        "krishna",
        "hari",
        "how",
        "thanks",
        "thank",
        "ok",
        "okay",
    }
)


def _is_pure_greeting(message: str, entities: Mapping[str, Any]) -> bool:
    """True when the message is only small-talk / greeting with no operational ask."""
    if entities.get("event_name") or entities.get("program_name") or entities.get("timeframe"):
        return False
    if _EXPLICIT_EVENT_BROWSE.search(message):
        return False
    raw = message.strip().lower()
    if not raw or len(raw) > 96:
        return False
    compact = re.sub(r"[''`]", "", raw)
    compact = re.sub(r"[^\w\s]", " ", compact)
    tokens = [t for t in compact.split() if t]
    if not tokens or len(tokens) > 12:
        return False
    for t in tokens:
        if t in _PURE_GREETING_FORBIDDEN:
            return False
        if t not in _PURE_GREETING_ALLOWED:
            return False
    if not (set(tokens) & _GREETING_STEMS):
        return False
    return True


def _is_likely_gibberish(message: str) -> bool:
    """Heuristic for random keyboard input (e.g. sdfghj) — letters but no vowels."""
    letters = re.sub(r"[^a-zA-Z]", "", message).lower()
    if len(letters) < 5:
        return False
    vowels = frozenset("aeiouy")
    return not any(ch in vowels for ch in letters)


# -------------------------------
# SYSTEM PROMPT (LLM)
# -------------------------------
_SYSTEM_PROMPT = """You are an intent classifier for a WhatsApp bot for Radha Krishna Temple of Dallas (Allen, TX).

Classify the user message into exactly one of these intents:
- time_based
- event_specific
- recurring_schedule
- logistics
- sponsorship
- discovery
- no_results_check
- ambiguous

Important: If the user is mainly asking for personal spiritual philosophy, inner peace, enlightenment,
life counseling, or generic "how to help the world" guidance — and they are NOT asking what is on the
temple calendar, for parking/food/registration for an event, for recurring program times, or for
donation logistics — choose intent "ambiguous" with confidence below 0.35. Do not label those as
discovery or event_specific just because the temple runs programs.

If the message is ONLY a short greeting or salutation (e.g. "hi", "hello", "hey there", "good morning",
"namaste", "radhe radhe") with no question about events, schedule, parking, donations, or a named
program — choose intent "ambiguous" with confidence below 0.35. Do NOT use "discovery" for bare
greetings.

Questions about how many gurus/spiritual teachers/staff are at the temple, or who they are by name
roster — choose intent "ambiguous" below 0.35 (not discovery); the bot has no staff directory in its data.

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
# OLLAMA CLOUD CLASSIFIER (FALLBACK)
# -------------------------------
# Bugfix (Round-3, R3-6): Gemini's free-tier daily quota is 20 requests/day
# on `gemini-2.5-flash-lite`, so production runs hit 429 by lunchtime. We
# add a second LLM tier using Ollama Cloud's OpenAI-compatible API. The
# classifier tries Gemini → Ollama Cloud → Jaccard, in that order, so a
# Gemini quota miss no longer collapses to keyword-only matching.
#
# Auth: bearer key in `OLLAMA_CLOUD_API_KEY`.
# Endpoint: `https://ollama.com/v1/chat/completions` (OpenAI-compatible).
# Default model: `gemma3:4b` (small, fast, well-suited to a tiny
# JSON-classification prompt). Override via `OLLAMA_CLOUD_MODEL` if a
# larger model is desired (e.g. `gpt-oss:20b`, `qwen3-coder-next`,
# `glm-5`, `kimi-k2:1t`).
_OLLAMA_CLOUD_BASE = "https://ollama.com/v1"
_OLLAMA_CLOUD_DEFAULT_MODEL = "gemma3:4b"


def _classify_with_ollama_cloud(user_message: str) -> Dict | None:
    api_key = (
        os.getenv("OLLAMA_CLOUD_API_KEY")
        or os.getenv("OLLAMA_API_KEY")
        # Backwards compat: an earlier draft of this adapter used ZAI_API_KEY.
        or os.getenv("ZAI_API_KEY")
    )
    if not api_key:
        return None

    base = (os.getenv("OLLAMA_CLOUD_BASE_URL") or _OLLAMA_CLOUD_BASE).rstrip("/")
    model = os.getenv("OLLAMA_CLOUD_MODEL") or _OLLAMA_CLOUD_DEFAULT_MODEL
    url = f"{base}/chat/completions"

    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 60,
        # Ollama-Cloud-specific: ask the model to keep the response short by
        # giving the system prompt and user message verbatim.
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        # Lazy import so the module loads cleanly when httpx isn't present
        # (e.g. constrained test environments).
        import httpx
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            log.debug("Ollama Cloud classify HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        # Strip ``` fences in case the model emits markdown-wrapped JSON.
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].lstrip()
        # Some models include leading whitespace or a thinking preamble —
        # locate the first JSON object in the response.
        first_brace = content.find("{")
        if first_brace > 0:
            content = content[first_brace:]
        last_brace = content.rfind("}")
        if last_brace >= 0:
            content = content[: last_brace + 1]
        result = json.loads(content)
        return {
            "intent": result.get("intent", "ambiguous"),
            "confidence": float(result.get("confidence", 0.0)),
            "_source": "ollama_cloud",
        }
    except Exception as exc:
        log.debug("Ollama Cloud classify failed; continuing fallback chain. %s", exc)
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
    # Bugfix (post-Week-12 audit): the Jaccard score must compare tokens
    # against a *tokenised* keyword set. Previously some entries in
    # INTENT_KEYWORDS were multi-word phrases like "any events" or "what's
    # happening" — they routed correctly via the substring scan above, but
    # they could never enter the Jaccard intersection (since `tokens` is a
    # set of single words). They DID inflate the union, structurally
    # depressing Jaccard scores. Splitting on whitespace and merging back
    # into a flat single-word set fixes both halves of the bug.
    keyword_set_flat = _flatten_keyword_set(INTENT_KEYWORDS.get(intent, set()))
    keyword_score = jaccard_similarity(tokens, keyword_set_flat)
    entity_score = compute_entity_score(entities)

    if intent in ["event_specific", "time_based", "recurring_schedule"]:
        confidence = 0.6 * entity_score + 0.4 * keyword_score
    elif intent in ["logistics", "sponsorship"]:
        confidence = 0.4 * entity_score + 0.6 * keyword_score
    else:
        confidence = 0.2 * entity_score + 0.8 * keyword_score

    # Bugfix (post-Week-12 audit): the previous `max(confidence, 0.5)` floor
    # was a workaround for the multi-word-keyword bug above — once that's
    # fixed, the raw Jaccard+entity blend produces honest values in the
    # 0.10–0.95 range. The downstream clarification gate no longer relies on
    # this number at all (it routes on `intent == "ambiguous"` and the
    # `has_signal` flag), so dropping the floor exposes real signal without
    # changing routing.

    return {
        "intent": intent,
        "confidence": round(confidence, 2),
        "has_signal": has_signal,
    }


def _flatten_keyword_set(keywords: Iterable) -> set:
    """Split multi-word keyword entries into individual tokens.

    INTENT_KEYWORDS doubles as (a) a substring set for routing and (b) the
    keyword reference set for Jaccard scoring. The two uses pull in opposite
    directions: routing wants whole phrases like "any events" so they match
    contiguously in `msg`, but Jaccard wants single tokens so they can match
    the tokenised user message. This helper produces the single-token view.
    """
    flat: set = set()
    for entry in keywords:
        for word in str(entry).lower().split():
            if word:
                flat.add(word)
    return flat


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
    local_result = _classify_with_jaccard(message, entities)

    # Week 13 improvement: obvious local/entity-backed routes should not pay
    # Gemini latency. If the deterministic classifier found real signal, trust
    # it first and reserve LLM calls for the genuinely ambiguous/no-signal
    # branch.
    if (
        local_result.get("intent") != "ambiguous"
        and local_result.get("has_signal", True)
    ):
        result = local_result
        used_jaccard = True
    else:
        # LLM tier 1: Gemini, but only for messages local rules could not route.
        ai_result = _classify_with_gemini(message)
        if ai_result and ai_result["confidence"] >= CLARIFY_THRESHOLD:
            result = ai_result
            used_jaccard = False
        else:
            result = local_result
            used_jaccard = True

    # LLM tier 2: Ollama Cloud — only as a *tie-breaker* when Gemini didn't
    # answer AND our Jaccard heuristic produced no clear signal (the
    # "ambiguous, no keyword/entity match" branch). Used this way it
    # rescues genuinely-unmatchable messages instead of overriding
    # correct rule-based answers like "Sunday Satsang -> recurring_schedule"
    # with whatever label gemma3:4b feels like emitting at conf=0.95.
    # Bugfix (Round-3, R3-6): the previous version called Ollama Cloud
    # whenever Gemini's confidence was below 0.6, which let the cloud
    # model overwrite Jaccard's correct answers and broke the regression
    # suite (32/32 -> 17/32).
    if (
        used_jaccard
        and (result.get("intent") == "ambiguous" or not result.get("has_signal", True))
    ):
        cloud = _classify_with_ollama_cloud(message)
        if cloud and cloud.get("confidence", 0.0) >= CLARIFY_THRESHOLD:
            result = cloud
            used_jaccard = False  # cloud answered with confidence

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

    # LLMs sometimes label broad spiritual/counseling questions as discovery,
    # which triggers a generic upcoming-events list. Force clarification when
    # the text is clearly non-operational and the user did not ask for a
    # calendar-style browse. Same for "talk to baba" mis-routed as logistics
    # without an event (otherwise the bot dumps the static temple block).
    if intent not in ("clarification_needed", "unknown"):
        if intent in ("discovery", "no_results_check") and _should_clarify_instead_of_event_catalog(
            message, entities
        ):
            intent = "clarification_needed"
        elif _should_clarify_guru_contact_without_event(message, intent, entities):
            intent = "clarification_needed"

    # Bare "hello" / "good morning" etc. must not become discovery → event catalog
    # when an LLM tier overconfidently labels small talk.
    if intent not in ("clarification_needed", "unknown") and _is_pure_greeting(message, entities):
        intent = "clarification_needed"
        confidence = min(float(confidence or 0.0), 0.55)

    # Random keyboard-style input (no vowels) — never dump the events list.
    if intent not in ("clarification_needed", "unknown") and _is_likely_gibberish(message):
        intent = "clarification_needed"
        confidence = min(float(confidence or 0.0), 0.55)

    # Staff / guru roster questions — not in event API; never browse events.
    if intent not in ("clarification_needed", "unknown") and _is_temple_personnel_roster_question(
        message, entities
    ):
        intent = "clarification_needed"
        confidence = min(float(confidence or 0.0), 0.55)

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
