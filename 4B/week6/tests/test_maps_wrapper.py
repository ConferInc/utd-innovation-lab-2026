import pytest
from unittest.mock import patch, MagicMock

from service_wrappers.base_wrapper import CircuitBreakerOpenError, NonRetryableServiceError
from service_wrappers.maps_wrapper import MapsWrapper


def test_maps_health_check():
    wrapper = MapsWrapper(api_key="dummy")
    result = wrapper.health_check()
    assert result["service"] == "google_maps"
    assert result["configured"] is True


def test_maps_invalid_geocode():
    wrapper = MapsWrapper(api_key="dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.geocode("")


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_geocode_retry_exhausted_timeout(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.side_effect = TimeoutError("timeout")
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")

    with pytest.raises(RuntimeError):
        wrapper.geocode("Dallas")


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_circuit_breaker_fail_fast(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.side_effect = TimeoutError("timeout")
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            wrapper.geocode("Dallas")

    with pytest.raises(CircuitBreakerOpenError):
        wrapper.geocode("Dallas")