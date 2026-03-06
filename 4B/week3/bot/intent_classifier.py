"""
Intent Classifier for JKYog WhatsApp Bot
Rohan Kothapalli - Week 3 Assignment

Classifies user messages into intents using OpenAI text-embedding-3-small
with keyword fallback for when API is unavailable.
"""

import os
import re
from typing import Dict, List, Tuple

import numpy as np
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available, using keyword fallback only")

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = None
if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Intent definitions with training examples
INTENT_EXAMPLES = {
    "faq_query": [
        "Where is the temple located?",
        "What are the temple hours?",
        "Is there a dress code?",
        "Is parking available?",
        "What is the temple address?",
        "When is the temple open?",
        "What should I wear to the temple?",
        "Can I park at the temple?",
        "What philosophy does JKYog follow?",
        "Tell me about the temple location",
    ],
    "event_query": [
        "When is the next satsang?",
        "What time is Friday satsang?",
        "Tell me about Holi Mela",
        "Are there any upcoming events?",
        "When are the bhajans?",
        "What events are happening this week?",
        "Sunday satsang timings",
        "Daily meditation schedule",
        "Event calendar",
    ],
    "donation_request": [
        "How do I donate?",
        "I want to make a donation",
        "Can I contribute?",
        "Payment link for donation",
        "Support the temple",
        "How to give donation?",
        "I want to help financially",
    ],
    "directions_request": [
        "How do I get to the temple?",
        "Directions to the temple",
        "Where is the temple from Dallas?",
        "How to reach the temple?",
        "Route to JKYog temple",
        "Navigation to temple",
        "Directions from Irving",
    ],
    "greeting": [
        "Hello",
        "Hi",
        "Hey",
        "Namaste",
        "Good morning",
        "Good evening",
        "Hari Om",
        "Radhe Radhe",
    ],
}

# Keyword patterns for fallback
KEYWORD_PATTERNS = {
    "faq_query": [
        r"\b(where|location|address|hours?|timings?|open|close|dress code|parking|philosophy)\b",
        r"\b(temple|visit|visiting)\b",
    ],
    "event_query": [
        r"\b(satsang|event|bhajan|mela|holi|meditation|kirtan|schedule|calendar)\b",
        r"\b(when|what time|upcoming|next|today|tomorrow)\b",
    ],
    "donation_request": [
        r"\b(donat(e|ion)|contribut(e|ion)|payment|support|give|fund|help financially)\b",
    ],
    "directions_request": [
        r"\b(direction|route|navigation|how to (get|reach)|way to|from)\b",
        r"\b(temple|location)\b",
    ],
    "greeting": [
        r"\b(hello|hi|hey|namaste|greetings?|good (morning|evening|afternoon))\b",
        r"\b(hari om|radhe radhe)\b",
    ],
}

# Cache for embeddings
_embedding_cache: Dict[str, List[Tuple[str, np.ndarray]]] = {}


def _get_embedding(text: str) -> np.ndarray:
    """Get embedding for a text using OpenAI API."""
    if not client:
        return None
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def _initialize_embeddings():
    """Pre-compute embeddings for all training examples."""
    global _embedding_cache
    
    if not client or _embedding_cache:
        return
    
    print("Initializing intent classifier embeddings...")
    for intent, examples in INTENT_EXAMPLES.items():
        _embedding_cache[intent] = []
        for example in examples:
            embedding = _get_embedding(example)
            if embedding is not None:
                _embedding_cache[intent].append((example, embedding))
    
    print(f"Loaded embeddings for {len(_embedding_cache)} intent types")


def _classify_with_embeddings(user_message: str) -> Dict[str, any]:
    """Classify intent using OpenAI embeddings."""
    if not _embedding_cache:
        _initialize_embeddings()
    
    if not _embedding_cache:
        return None
    
    # Get embedding for user message
    message_embedding = _get_embedding(user_message)
    if message_embedding is None:
        return None
    
    # Find best matching intent
    best_intent = "unknown"
    best_score = 0.0
    
    for intent, examples in _embedding_cache.items():
        for example_text, example_embedding in examples:
            similarity = _cosine_similarity(message_embedding, example_embedding)
            if similarity > best_score:
                best_score = similarity
                best_intent = intent
    
    return {
        "intent": best_intent,
        "confidence": float(best_score)
    }


def _classify_with_keywords(user_message: str) -> Dict[str, any]:
    """Classify intent using keyword patterns (fallback)."""
    message_lower = user_message.lower()
    
    intent_scores = {}
    
    for intent, patterns in KEYWORD_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, message_lower, re.IGNORECASE)
            score += len(matches)
        
        if score > 0:
            intent_scores[intent] = score
    
    if not intent_scores:
        return {
            "intent": "unknown",
            "confidence": 0.0
        }
    
    # Get intent with highest score
    best_intent = max(intent_scores, key=intent_scores.get)
    max_score = intent_scores[best_intent]
    
    # Normalize confidence (keyword matching is less confident than embeddings)
    confidence = min(0.6, 0.3 + (max_score * 0.1))
    
    return {
        "intent": best_intent,
        "confidence": float(confidence)
    }


def classify_intent(user_message: str) -> Dict[str, any]:
    """
    Classify user message into an intent category.
    
    Uses OpenAI text-embedding-3-small for semantic matching with fallback
    to keyword-based classification if API is unavailable.
    
    Args:
        user_message: The user's input message
    
    Returns:
        Dictionary with:
        - intent: One of faq_query, event_query, donation_request, 
                  directions_request, greeting, unknown
        - confidence: Float between 0.0 and 1.0
    
    Example:
        >>> classify_intent("Where is the temple?")
        {"intent": "faq_query", "confidence": 0.85}
    """
    if not user_message or not user_message.strip():
        return {
            "intent": "unknown",
            "confidence": 0.0
        }
    
    # Try embeddings first
    result = _classify_with_embeddings(user_message)
    
    # Fall back to keywords if embeddings fail
    if result is None:
        result = _classify_with_keywords(user_message)
    
    # If confidence is too low, mark as unknown
    if result["confidence"] < 0.3:
        result["intent"] = "unknown"
    
    return result


if __name__ == "__main__":
    # Test the intent classifier
    test_messages = [
        "Where is the temple located?",
        "What time is Friday satsang?",
        "How do I donate?",
        "Directions from Irving",
        "Hello",
        "What's the weather like?",
        "When does the temple open?",
        "Tell me about Holi Mela",
    ]
    
    print("\n=== Intent Classifier Test ===\n")
    for message in test_messages:
        result = classify_intent(message)
        print(f"Message: {message}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print()
