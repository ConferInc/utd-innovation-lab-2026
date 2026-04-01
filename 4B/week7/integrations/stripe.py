"""
Stripe Payment Links - Donationsm + Webhook Handling
Subodh Krishna Nikumbh - Week 3 JKYog WhatsApp Bot
No API key needed - uses pre-created Stripe Payment Links
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    import stripe
except ImportError:
    stripe = None

# Pre-created Stripe Payment Links (team configures URLs)
DONATION_LINKS = {
    "default": os.getenv("STRIPE_DEFAULT_LINK", "https://buy.stripe.com/test_co_8wE4..."),
    "dallas": os.getenv("STRIPE_DALLAS_LINK", "https://buy.stripe.com/test_dallas"),
    "irving": os.getenv("STRIPE_IRVING_LINK", "https://buy.stripe.com/test_irving"),
    "houston": os.getenv("STRIPE_HOUSTON_LINK", "https://buy.stripe.com/test_houston"),
}


def get_donation_link(temple_slug: Optional[str] = None) -> str:
    """Rohan's bot entrypoint - returns donation URL"""
    if temple_slug:
        link = DONATION_LINKS.get(temple_slug.lower())
        if link and link.startswith("https://buy.stripe.com"):
            return link
    
    return DONATION_LINKS["default"] + "\n\n💝 Thank you for your support!"


class StripeIntegration:
    """Stripe integration for payment intents, donation links, and webhooks."""

    def __init__(self) -> None:
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if stripe and self.secret_key:
            stripe.api_key = self.secret_key

    def create_payment_intent(self, amount: int, currency: str = "usd") -> object:
        """Create a Stripe PaymentIntent. Returns an object with client_secret.
        Requires STRIPE_SECRET_KEY in env. If not set, returns a placeholder.
        """
        if not stripe or not self.secret_key:
            return type("Intent", (), {"client_secret": None})()

        try:
            intent = stripe.PaymentIntent.create(amount = amount, currency = currency)
            return intent
        except Exception: 
            return type("Intent", (), {"client_secret": None})()
        
        
    def construct_webhook_event(self, payload: bytes, sig_header: Optional[str]) -> Dict[str, Any]:
        """
        Verify Stripe signature and construct the event.
        Raises ValueError if config is missing or signature is invalid.
        """
        if not stripe:
            raise ValueError("Stripe library is not installed.")

        if not self.webhook_secret:
            raise ValueError("Missing STRIPE_WEBHOOK_SECRET.")

        if not sig_header:
            raise ValueError("Missing Stripe-Signature header.")

        if not payload:
            raise ValueError("Missing webhook payload.")
        
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=self.webhook_secret,
            )
            return event
        except Exception as exc:
            raise ValueError(f"Invalid Stripe webhook: {exc}") from exc

    def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle supported Stripe webhook event types.
        """
        event_type = event.get("type")
        data_object = event.get("data", {}).get("object", {})

        if event_type == "payment_intent.succeeded":
            return {
                "status": "processed",
                "event_type": event_type,
                "payment_intent_id": data_object.get("id"),
                "amount": data_object.get("amount"),
                "currency": data_object.get("currency"),
                "message": "Payment succeeded.",
            }

        if event_type == "payment_intent.payment_failed":
            last_error = data_object.get("last_payment_error", {}) or {}
            return {
                "status": "processed",
                "event_type": event_type,
                "payment_intent_id": data_object.get("id"),
                "amount": data_object.get("amount"),
                "currency": data_object.get("currency"),
                "failure_message": last_error.get("message"),
                "message": "Payment failed.",
            }

        return {
            "status": "ignored",
            "event_type": event_type,
            "message": "Unhandled event type.",
        }
    
        