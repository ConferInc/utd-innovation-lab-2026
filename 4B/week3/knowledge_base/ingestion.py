import json
import re
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent
FAQS_PATH = BASE_DIR / "faqs.json"
EVENTS_PATH = BASE_DIR / "events.json"


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


def build_documents() -> List[Dict[str, Any]]:
    """Turns FAQs + Events into searchable documents."""
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