from unittest.mock import patch, MagicMock

from service_wrappers.stripe_wrapper import StripeWrapper
from service_wrappers.maps_wrapper import MapsWrapper
from service_wrappers.calendar_wrapper import CalendarWrapper


@patch("service_wrappers.stripe_wrapper.stripe.PaymentIntent.create")
def test_stripe_wrapper_integration_mocked(mock_create):
    mock_create.return_value = {"id": "pi_123", "amount": 1000}
    wrapper = StripeWrapper(secret_key="sk_test_dummy")

    result = wrapper.create_payment_intent(1000)
    assert result["id"] == "pi_123"


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_wrapper_integration_mocked(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.return_value = [{"formatted_address": "Dallas, TX"}]
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")
    result = wrapper.geocode("Dallas")

    assert result["results"][0]["formatted_address"] == "Dallas, TX"


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_calendar_wrapper_integration_mocked(mock_creds, mock_build):
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_events.list.return_value.execute.return_value = {"items": [{"id": "evt_1"}]}
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")
    result = wrapper.list_events()

    assert result["events"][0]["id"] == "evt_1"
