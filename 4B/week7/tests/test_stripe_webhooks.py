import pytest
import importlib.util
from pathlib import Path

stripe_path = Path(__file__).resolve().parents[1] / "integrations" / "stripe.py"
spec = importlib.util.spec_from_file_location("stripe_module", stripe_path)
stripe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stripe_module)

StripeIntegration = stripe_module.StripeIntegration


def test_handle_payment_intent_succeeded():
    stripe_integration = StripeIntegration()

    event = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_123",
                "amount": 5000,
                "currency": "usd",
            }
        },
    }

    result = stripe_integration.handle_webhook_event(event)

    assert result["status"] == "processed"
    assert result["event_type"] == "payment_intent.succeeded"
    assert result["payment_intent_id"] == "pi_123"
    assert result["amount"] == 5000
    assert result["currency"] == "usd"
    assert result["message"] == "Payment succeeded."


def test_handle_payment_intent_payment_failed():
    stripe_integration = StripeIntegration()

    event = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_456",
                "amount": 3000,
                "currency": "usd",
                "last_payment_error": {
                    "message": "Your card was declined."
                },
            }
        },
    }

    result = stripe_integration.handle_webhook_event(event)

    assert result["status"] == "processed"
    assert result["event_type"] == "payment_intent.payment_failed"
    assert result["payment_intent_id"] == "pi_456"
    assert result["amount"] == 3000
    assert result["currency"] == "usd"
    assert result["failure_message"] == "Your card was declined."
    assert result["message"] == "Payment failed."


def test_handle_unknown_event_type():
    stripe_integration = StripeIntegration()

    event = {
        "type": "customer.created",
        "data": {
            "object": {
                "id": "cus_123"
            }
        },
    }

    result = stripe_integration.handle_webhook_event(event)

    assert result["status"] == "ignored"
    assert result["event_type"] == "customer.created"
    assert result["message"] == "Unhandled event type."


def test_construct_webhook_event_missing_signature():
    stripe_integration = StripeIntegration()

    with pytest.raises(ValueError, match="Missing Stripe-Signature header."):
        stripe_integration.construct_webhook_event(b"{}", None)