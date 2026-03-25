import pytest
from unittest.mock import patch, MagicMock

from service_wrappers.base_wrapper import CircuitBreakerOpenError, NonRetryableServiceError
from service_wrappers.maps_wrapper import MapsWrapper


# --- health check ---

@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_health_check(mock_client_class):
    wrapper = MapsWrapper(api_key="dummy")
    result = wrapper.health_check()
    assert result["service"] == "google_maps"
    assert result["configured"] is True


# --- success ---

@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_geocode_success(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.return_value = [{"formatted_address": "Dallas, TX"}]
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")
    result = wrapper.geocode("Dallas")

    assert "results" in result
    assert result["results"][0]["formatted_address"] == "Dallas, TX"


# --- non-retryable: invalid input ---

@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_invalid_geocode(mock_client_class):
    wrapper = MapsWrapper(api_key="dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.geocode("")


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_invalid_directions(mock_client_class):
    wrapper = MapsWrapper(api_key="dummy")
    with pytest.raises(NonRetryableServiceError):
        wrapper.directions("", "dest")
    with pytest.raises(NonRetryableServiceError):
        wrapper.directions("origin", "")


# --- timeout / retry exhaustion ---

@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_geocode_retry_exhausted_timeout(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.side_effect = TimeoutError("timeout")
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")

    with pytest.raises(RuntimeError):
        wrapper.geocode("Dallas")


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_directions_retry_exhausted_timeout(mock_client_class):
    mock_client = MagicMock()
    mock_client.directions.side_effect = TimeoutError("timeout")
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")

    with pytest.raises(RuntimeError):
        wrapper.directions("Dallas", "Austin")


# --- circuit breaker (retries=3, threshold=3 => opens after 1 failed call) ---

@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_maps_circuit_breaker_fail_fast(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.side_effect = TimeoutError("timeout")
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")

    with pytest.raises(RuntimeError):
        wrapper.geocode("Dallas")

    with pytest.raises(CircuitBreakerOpenError):
        wrapper.geocode("Dallas")
