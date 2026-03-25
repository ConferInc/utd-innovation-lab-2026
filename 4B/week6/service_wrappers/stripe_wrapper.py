import os
import logging
from typing import Any, Dict, Optional

import stripe

from .base_wrapper import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    NonRetryableServiceError,
    with_retry,
)

logger = logging.getLogger(__name__)


class StripeWrapper:
    """
    Wrapper around Stripe SDK with retry, circuit breaker, and error handling.
    """

    def __init__(self, secret_key: Optional[str] = None) -> None:
        self.secret_key = secret_key or os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30)

        if not self.secret_key:
            logger.error("StripeWrapper init failed: STRIPE_SECRET_KEY missing")
            raise ValueError("STRIPE_SECRET_KEY is not set")

        stripe.api_key = self.secret_key
        logger.info("StripeWrapper initialized")

    def health_check(self) -> Dict[str, Any]:
        return {
            "service": "stripe",
            "configured": bool(self.secret_key),
            "publishable_key_present": bool(self.publishable_key),
            "circuit_open": self.circuit_breaker.is_open(),
        }

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
            return with_retry(
                _call,
                operation_name="create_payment_intent",
                service_name="stripe",
                retries=3,
                delay=1.0,
                retry_exceptions=(
                    stripe.APIConnectionError,
                    stripe.APIError,
                    stripe.RateLimitError,
                ),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "StripeWrapper create_payment_intent failed fast amount=%s currency=%s",
                amount,
                currency,
            )
            raise
        except stripe.InvalidRequestError as exc:
            logger.exception(
                "StripeWrapper invalid request amount=%s currency=%s",
                amount,
                currency,
            )
            raise NonRetryableServiceError(str(exc)) from exc
        except stripe.StripeError as exc:
            logger.exception(
                "StripeWrapper create_payment_intent failed amount=%s currency=%s",
                amount,
                currency,
            )
            raise RuntimeError(f"Stripe error: {str(exc)}") from exc

    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        if not payment_intent_id:
            raise NonRetryableServiceError("payment_intent_id is required")

        def _call() -> Dict[str, Any]:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return dict(intent)

        try:
            return with_retry(
                _call,
                operation_name="retrieve_payment_intent",
                service_name="stripe",
                retries=3,
                delay=1.0,
                retry_exceptions=(
                    stripe.APIConnectionError,
                    stripe.APIError,
                    stripe.RateLimitError,
                ),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "StripeWrapper retrieve_payment_intent failed fast payment_intent_id=%s",
                payment_intent_id,
            )
            raise
        except stripe.InvalidRequestError as exc:
            logger.exception(
                "StripeWrapper invalid retrieve payment_intent_id=%s",
                payment_intent_id,
            )
            raise NonRetryableServiceError(str(exc)) from exc
        except stripe.StripeError as exc:
            logger.exception(
                "StripeWrapper retrieve_payment_intent failed payment_intent_id=%s",
                payment_intent_id,
            )
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
            return with_retry(
                _call,
                operation_name="create_checkout_session",
                service_name="stripe",
                retries=3,
                delay=1.0,
                retry_exceptions=(
                    stripe.APIConnectionError,
                    stripe.APIError,
                    stripe.RateLimitError,
                ),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "StripeWrapper create_checkout_session failed fast amount=%s currency=%s product_name=%s",
                amount,
                currency,
                product_name,
            )
            raise
        except stripe.InvalidRequestError as exc:
            logger.exception(
                "StripeWrapper invalid checkout session amount=%s currency=%s product_name=%s",
                amount,
                currency,
                product_name,
            )
            raise NonRetryableServiceError(str(exc)) from exc
        except stripe.StripeError as exc:
            logger.exception(
                "StripeWrapper create_checkout_session failed amount=%s currency=%s product_name=%s",
                amount,
                currency,
                product_name,
            )
            raise RuntimeError(f"Stripe error: {str(exc)}") from exc