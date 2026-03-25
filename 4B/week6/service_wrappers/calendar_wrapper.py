import os
import logging
from typing import Any, Dict

import googlemaps

from .base_wrapper import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    NonRetryableServiceError,
    with_retry,
)

logger = logging.getLogger(__name__)


class MapsWrapper:
    """
    Wrapper around Google Maps client.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30)

        if not self.api_key:
            logger.error("MapsWrapper init failed: GOOGLE_MAPS_API_KEY missing")
            raise ValueError("GOOGLE_MAPS_API_KEY is not set")

        self.client = googlemaps.Client(key=self.api_key)
        logger.info("MapsWrapper initialized")

    def health_check(self) -> Dict[str, Any]:
        return {
            "service": "google_maps",
            "configured": bool(self.api_key),
            "circuit_open": self.circuit_breaker.is_open(),
        }

    def geocode(self, address: str) -> Dict[str, Any]:
        if not address:
            raise NonRetryableServiceError("address is required")

        def _call() -> Dict[str, Any]:
            result = self.client.geocode(address)
            return {"results": result}

        try:
            return with_retry(
                _call,
                operation_name="geocode",
                service_name="google_maps",
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception("MapsWrapper geocode failed fast address=%s", address)
            raise
        except Exception as exc:
            logger.exception("MapsWrapper geocode failed address=%s", address)
            raise RuntimeError(f"Google Maps error: {str(exc)}") from exc

    def directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
    ) -> Dict[str, Any]:
        if not origin or not destination:
            raise NonRetryableServiceError("origin and destination are required")

        def _call() -> Dict[str, Any]:
            result = self.client.directions(origin, destination, mode=mode)
            return {"routes": result}

        try:
            return with_retry(
                _call,
                operation_name="directions",
                service_name="google_maps",
                retries=3,
                delay=1.0,
                retry_exceptions=(TimeoutError, Exception),
                circuit_breaker=self.circuit_breaker,
            )
        except CircuitBreakerOpenError:
            logger.exception(
                "MapsWrapper directions failed fast origin=%s destination=%s mode=%s",
                origin,
                destination,
                mode,
            )
            raise
        except Exception as exc:
            logger.exception(
                "MapsWrapper directions failed origin=%s destination=%s mode=%s",
                origin,
                destination,
                mode,
            )
            raise RuntimeError(f"Google Maps error: {str(exc)}") from exc