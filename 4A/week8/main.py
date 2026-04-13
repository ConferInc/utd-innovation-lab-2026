import os
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from twilio.util import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from .intent_classifier import classify_intent
from .response_builder import build_response

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("4A.main")

app = FastAPI(title="JKYog WhatsApp Bot Layer")

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
VALIDATOR = RequestValidator(TWILIO_AUTH_TOKEN)

def verify_twilio_signature(request_url: str, params: dict, signature: str) -> bool:
    """Verifies that the request actually came from Twilio."""
    return VALIDATOR.validate(request_url, params, signature)

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Main entry point for WhatsApp messages.
    Receives Form-Encoded data from Twilio.
    """
    # 1. Capture the raw form data
    form_data = await request.form()
    params = dict(form_data)
    
    # 2. Security: Verify Twilio Signature
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    
    # Standard Render/Proxy fix: Ensure URL is HTTPS for validation
    if os.getenv("ENV") == "production":
        url = url.replace("http://", "https://")

    if not verify_twilio_signature(url, params, signature):
        logger.warning("Invalid Twilio Signature received.")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 3. Extract Message Content
    user_message = params.get("Body", "").strip()
    sender_phone = params.get("From", "")
    
    logger.info(f"Received message from {sender_phone}: {user_message}")

    # 4. Orchestration Pipeline
    try:
        # Step A: Classify the Intent
        intent_result = classify_intent(user_message)
        
        # Step B: Build the Session Context
        session_context = {
            "phone_number": sender_phone,
            "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
            "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN")
        }

        # Step C: Build the Response (Calls 4B API internally)
        reply_text = build_response(intent_result, session_context)

    except Exception as e:
        logger.error(f"Pipeline Error: {e}")
        # Graceful Fallback (Requirement)
        reply_text = ("I'm having trouble understanding that right now. "
                      "Try: 'What events are happening this weekend?'")

    # 5. Return TwiML Response
    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_text)
    
    return Response(
        content=str(twiml_resp), 
        media_type="application/xml"
    )

@app.get("/health")
def health():
    return {"status": "online", "deployment": "Render"}