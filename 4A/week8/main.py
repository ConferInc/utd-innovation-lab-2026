import os
import logging
import time
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from dotenv import load_dotenv

from intent_classifier import classify
from response_builder import build_response

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

load_dotenv()

app = FastAPI(title="JKYog WhatsApp Bot")

def send_whatsapp_message(to: str, body: str) -> str:
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    
    # Safely format the WhatsApp number to prevent Twilio 400 errors
    formatted_to = to if to.startswith("whatsapp:") else f"whatsapp:{to if to.startswith('+') else '+' + to}"
    
    msg = client.messages.create(
        from_=os.environ.get("TWILIO_WHATSAPP_FROM", ""),
        body=body,
        to=formatted_to,
    )
    return getattr(msg, "sid", "")

def process_message_background(body_text: str, sender_phone: str) -> None:
    start_time = time.monotonic()
    
    try:
        # 1. Let the AI (Gemini) completely classify the intent
        intent_data = classify(body_text)
        logger.info(f"AI CLASSIFICATION: {intent_data}")
    except Exception as e:
        logger.error(f"Classification Failed: {e}", exc_info=True)
        intent_data = {"intent": "unknown", "entities": {}, "confidence": 0.0}

    try:
        context = {
            "phone_number": sender_phone,
            "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
            "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN"),
        }
        
        # 2. Pass the AI's exact intent straight to the builder to fetch from the API
        reply_text = build_response(intent_data, context)

    except Exception as e:
        logger.error(f"Response Builder Failed: {e}", exc_info=True)
        reply_text = "Namaste! I'm having trouble fetching that right now. Please try again in a moment."

    if not reply_text or len(reply_text.strip()) == 0:
        reply_text = "I'm not sure I understand. Try asking about 'parking', 'today's events', or 'satsang schedule'."

    try:
        # 3. Send the real API response to Twilio
        send_whatsapp_message(to=sender_phone, body=reply_text)
        elapsed = int((time.monotonic() - start_time) * 1000)
        logger.info(f"Message processed and sent successfully in {elapsed}ms to {sender_phone}")
    except Exception as e:
        logger.error(f"Failed to send Twilio message: {e}", exc_info=True)

@app.get("/")
async def root():
    return {
        "status": "JKYog Bot is online",
        "environment": os.getenv("ENV", "development"),
    }

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    body_text = form_data.get("Body", "").strip()
    sender_phone = form_data.get("From", "")
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if os.getenv("ENV") == "production":
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
        if not validator.validate(url, dict(form_data), signature):
            logger.warning("Invalid Twilio Signature dropped.")
            return JSONResponse(status_code=403, content={"error": "Invalid signature"})

    background_tasks.add_task(process_message_background, body_text, sender_phone)
    
    return JSONResponse(status_code=200, content={"status": "accepted"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
