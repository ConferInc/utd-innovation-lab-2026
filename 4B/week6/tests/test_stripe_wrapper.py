import pytest
import stripe
from unittest.mock import patch

from service_wrappers.base_wrapper import CircuitBreakerOpenError, NonRetryableServiceError
from service_wrappers.stripe_wrapper import StripeWrapper


def test_stripe_health_check():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.health_check()
    assert result["service"] == "stripe"
    assert result["configured"] is True


def test_stripe_invalid_amount():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.create_payment_intent(0)


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_retry_exhausted_timeout(mock_create):
    mock_create.side_effect = stripe.APIConnectionError(message="timeout")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    with pytest.raises(RuntimeError):
        wrapper.create_payment_intent(1000)


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_rate_limit(mock_create):
    mock_create.side_effect = stripe.RateLimitError(
        message="Too many requests",
        param=None,
    )
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    with pytest.raises(RuntimeError):
        wrapper.create_payment_intent(1000)


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_stripe_circuit_breaker_fail_fast(mock_create):
    mock_create.side_effect = stripe.APIError(message="server down")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            wrapper.create_payment_intent(1000)

    with pytest.raises(CircuitBreakerOpenError):
        wrapper.create_payment_intent(1000)