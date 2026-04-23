"""Improved API client for Team 4B event endpoints.

Features
--------
- Wraps the 5 required endpoints
- 30 second timeout
- Clean error handling
- Consistent extraction helpers for event payloads
- Small reusable methods for response_builder.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

import httpx


DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_BASE_URL = os.getenv("EVENTS_API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_EVENTS_BASE_PATH = "/api/v2/events"


class APIClientError(RuntimeError):
    """Base exception for event API failures."""


class APITimeoutError(APIClientError):
    """Raised when the upstream API times out."""


class APIConnectionError(APIClientError):
    """Raised when the upstream API cannot be reached."""


class APIResponseError(APIClientError):
    """Raised for non-2xx responses from the upstream API."""

    def __init__(self, message: str, *, status_code: int, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class APIParseError(APIClientError):
    """Raised when the upstream API response cannot be parsed as JSON."""


@dataclass(frozen=True)
class APIConfig:
    """Runtime configuration for the Team 4B event API."""

    base_url: str = DEFAULT_BASE_URL
    events_base_path: str = DEFAULT_EVENTS_BASE_PATH
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    bearer_token: Optional[str] = os.getenv("TEAM4B_API_BEARER_TOKEN")

    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")

    def normalized_events_base_path(self) -> str:
        base_path = self.events_base_path.strip() or DEFAULT_EVENTS_BASE_PATH
        if not base_path.startswith("/"):
            base_path = "/" + base_path
        return base_path.rstrip("/")


class EventAPIClient:
    """Small wrapper around Team 4B event endpoints."""

    def __init__(
        self,
        *,
        config: Optional[APIConfig] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.config = config or APIConfig()
        self._headers: Dict[str, str] = {"Accept": "application/json"}
        if self.config.bearer_token:
            self._headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        if headers:
            self._headers.update(dict(headers))

    @property
    def events_root(self) -> str:
        return f"{self.config.normalized_base_url()}{self.config.normalized_events_base_path()}"

    def _request(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.events_root}{path}"
        try:
            with httpx.Client(timeout=self.config.timeout_seconds, headers=self._headers) as client:
                response = client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise APITimeoutError(
                f"Timed out after {self.config.timeout_seconds:.0f}s while calling {url}"
            ) from exc
        except httpx.HTTPError as exc:
            raise APIConnectionError(f"Could not reach Team 4B API at {url}") from exc

        if response.status_code >= 400:
            message = f"Team 4B API returned HTTP {response.status_code} for {url}"
            try:
                payload = response.json()
                if isinstance(payload, dict) and payload.get("detail"):
                    message = f"{message}: {payload['detail']}"
            except ValueError:
                pass
            raise APIResponseError(
                message,
                status_code=response.status_code,
                response_body=response.text[:1000],
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise APIParseError(f"Team 4B API returned non-JSON data for {url}") from exc

        if not isinstance(data, dict):
            raise APIParseError(f"Team 4B API returned unexpected JSON shape for {url}")
        return data

    def get_events(self, *, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        return self._request("", params={"limit": limit, "offset": offset})

    def get_today(self) -> Dict[str, Any]:
        return self._request("/today")

    def search_events(self, query: str, *, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            raise ValueError("query must be non-empty")
        return self._request("/search", params={"q": cleaned_query, "limit": limit, "offset": offset})

    def get_recurring(self) -> Dict[str, Any]:
        return self._request("/recurring")

    def get_event_by_id(self, event_id: int) -> Dict[str, Any]:
        if not isinstance(event_id, int):
            raise ValueError("event_id must be an integer")
        return self._request(f"/{event_id}")

    @staticmethod
    def extract_events(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
        events = payload.get("events")
        if isinstance(events, list):
            return [dict(event) for event in events if isinstance(event, Mapping)]
        return []

    @staticmethod
    def extract_event(payload: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        if "events" in payload:
            events = EventAPIClient.extract_events(payload)
            return events[0] if events else None
        return dict(payload) if isinstance(payload, Mapping) else None

    def list_upcoming_events(self, *, limit: int = 25) -> List[Dict[str, Any]]:
        payload = self.get_events(limit=limit, offset=0)
        return self.extract_events(payload)

    def search_event_items(self, query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
        payload = self.search_events(query, limit=limit, offset=0)
        return self.extract_events(payload)

    def get_today_items(self) -> List[Dict[str, Any]]:
        payload = self.get_today()
        return self.extract_events(payload)

    def get_recurring_items(self) -> List[Dict[str, Any]]:
        payload = self.get_recurring()
        return self.extract_events(payload)
