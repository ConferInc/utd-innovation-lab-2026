"""API client for Team 4B event endpoints.

Wraps the 5 required event endpoints with:
- 30 second timeout
- clean error handling
- small, reusable methods for response_builder.py

Expected endpoints:
- GET /api/v2/events
- GET /api/v2/events/today
- GET /api/v2/events/search?q=...
- GET /api/v2/events/recurring
- GET /api/v2/events/{id}
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

import httpx


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


DEFAULT_CONNECT_TIMEOUT_SECONDS = _env_float("EVENTS_API_CONNECT_TIMEOUT_SECONDS", 5.0)
DEFAULT_READ_TIMEOUT_SECONDS = _env_float("EVENTS_API_READ_TIMEOUT_SECONDS", 10.0)
DEFAULT_WRITE_TIMEOUT_SECONDS = _env_float("EVENTS_API_WRITE_TIMEOUT_SECONDS", 10.0)
DEFAULT_POOL_TIMEOUT_SECONDS = _env_float("EVENTS_API_POOL_TIMEOUT_SECONDS", 5.0)
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
    connect_timeout_seconds: float = DEFAULT_CONNECT_TIMEOUT_SECONDS
    read_timeout_seconds: float = DEFAULT_READ_TIMEOUT_SECONDS
    write_timeout_seconds: float = DEFAULT_WRITE_TIMEOUT_SECONDS
    pool_timeout_seconds: float = DEFAULT_POOL_TIMEOUT_SECONDS
    bearer_token: Optional[str] = os.getenv("EVENTS_API_BEARER_TOKEN")

    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")

    def normalized_events_base_path(self) -> str:
        base_path = self.events_base_path.strip()
        if not base_path.startswith("/"):
            base_path = "/" + base_path
        return base_path.rstrip("/")

    def httpx_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect_timeout_seconds,
            read=self.read_timeout_seconds,
            write=self.write_timeout_seconds,
            pool=self.pool_timeout_seconds,
        )


class EventAPIClient:
    """Small wrapper around Team 4B event endpoints."""

    def __init__(
        self,
        *,
        config: Optional[APIConfig] = None,
        headers: Optional[Mapping[str, str]] = None,
        observer: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.config = config or APIConfig()
        self._headers: Dict[str, str] = {"Accept": "application/json"}
        self._observer = observer
        if self.config.bearer_token:
            self._headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        if headers:
            self._headers.update(dict(headers))

    @property
    def events_root(self) -> str:
        return f"{self.config.normalized_base_url()}{self.config.normalized_events_base_path()}"

    def _request(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.events_root}{path}"
        started = time.monotonic()
        status_code: Optional[int] = None
        error_type: Optional[str] = None
        try:
            try:
                with httpx.Client(timeout=self.config.httpx_timeout(), headers=self._headers) as client:
                    response = client.get(url, params=params)
            except httpx.TimeoutException as exc:
                error_type = "timeout"
                raise APITimeoutError(
                    "Timed out while calling "
                    f"{url} (connect={self.config.connect_timeout_seconds:.0f}s, "
                    f"read={self.config.read_timeout_seconds:.0f}s)"
                ) from exc
            except httpx.HTTPError as exc:
                error_type = "connection_error"
                raise APIConnectionError(f"Could not reach Team 4B API at {url}") from exc

            status_code = response.status_code
            if response.status_code >= 400:
                error_type = "http_error"
                message = f"Team 4B API returned HTTP {response.status_code} for {url}"
                try:
                    payload = response.json()
                    if isinstance(payload, dict) and payload.get("detail"):
                        message = f"{message}: {payload['detail']}"
                except ValueError:
                    payload = None
                raise APIResponseError(
                    message,
                    status_code=response.status_code,
                    response_body=response.text[:1000],
                )

            try:
                data = response.json()
            except ValueError as exc:
                error_type = "parse_error"
                raise APIParseError(f"Team 4B API returned non-JSON data for {url}") from exc

            if not isinstance(data, dict):
                error_type = "parse_error"
                raise APIParseError(f"Team 4B API returned unexpected JSON shape for {url}")
            return data
        finally:
            if self._observer is not None:
                self._observer(
                    {
                        "url": url,
                        "path": path or "/",
                        "params": dict(params or {}),
                        "status_code": status_code,
                        "error_type": error_type,
                        "elapsed_ms": int((time.monotonic() - started) * 1000),
                    }
                )

    def get_events(self, *, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """GET /api/v2/events"""
        return self._request("", params={"limit": limit, "offset": offset})

    def get_today(self) -> Dict[str, Any]:
        """GET /api/v2/events/today"""
        return self._request("/today")

    def search_events(self, query: str, *, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """GET /api/v2/events/search?q=..."""
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            raise ValueError("query must be non-empty")
        return self._request("/search", params={"q": cleaned_query, "limit": limit, "offset": offset})

    def get_recurring(self) -> Dict[str, Any]:
        """GET /api/v2/events/recurring"""
        return self._request("/recurring")

    def get_event_by_id(self, event_id: int) -> Dict[str, Any]:
        """GET /api/v2/events/{id}"""
        if not isinstance(event_id, int):
            raise ValueError("event_id must be an integer")
        return self._request(f"/{event_id}")
