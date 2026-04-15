import os
import logging
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from dotenv import load_dotenv

from intent_classifier import classify
from response_builder import build_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("4A.main")

load_dotenv()

app = FastAPI()

def bridge_intent_to_builder(classifier_output: dict, message: str) -> dict:
    msg = message.lower()

    if "weekend" in msg or "today" in msg or "tonight" in msg:
        return {"intent": "event_list", "entities": {"timeframe": "upcoming"}}

    if "satsang" in msg:
        return {"intent": "recurring_events"}

    if "hanuman" in msg:
        return {"intent": "single_event_detail", "entities": {"event_name": "hanuman jayanti"}}

    if any(k in msg for k in ["parking", "food", "directions"]):
        return {"intent": "logistics_parking"}

    return classifier_output


@app.get("/")
async def root():
    return {
        "status": "JKYog Bot is online",
        "environment": os.getenv("ENV", "development"),
    }


@app.post("/webhook")
async def webhook(request: Request):
    form_data = await request.form()
    body_text = form_data.get("Body", "").strip()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if os.getenv("ENV") == "production":
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)

        validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
        if not validator.validate(url, dict(form_data), signature):
            logger.warning("Invalid Twilio Signature")

    try:
        raw_classification = classify(body_text)
        logger.info(f"RAW AI OUTPUT: {raw_classification}")
    except Exception as e:
        logger.error(f"AI Classification Failed: {e}")
        raw_classification = {"intent": "unknown", "entities": {}}

    final_intent_data = bridge_intent_to_builder(raw_classification, body_text)
    logger.info(f"FINAL MAPPED INTENT: {final_intent_data}")

    try:
        context = {
            "phone_number": form_data.get("From"),
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
        logger.error(f"Response Builder Failed: {e}")
        reply_text = "Namaste! I'm having trouble fetching that right now. Please try again in a moment."

    if not reply_text or len(reply_text.strip()) == 0:
        reply_text = "I'm not sure I understand. Try asking about 'parking', 'today's events', or 'satsang schedule'."

    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_text)

    return Response(
        content=str(twiml_resp),
        media_type="application/xml"
    )
