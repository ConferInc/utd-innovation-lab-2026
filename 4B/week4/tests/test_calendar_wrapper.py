import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from service_wrappers.base_wrapper import CircuitBreakerOpenError, NonRetryableServiceError
from service_wrappers.calendar_wrapper import CalendarWrapper


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_calendar_health_check(mock_creds, mock_build):
    mock_build.return_value = MagicMock()
    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")
    result = wrapper.health_check()
    assert result["service"] == "google_calendar"
    assert result["configured"] is True


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_calendar_create_event_invalid_summary(mock_creds, mock_build):
    mock_build.return_value = MagicMock()
    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")

    with pytest.raises(NonRetryableServiceError):
        wrapper.create_event("", datetime.utcnow())


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_calendar_list_events_retry_exhausted(mock_creds, mock_build):
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_events.list.return_value.execute.side_effect = TimeoutError("timeout")
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")

    with pytest.raises(RuntimeError):
        wrapper.list_events()


@patch("service_wrappers.calendar_wrapper.build")
@patch("service_wrappers.calendar_wrapper.Credentials.from_service_account_file")
def test_calendar_circuit_breaker_fail_fast(mock_creds, mock_build):
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_events.list.return_value.execute.side_effect = TimeoutError("timeout")
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    wrapper = CalendarWrapper(credentials_file="dummy.json", calendar_id="primary")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            wrapper.list_events()

    with pytest.raises(CircuitBreakerOpenError):
        wrapper.list_events()