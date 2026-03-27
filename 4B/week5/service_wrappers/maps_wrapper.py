import os
import logging
from typing import Any, Dict

import googlemaps

from .base_wrapper import with_retry, NonRetryableServiceError

logger = logging.getLogger(__name__)


class MapsWrapper:
    """
    Wrapper around Google Maps client.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY is not set")

        self.client = googlemaps.Client(key=self.api_key)

    def geocode(self, address: str) -> Dict[str, Any]:
        if not address:
            raise NonRetryableServiceError("address is required")

        def _call() -> Dict[str, Any]:
            result = self.client.geocode(address)
            return {"results": result}

        try:
            return with_retry(_call, retries=3, delay=1.0, retry_exceptions=(TimeoutError, Exception))
        except Exception as exc:
            logger.exception("Google Maps geocode failed")
            raise RuntimeError(f"Google Maps error: {str(exc)}") from exc

    def directions(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        if not origin or not destination:
            raise NonRetryableServiceError("origin and destination are required")

        def _call() -> Dict[str, Any]:
            result = self.client.directions(origin, destination, mode=mode)
            return {"routes": result}

        try:
            return with_retry(_call, retries=3, delay=1.0, retry_exceptions=(TimeoutError, Exception))
        except Exception as exc:
            logger.exception("Google Maps directions failed")
            raise RuntimeError(f"Google Maps error: {str(exc)}") from exc