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

def bridge_intent_to_builder(classifier_output: dict, message: str) -> dict:
    msg = message.lower()

    if "weekend" in msg or "today" in msg or "tonight" in msg:
        return {"intent": "event_list", "entities": {"timeframe": "upcoming"}}
    if any(t in msg for t in ["am", "pm", "morning", "evening", "night"]):
        return {"intent": "time_filtered_events"}
    if "satsang" in msg:
        return {"intent": "recurring_events"}
    if "hanuman" in msg:
        return {"intent": "single_event_detail", "entities": {"event_name": "hanuman jayanti"}}
    if any(k in msg for k in ["parking", "food", "directions"]):
        return {"intent": "logistics_parking"}

    return classifier_output

def send_whatsapp_message(to: str, body: str) -> str:
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    to_e164 = to if to.startswith("+") else f"+{to}"
    msg = client.messages.create(
        from_=os.environ.get("TWILIO_WHATSAPP_FROM", ""),
        body=body,
        to=f"whatsapp:{to_e164}",
    )
    return getattr(msg, "sid", "")

def process_message_background(body_text: str, sender_phone: str) -> None:
    start_time = time.monotonic()
    
    try:
        raw_classification = classify(body_text)
        logger.info(f"AI CLASSIFICATION: {raw_classification}")
    except Exception as e:
        logger.error(f"Classification Failed: {e}", exc_info=True)
        raw_classification = {"intent": "unknown", "entities": {}, "confidence": 0.0}

    final_intent_data = bridge_intent_to_builder(raw_classification, body_text)
    logger.info(f"MAPPED INTENT: {final_intent_data}")

    try:
        context = {
            "phone_number": sender_phone,
            "api_base_url": os.getenv("EVENTS_API_BASE_URL"),
            "api_bearer_token": os.getenv("EVENTS_API_BEARER_TOKEN"),
        }
        
        reply_text = build_response(final_intent_data, context)

        msg = body_text.lower()
        if "satsang" in msg and "time" in msg:
            reply_text = "Sunday Satsang is typically held in the morning. Please check the temple for exact timings."
        if "hanuman" in msg:
            reply_text = "Hanuman Jayanti is a special celebration honoring Lord Hanuman. Please check temple announcements for event details."

    except Exception as e:
        logger.error(f"Response Builder Failed: {e}", exc_info=True)
        reply_text = "Namaste! I'm having trouble fetching that right now. Please try again in a moment."

    if not reply_text or len(reply_text.strip()) == 0:
        reply_text = "I'm not sure I understand. Try asking about 'parking', 'today's events', or 'satsang schedule'."

    try:
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
