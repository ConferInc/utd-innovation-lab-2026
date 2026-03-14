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
