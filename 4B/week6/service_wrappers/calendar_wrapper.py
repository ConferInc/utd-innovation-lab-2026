import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .base_wrapper import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    NonRetryableServiceError,
    with_retry,
)

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarWrapper:
    """
    Wrapper around Google Calendar API with retry, circuit breaker, and error handling.
    """

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> None:
        self.credentials_file = credentials_file
        self.calendar_id = calendar_id
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30)

        if not self.credentials_file:
            logger.error("CalendarWrapper init failed: credentials_file missing")
            raise ValueError("credentials_file is required")

        creds = Credentials.from_service_account_file(
            self.credentials_file, scopes=SCOPES
        )
        self.service = build("calendar", "v3", credentials=creds)
        logger.info("CalendarWrapper initialized calendar_id=%s", self.calendar_id)

    def health_check(self) -> Dict[str, Any]:
        return {
            "service": "google_calendar",
            "configured": bool(self.credentials_file),
            "circuit_open": self.circuit_breaker.is_open(),
        }

    def list_events(self, limit: int = 10) -> Dict[str, Any]:
        now = datetime.now(tz=timezone.utc).isoformat()

        def _call() -> Dict[str, Any]:
            response = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=now,
                    maxResults=limit,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return {"events": response.get("items", [])}

        try:
            return with_retry(
                _call,
                operation_name="list_events",
                service_name="google_calendar",
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "CalendarWrapper list_events failed fast calendar_id=%s",
                self.calendar_id,
            )
            raise
        except Exception as exc:
            logger.exception(
                "CalendarWrapper list_events failed calendar_id=%s",
                self.calendar_id,
            )
            raise RuntimeError(f"Google Calendar error: {str(exc)}") from exc

    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        timezone: str = "America/Chicago",
    ) -> Dict[str, Any]:
        if not summary or not summary.strip():
            raise NonRetryableServiceError("summary is required")

        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        event_body = {
            "summary": summary,
            "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
        }

        def _call() -> Dict[str, Any]:
            return (
                self.service.events()
                .insert(calendarId=self.calendar_id, body=event_body)
                .execute()
            )

        try:
            return with_retry(
                _call,
                operation_name="create_event",
                service_name="google_calendar",
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "CalendarWrapper create_event failed fast summary=%s calendar_id=%s",
                summary,
                self.calendar_id,
            )
            raise
        except Exception as exc:
            logger.exception(
                "CalendarWrapper create_event failed summary=%s calendar_id=%s",
                summary,
                self.calendar_id,
            )
            raise RuntimeError(f"Google Calendar error: {str(exc)}") from exc
