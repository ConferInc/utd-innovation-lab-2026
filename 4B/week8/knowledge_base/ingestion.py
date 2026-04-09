"""FAQ + static JSON events + database-backed upcoming events for KB search.

`ingest_events` loads rows produced by the scraper/seed pipeline into an in-memory
document list merged by `build_documents`, so `search_kb` can surface temple events for
Team 4A's intent classifier without relying solely on direct HTTP calls to the events API.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parent
FAQS_PATH = BASE_DIR / "faqs.json"
EVENTS_PATH = BASE_DIR / "events.json"

# Populated by `ingest_events` (typically after seeding from scraped JSON).
_ingested_event_docs: List[Dict[str, Any]] = []


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9']+", _normalize(text))


def _score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """Simple overlap score (works well enough for a prototype)."""
    if not query_tokens or not doc_tokens:
        return 0.0
    q = set(query_tokens)
    d = set(doc_tokens)
    return len(q & d) / len(q | d)


def load_faqs() -> List[Dict[str, Any]]:
    if not FAQS_PATH.exists():
        return []
    data = json.loads(FAQS_PATH.read_text(encoding="utf-8"))
    return data.get("faqs", [])


def load_events() -> List[Dict[str, Any]]:
    if not EVENTS_PATH.exists():
        return []
    data = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    return data.get("events", [])


def clear_ingested_events() -> None:
    """Remove DB-sourced event docs (e.g. before a full re-ingest)."""
    global _ingested_event_docs
    _ingested_event_docs = []


def _tier_snippet(tiers: Any) -> str:
    if not isinstance(tiers, list):
        return ""
    parts: List[str] = []
    for t in tiers:
        if not isinstance(t, dict):
            continue
        name = t.get("tier_name") or t.get("name") or ""
        price = t.get("price")
        desc = t.get("description") or ""
        if price is not None:
            parts.append(f"{name} {price} {desc}".strip())
        else:
            parts.append(f"{name} {desc}".strip())
    return " ".join(parts)


def _event_dict_to_kb_doc(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a serialized API/storage event dict into a search_kb document."""
    eid = event.get("id")
    text_parts = [
        str(event.get("name") or ""),
        str(event.get("subtitle") or ""),
        str(event.get("description") or ""),
        str(event.get("category") or ""),
        str(event.get("notes") or ""),
        str(event.get("location_name") or ""),
        str(event.get("city") or ""),
        str(event.get("recurrence_text") or ""),
        str(event.get("start_datetime") or ""),
        str(event.get("end_datetime") or ""),
        _tier_snippet(event.get("sponsorship_tiers")),
    ]
    text = " ".join(p for p in text_parts if p)
    return {
        "type": "event",
        "id": f"db_event_{eid}" if eid is not None else None,
        "tokens": _tokenize(text),
        "payload": event,
    }


def ingest_events(db: "Session", *, page_size: int = 200) -> int:
    """Load **all** upcoming events via EventService and register them for `search_kb`.

    Paginates with *page_size* until no rows remain so large calendars are fully indexed.
    Replaces any previous ingested DB events in this process for a consistent snapshot.
    """
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    try:
        from events.services.event_service import EventService
    except ImportError:
        from week8.events.services.event_service import EventService

    clear_ingested_events()
    service = EventService(db, cache=None)
    combined: List[Dict[str, Any]] = []
    offset = 0
    while True:
        rows = service.get_upcoming_events(
            limit=page_size, offset=offset, stale_after_days=30
        )
        if not rows:
            break
        combined.extend(_event_dict_to_kb_doc(ev) for ev in rows)
        if len(rows) < page_size:
            break
        offset += page_size
    global _ingested_event_docs
    _ingested_event_docs = combined
    return len(_ingested_event_docs)


def build_documents() -> List[Dict[str, Any]]:
    """Turns FAQs, static JSON events, and ingested DB events into searchable documents."""
    docs: List[Dict[str, Any]] = []

    for faq in load_faqs():
        text = f"{faq.get('question','')} {faq.get('answer','')} {' '.join(faq.get('tags', []))}"
        docs.append(
            {
                "type": "faq",
                "id": faq.get("id"),
                "tokens": _tokenize(text),
                "payload": faq,
            }
        )

    for event in load_events():
        text = f"{event.get('title','')} {event.get('description','')} {event.get('day','')} {event.get('start_time','')} {event.get('end_time','')} {' '.join(event.get('tags', []))}"
        docs.append(
            {
                "type": "event",
                "id": event.get("id"),
                "tokens": _tokenize(text),
                "payload": event,
            }
        )

    docs.extend(_ingested_event_docs)
    return docs


def search_kb(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search FAQs + Events and return the best matches.
    Returns:
      [{"type": "...", "id": "...", "score": 0.12, "payload": {...}}, ...]
    """
    docs = build_documents()
    q_tokens = _tokenize(query)

    scored = []
    for doc in docs:
        s = _score(q_tokens, doc["tokens"])
        scored.append((s, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    results: List[Dict[str, Any]] = []
    for s, doc in scored[:top_k]:
        if s <= 0:
            continue
        results.append(
            {
                "type": doc["type"],
                "id": doc["id"],
                "score": round(s, 4),
                "payload": doc["payload"],
            }
        )

    return results


if __name__ == "__main__":
    # Quick test
    tests = [
        "where is the temple located",
        "temple hours",
        "is parking available",
        "friday satsang",
        "holi mela",
    ]
    for t in tests:
        print("\nQUERY:", t)
        print(search_kb(t, top_k=2))
