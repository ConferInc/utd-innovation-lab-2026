"""
Response Builder for JKYog WhatsApp Bot
Rohan Kothapalli - Week 3 Assignment

Orchestrates bot responses by routing to appropriate handlers based on intent
and integrating with all teammate modules (knowledge base, database, integrations).
"""

import sys
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, r'C:\Users\rohan\Downloads\Week3 Files')

from bot.intent_classifier import classify_intent
from bot.entity_extractor import extract_entities

# Import teammate modules
try:
    from knowledge_base.ingestion import search_kb
except ImportError:
    print("Warning: knowledge_base module not found")
    def search_kb(query, top_k=3):
        return []

try:
    from integrations.google_maps import get_temple_directions_from_user_location
except ImportError:
    print("Warning: google_maps integration not found")
    def get_temple_directions_from_user_location(user_location, temple_address, mode="driving"):
        return f"🗺️ Directions from {user_location} to {temple_address} (integration unavailable)"

try:
    from integrations.stripe import get_donation_link
except ImportError:
    print("Warning: stripe integration not found")
    def get_donation_link(temple_slug=None):
        return "https://buy.stripe.com/test_default"

try:
    from integrations.calendar import get_upcoming_events, get_events_on_date
except ImportError:
    print("Warning: calendar integration not found")
    def get_upcoming_events(limit=5):
        return []
    def get_events_on_date(date_str):
        return []


# Temple address constant
TEMPLE_ADDRESS = "1450 North Watters Road, Allen, TX 75013"
TEMPLE_NAME = "JKYog Radha Krishna Temple"


def handle_greeting(user_context: Optional[Dict] = None) -> str:
    """
    Handle greeting intent.
    
    Returns a welcoming message introducing the bot.
    """
    greeting = "🙏 Namaste! Welcome to JKYog Radha Krishna Temple.\n\n"
    greeting += "I can help you with:\n"
    greeting += "• Temple information (location, hours, dress code)\n"
    greeting += "• Event schedules (satsang, bhajans, special events)\n"
    greeting += "• Directions to the temple\n"
    greeting += "• Donation information\n\n"
    greeting += "How can I assist you today?"
    
    return greeting


def handle_faq_query(user_message: str, entities: Dict) -> str:
    """
    Handle FAQ query intent.
    
    Searches the knowledge base for relevant FAQs.
    """
    results = search_kb(user_message, top_k=3)
    
    if not results or len(results) == 0:
        return "I don't have specific information about that. Please contact the temple directly at (469) 606-3119 or visit jkyog.org."
    
    # Format the top result
    top_result = results[0]
    
    if top_result["type"] == "faq":
        faq = top_result["payload"]
        response = f"📚 {faq.get('answer', '')}\n\n"
        
        # Add additional context if available
        if len(results) > 1:
            response += "Related information:\n"
            for i, result in enumerate(results[1:3], 1):
                if result["type"] == "faq":
                    related_faq = result["payload"]
                    response += f"• {related_faq.get('question', '')}\n"
        
        return response
    
    return "I found some information but couldn't format it properly. Please contact the temple for details."


def handle_event_query(user_message: str, entities: Dict) -> str:
    """
    Handle event query intent.
    
    Searches for events in the knowledge base and calendar integration.
    """
    # Search knowledge base for events
    results = search_kb(user_message, top_k=3)
    
    # Filter for event results
    event_results = [r for r in results if r["type"] == "event"]
    
    if not event_results:
        # Try calendar integration
        if "date" in entities:
            calendar_events = get_events_on_date(entities["date"])
        else:
            calendar_events = get_upcoming_events(limit=5)
        
        if calendar_events:
            response = "📅 Upcoming Events:\n\n"
            for event in calendar_events[:3]:
                response += f"• {event.get('summary', 'Event')}\n"
                response += f"  {event.get('start', '')}\n"
                if event.get('location'):
                    response += f"  📍 {event['location']}\n"
                response += "\n"
            return response
        else:
            return "I couldn't find specific event information. Please check our website at jkyog.org or call (469) 606-3119."
    
    # Format event results from knowledge base
    response = "📅 Events:\n\n"
    
    for result in event_results[:3]:
        event = result["payload"]
        response += f"🔸 {event.get('title', 'Event')}\n"
        
        if event.get('description'):
            response += f"   {event['description']}\n"
        
        # Format timing
        if event.get('day'):
            response += f"   📆 {event['day']}"
            if event.get('start_time'):
                response += f" at {event['start_time']}"
            if event.get('end_time'):
                response += f" - {event['end_time']}"
            response += "\n"
        
        if event.get('location'):
            response += f"   📍 {event['location']}\n"
        
        response += "\n"
    
    return response


