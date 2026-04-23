from fastapi import APIRouter, Request, HTTPException
from ..integrations.stripe import StripeIntegration

router = APIRouter()

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    stripe_integration = StripeIntegration()

    try:
        event = stripe_integration.construct_webhook_event(payload, sig_header)
        result = stripe_integration.handle_webhook_event(event)
        return {"success": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {exc}")