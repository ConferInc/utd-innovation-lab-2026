import os
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from intent_classifier import classify
from response_builder import build_response

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("4A.main")

app = FastAPI(title="JKYog Bot Orchestrator")

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
VALIDATOR = RequestValidator(TWILIO_AUTH_TOKEN)

def verify_twilio_signature(request_url: str, params: dict, signature: str) -> bool:
    if os.getenv("ENV") != "production":
        return True 
    return VALIDATOR.validate(request_url, params, signature)

def bridge_intent_to_builder(classifier_output: dict, message: str) -> dict:
    """
    Mapping Layer: Bridges Rujul's Intents to Chanakya's Builder logic.
    Also adds keyword-based 'Today/Recurring' overrides.
    """
    msg = message.lower()
    intent = classifier_output.get("intent", "ambiguous")
    
    
    if "today" in msg or "tonight" in msg:
        intent = "today_events"
    elif any(word in msg for word in ["satsang", "recurring", "daily", "aarti"]):
        intent = "recurring_events"
    
    
    mapping = {
        "time_based": "today_events",
        "event_specific": "single_event_detail",
        "recurring_schedule": "recurring_events",
        "logistics": "logistics_parking",
        "sponsorship": "sponsorship_tiers",
        "discovery": "event_list",
        "no_results_check": "event_list",
        "ambiguous": "event_list",
        "clarification_needed": "event_list"
    }
    
    classifier_output["intent"] = mapping.get(intent, "event_list")
    return classifier_output

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    params = dict(form_data)
    
    
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    if os.getenv("ENV") == "production":
        url = url.replace("http://", "https://")

    if not verify_twilio_signature(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Signature")

    user_message = params.get("Body", "").strip()
    sender = params.get("From", "")

    try:
        
        raw_intent = classify(user_message)
        mapped_intent = bridge_intent_to_builder(raw_intent, user_message)
        
        logger.info(f"RAW INTENT: {raw_intent}")
        logger.info(f"MAPPED INTENT: {mapped_intent}")
        
        context = {
            "phone_number": sender,
            "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
            "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN")
        }

        reply_text = build_response(mapped_intent, context)

    except Exception as e:
        logger.error(f"Logic Error: {e}")
        reply_text = "I'm having trouble with my temple records. Try: 'What events are happening this weekend?'"

    
    twiml = MessagingResponse()
    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")

@app.get("/health")
def health():
    return {"status": "ok", "team": "4A"}
