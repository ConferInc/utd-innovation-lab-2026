"""
Stripe Payment Links - Donations
Subodh Krishna Nikumbh - Week 3 JKYog WhatsApp Bot
No API key needed - uses pre-created Stripe Payment Links
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

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
    """Stripe integration for payment intents and donation links."""

    def create_payment_intent(self, amount: int, currency: str = "usd") -> object:
        """Create a Stripe PaymentIntent. Returns an object with client_secret.
        Requires STRIPE_SECRET_KEY in env. If not set, returns a placeholder.
        """
        secret = os.getenv("STRIPE_SECRET_KEY")
        if not secret:
            return type("Intent", (), {"client_secret": None})()
        try:
            import stripe
            stripe.api_key = secret
            intent = stripe.PaymentIntent.create(amount=amount, currency=currency)
            return intent
        except Exception:
            return type("Intent", (), {"client_secret": None})()
