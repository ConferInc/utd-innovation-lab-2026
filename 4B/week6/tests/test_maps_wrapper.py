from unittest.mock import patch, MagicMock

from service_wrappers.maps_wrapper import MapsWrapper


@patch("service_wrappers.maps_wrapper.googlemaps.Client")
def test_geocode_success(mock_client_class):
    mock_client = MagicMock()
    mock_client.geocode.return_value = [{"formatted_address": "Dallas, TX"}]
    mock_client_class.return_value = mock_client

    wrapper = MapsWrapper(api_key="dummy")
    result = wrapper.geocode("Dallas")

    assert "results" in result
    assert result["results"][0]["formatted_address"] == "Dallas, TX"