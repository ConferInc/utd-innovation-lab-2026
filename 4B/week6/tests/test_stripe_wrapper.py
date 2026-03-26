import pytest
import stripe
from unittest.mock import patch, MagicMock

from service_wrappers.base_wrapper import CircuitBreakerOpenError, NonRetryableServiceError
from service_wrappers.stripe_wrapper import StripeWrapper


# --- health check ---

def test_stripe_health_check():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.health_check()
    assert result["service"] == "stripe"
    assert result["configured"] is True


# --- success ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_success(mock_create):
    mock_create.return_value = {"id": "pi_123", "amount": 1000}
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.create_payment_intent(amount=1000)
    assert result["id"] == "pi_123"
    assert result["amount"] == 1000


# --- non-retryable: invalid amount ---

def test_stripe_invalid_amount():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.create_payment_intent(0)


# --- timeout / retry exhaustion ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_retry_exhausted_timeout(mock_create):
    mock_create.side_effect = stripe.APIConnectionError(message="timeout")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    with pytest.raises(RuntimeError):
        wrapper.create_payment_intent(1000)


# --- rate limit (429) ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_rate_limit(mock_create):
    mock_create.side_effect = stripe.RateLimitError(message="Too many requests")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    with pytest.raises(RuntimeError):
        wrapper.create_payment_intent(1000)


# --- circuit breaker (retries=3, threshold=3 => opens after 1 failed call) ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_stripe_circuit_breaker_fail_fast(mock_create):
    mock_create.side_effect = stripe.APIError(message="server down")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    with pytest.raises(RuntimeError):
        wrapper.create_payment_intent(1000)

    with pytest.raises(CircuitBreakerOpenError):
        wrapper.create_payment_intent(1000)


# --- retrieve_payment_intent ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.retrieve")
def test_retrieve_payment_intent_success(mock_retrieve):
    mock_retrieve.return_value = {"id": "pi_456", "status": "succeeded"}
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.retrieve_payment_intent("pi_456")
    assert result["id"] == "pi_456"


def test_retrieve_payment_intent_missing_id():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.retrieve_payment_intent("")


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.retrieve")
def test_retrieve_payment_intent_retry_exhausted(mock_retrieve):
    mock_retrieve.side_effect = stripe.APIConnectionError(message="timeout")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(RuntimeError):
        wrapper.retrieve_payment_intent("pi_456")


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.retrieve")
def test_retrieve_payment_intent_invalid_request(mock_retrieve):
    mock_retrieve.side_effect = stripe.InvalidRequestError(
        message="No such payment_intent", param="id"
    )
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.retrieve_payment_intent("pi_bad")


# --- create_checkout_session ---

@patch("service_wrappers.stripe_wrapper.stripe.checkout.Session.create")
def test_create_checkout_session_success(mock_create):
    mock_create.return_value = {"id": "cs_123", "url": "https://checkout.stripe.com/x"}
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.create_checkout_session(
        success_url="https://example.com/ok",
        cancel_url="https://example.com/cancel",
        amount=2000,
    )
    assert result["id"] == "cs_123"


def test_create_checkout_session_invalid_amount():
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.create_checkout_session(
            success_url="https://example.com/ok",
            cancel_url="https://example.com/cancel",
            amount=0,
        )


@patch("service_wrappers.stripe_wrapper.stripe.checkout.Session.create")
def test_create_checkout_session_retry_exhausted(mock_create):
    mock_create.side_effect = stripe.APIConnectionError(message="timeout")
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(RuntimeError):
        wrapper.create_checkout_session(
            success_url="https://example.com/ok",
            cancel_url="https://example.com/cancel",
            amount=2000,
        )


# --- invalid request error path on create_payment_intent ---

@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_invalid_request(mock_create):
    mock_create.side_effect = stripe.InvalidRequestError(
        message="Invalid currency", param="currency"
    )
    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.create_payment_intent(1000)
