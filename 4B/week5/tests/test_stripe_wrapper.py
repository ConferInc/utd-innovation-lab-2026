from unittest.mock import patch, MagicMock

from service_wrappers.stripe_wrapper import StripeWrapper


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_create_payment_intent_success(mock_create):
    mock_create.return_value = {"id": "pi_123", "amount": 1000}

    wrapper = StripeWrapper(secret_key="sk_test_dummy")
    result = wrapper.create_payment_intent(amount=1000)

    assert result["id"] == "pi_123"
    assert result["amount"] == 1000