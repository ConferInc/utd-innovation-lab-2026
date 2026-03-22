from unittest.mock import patch, MagicMock

from service_wrappers.calendar_wrapper import CalendarWrapper


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_list_events_success(mock_creds, mock_build):
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_events.list.return_value.execute.return_value = {"items": [{"id": "1"}]}
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")
    result = wrapper.list_events()

    assert "events" in result
    assert result["events"][0]["id"] == "1"