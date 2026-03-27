import os
import logging
from typing import Any, Dict, Optional

import stripe

from .base_wrapper import with_retry, NonRetryableServiceError

logger = logging.getLogger(__name__)


class StripeWrapper:
    """
    Wrapper around Stripe SDK with retry and error handling.
    """

    def __init__(self, secret_key: Optional[str] = None) -> None:
        self.secret_key = secret_key or os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")

        if not self.secret_key:
            raise ValueError("STRIPE_SECRET_KEY is not set")

        stripe.api_key = self.secret_key

    def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        if amount <= 0:
            raise NonRetryableServiceError("Amount must be greater than 0")

        def _call() -> Dict[str, Any]:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )
            return dict(intent)

        try:
            return with_retry(_call, retries=3, delay=1.0, retry_exceptions=(stripe.APIConnectionError, stripe.APIError))
        except stripe.StripeError as exc:
            logger.exception("Stripe create_payment_intent failed")
            raise RuntimeError(f"Stripe error: {str(exc)}") from exc

    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        if not payment_intent_id:
            raise NonRetryableServiceError("payment_intent_id is required")

        def _call() -> Dict[str, Any]:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return dict(intent)

        try:
            return with_retry(_call, retries=3, delay=1.0, retry_exceptions=(stripe.APIConnectionError, stripe.APIError))
        except stripe.StripeError as exc:
            logger.exception("Stripe retrieve_payment_intent failed")
            raise RuntimeError(f"Stripe error: {str(exc)}") from exc

    def create_checkout_session(
        self,
        success_url: str,
        cancel_url: str,
        amount: int,
        product_name: str = "Service Payment",
        currency: str = "usd",
    ) -> Dict[str, Any]:
        if amount <= 0:
            raise NonRetryableServiceError("Amount must be greater than 0")

        def _call() -> Dict[str, Any]:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {"name": product_name},
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return dict(session)

        try:
            return with_retry(_call, retries=3, delay=1.0, retry_exceptions=(stripe.APIConnectionError, stripe.APIError))
        except stripe.StripeError as exc:
            logger.exception("Stripe create_checkout_session failed")
            raise RuntimeError(f"Stripe error: {str(exc)}") from exc

