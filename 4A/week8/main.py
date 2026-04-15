import os
import json
import logging
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from dotenv import load_dotenv

# Import team modules (Ensure these are in the same 4A/week8 folder)
from intent_classifier import classify
from response_builder import build_response

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("4A.main")

load_dotenv()

app = FastAPI()

def bridge_intent_to_builder(classifier_output: dict, message: str) -> dict:
    """
    Acts as a safety net between the AI classifier and the response builder.
    """
    msg = message.lower()
    raw_intent = classifier_output.get("intent", "unknown")

    # 🔥 FORCE correct behavior for demo via keywords
    if any(k in msg for k in ["today", "weekend", "happening"]):
        classifier_output["intent"] = "today_events"
        return classifier_output

    if any(k in msg for k in ["satsang", "aarti", "schedule", "timings"]):
        classifier_output["intent"] = "recurring_events"
        return classifier_output

    if any(k in msg for k in ["parking", "food", "directions", "where"]):
        classifier_output["intent"] = "logistics_parking"
        return classifier_output

    if "about" in msg or "tell me about" in msg:
        classifier_output["intent"] = "single_event_detail"
        return classifier_output

    # Mapping AI categories to builder categories
    mapping = {
        "event_query": "event_search",
        "faq_query": "logistics_parking",
        "greeting": "event_list",
        "donation_request": "sponsorship_tiers",
        "directions_request": "logistics_parking",
        "unknown": "event_list",
    }

    classifier_output["intent"] = mapping.get(raw_intent, "event_list")
    return classifier_output

@app.get("/")
async def root():
    return {"status": "JKYog Bot is online", "environment": os.getenv("ENV", "development")}

@app.post("/webhook")
async def webhook(request: Request):
    # 1. Capture the incoming message
    form_data = await request.form()
    body_text = form_data.get("Body", "").strip()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    # 2. Security Validation (Checks if request is actually from Twilio)
    if os.getenv("ENV") == "production":
        # Render often uses http internally; we must check for https for the signature
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        
        validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
        if not validator.validate(url, dict(form_data), signature):
            logger.warning("Invalid Twilio Signature")
            # return Response(status_code=403) # Uncomment to enforce security

    # 3. Classify Intent using AI (Rujul's code + Google API Key)
# Inside your webhook function, change Step 3 to this:
    try:
        # Pass the message body to the AI classifier
        raw_classification = classify(body_text)
        logger.info(f"RAW AI OUTPUT: {raw_classification}")
    except Exception as e:
        logger.error(f"AI Classification Failed: {e}")
        raw_classification = {"intent": "unknown", "entities": {}}
    # 4. Apply the Bridge (Keyword Safety Net)
    final_intent_data = bridge_intent_to_builder(raw_classification, body_text)
    logger.info(f"FINAL MAPPED INTENT: {final_intent_data}")

    # 5. Generate Response (Team 4B API or Local Logic)

# 5. Generate Response (Team 4B API or Local Logic)
    try:
        context = {
            "phone_number": form_data.get("From"),
            "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
            "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN")
        }
    
     
    
        reply_text = build_response(final_intent_data, context)
    
     
    
    except Exception as e:
        logger.error(f"Response Builder Failed: {e}")
        reply_text = "Namaste! I'm having trouble fetching that right now. Please try again in a moment."



    # 6. Fallback if reply is empty
    if not reply_text or len(reply_text.strip()) == 0:
        reply_text = "I'm not sure I understand. Try asking about 'parking', 'today's events', or 'satsang schedule'."

    # 7. Send back to WhatsApp
    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_text)
    
    return Response(
        content=str(twiml_resp), 
        media_type="application/xml"
    )