def handle_donation(entities: Dict) -> str:
    """
    Handle donation request intent.
    
    Provides donation link via Stripe integration.
    """
    response = "🙏 Thank you for your generous support!\n\n"
    
    # Get donation link
    donation_link = get_donation_link(temple_slug="dallas")
    
    response += f"You can make a donation here:\n{donation_link}\n\n"
    response += "Your contributions help us:\n"
    response += "• Maintain the temple facilities\n"
    response += "• Organize spiritual programs\n"
    response += "• Serve the community\n\n"
    response += "All donations are tax-deductible. 💝"
    
    return response


def handle_directions(user_message: str, entities: Dict) -> str:
    """
    Handle directions request intent.
    
    Provides directions using Google Maps integration.
    """
    user_location = entities.get("location", "your location")
    
    response = f"🗺️ Directions to {TEMPLE_NAME}:\n\n"
    response += f"Address: {TEMPLE_ADDRESS}\n\n"
    
    # Get directions from Google Maps
    if entities.get("location"):
        directions = get_temple_directions_from_user_location(
            user_location=user_location,
            temple_address=TEMPLE_ADDRESS
        )
        response += directions
    else:
        response += "📍 The temple is located in Allen, Texas.\n\n"
        response += "For turn-by-turn directions, please share your starting location or use this address in your GPS:\n"
        response += f"{TEMPLE_ADDRESS}\n\n"
        response += "🅿️ Ample parking is available on-site."
    
    return response


def handle_unknown(user_message: str) -> str:
    """
    Handle unknown intent (fallback).
    
    Provides helpful guidance when the bot doesn't understand.
    """
    response = "I'm not sure I understood that. 🤔\n\n"
    response += "I can help you with:\n"
    response += "• Temple information (location, hours, facilities)\n"
    response += "• Event schedules and timings\n"
    response += "• Directions to the temple\n"
    response += "• Donation information\n\n"
    response += "For other inquiries, please contact:\n"
    response += "📞 (469) 606-3119\n"
    response += "🌐 jkyog.org"
    
    return response


def build_response(user_message: str, user_context: Optional[Dict] = None) -> str:
    """
    Build complete bot response by orchestrating the full pipeline.
    
    Pipeline:
    1. Classify intent
    2. Extract entities
    3. Route to appropriate handler
    4. Format response for WhatsApp
    
    Args:
        user_message: The user's input message
        user_context: Optional context (user_id, conversation_id, etc.)
    
    Returns:
        Formatted response string ready for WhatsApp
    
    Example:
        >>> build_response("Where is the temple?")
        "📚 The JKYog Radha Krishna Temple is located in Allen, Texas at..."
    """
    if not user_message or not user_message.strip():
        return handle_unknown(user_message)
    
    try:
        # Step 1: Classify intent
        intent_result = classify_intent(user_message)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        # Log for debugging (in production, log to database)
        print(f"Intent: {intent}, Confidence: {confidence:.2f}")
        
        # Step 2: Extract entities
        entities = extract_entities(user_message, intent)
        print(f"Entities: {entities}")
        
        # Step 3: Route to handler based on intent
        if intent == "greeting":
            response = handle_greeting(user_context)
        
        elif intent == "faq_query":
            response = handle_faq_query(user_message, entities)
        
        elif intent == "event_query":
            response = handle_event_query(user_message, entities)
        
        elif intent == "donation_request":
            response = handle_donation(entities)
        
        elif intent == "directions_request":
            response = handle_directions(user_message, entities)
        
        else:  # unknown intent
            response = handle_unknown(user_message)
        
        # Add confidence disclaimer for medium confidence
        if 0.3 <= confidence < 0.7 and intent != "unknown":
            response += "\n\n---\nIf this isn't what you were looking for, please rephrase your question or contact us at (469) 606-3119."
        
        return response
    
    except Exception as e:
        print(f"Error in build_response: {e}")
        return "I'm experiencing technical difficulties. Please try again or contact the temple at (469) 606-3119."


if __name__ == "__main__":
    # Test the response builder
    test_messages = [
        "Hello",
        "Where is the temple?",
        "What time is Friday satsang?",
        "How do I donate?",
        "Directions from Dallas",
        "What's the weather?",
    ]
    
    print("\n=== Response Builder Test ===\n")
    for message in test_messages:
        print(f"USER: {message}")
        print(f"BOT: {build_response(message)}")
        print("\n" + "="*50 + "\n")
