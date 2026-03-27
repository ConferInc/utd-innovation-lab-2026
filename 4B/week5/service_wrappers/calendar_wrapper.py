import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .base_wrapper import NonRetryableServiceError, with_retry

logger = logging.getLogger(__name__)


class CalendarWrapper:
    """
    Wrapper around Google Calendar API.
    """

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        calendar_id: Optional[str] = None,
    ) -> None:
        logger.info("CalendarWrapper: initializing")

        self.credentials_file = credentials_file or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.calendar_id = calendar_id or os.getenv("GOOGLE_CALENDAR_ID", "primary")

        if not self.credentials_file:
            logger.error("CalendarWrapper: GOOGLE_APPLICATION_CREDENTIALS is missing")
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set")

        logger.info(
            "CalendarWrapper: using credentials_file=%s calendar_id=%s",
            self.credentials_file,
            self.calendar_id,
        )

        scopes = ["https://www.googleapis.com/auth/calendar"]
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
        self.service = build("calendar", "v3", credentials=creds)

        logger.info("CalendarWrapper: initialized successfully")

    def list_events(self, max_results: int = 10) -> Dict[str, Any]:
        logger.info("CalendarWrapper: list_events called | max_results=%s", max_results)

        def _call() -> Dict[str, Any]:
            now = datetime.utcnow().isoformat() + "Z"
            logger.info("CalendarWrapper: calling Google Calendar events.list")
            response = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = response.get("items", [])
            logger.info("CalendarWrapper: list_events succeeded | events_count=%s", len(events))
            return {"events": events}

        try:
            return with_retry(
                _call,
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
            )
        except Exception as exc:
            logger.exception("CalendarWrapper: list_events failed")
            raise RuntimeError(f"Google Calendar error: {str(exc)}") from exc

    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        timezone: str = "America/Chicago",
    ) -> Dict[str, Any]:
        logger.info(
            "CalendarWrapper: create_event called | summary=%s timezone=%s",
            summary,
            timezone,
        )

        if not summary:
            logger.error("CalendarWrapper: summary is missing")
            raise NonRetryableServiceError("summary is required")

        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        event_body = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
        }

        def _call() -> Dict[str, Any]:
            logger.info("CalendarWrapper: calling Google Calendar events.insert")
            event = (
                self.service.events()
                .insert(calendarId=self.calendar_id, body=event_body)
                .execute()
            )
            logger.info("CalendarWrapper: create_event succeeded | event_id=%s", event.get("id"))
            return event

        try:
            return with_retry(
                _call,
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
            )
        except Exception as exc:
            logger.exception("CalendarWrapper: create_event failed")
            raise RuntimeError(f"Google Calendar error: {str(exc)}") from exc