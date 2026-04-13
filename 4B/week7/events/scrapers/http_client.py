from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class ScraperConfig:
    user_agent: str = os.getenv(
        "EVENT_SCRAPER_USER_AGENT",
        "JKYogTempleBot/1.0 (educational; contact: student-team)",
    )
    timeout_seconds: float = _env_float("EVENT_SCRAPER_TIMEOUT_SECONDS", 20.0)
    min_delay_seconds: float = _env_float("EVENT_SCRAPER_MIN_DELAY_SECONDS", 1.0)
    # Max *retry* rounds after a transient failure (5xx / timeout / connection error).
    # Total attempts = max_retries + 1 (default 3 + 1 = 4 GETs).
    max_retries: int = int(_env_int("EVENT_SCRAPER_MAX_RETRIES", 3))
    # First sleep after transient failure is backoff_factor * 1s, then *2s, then *4s (factor=1.0).
    backoff_factor: float = _env_float("EVENT_SCRAPER_BACKOFF_FACTOR", 1.0)


def _transient_backoff_seconds(attempt_index: int, backoff_factor: float) -> float:
    """Sleep duration after failed attempt ``attempt_index`` (1-based): factor*1, factor*2, factor*4, ..."""
    return float(backoff_factor) * float(2 ** (attempt_index - 1))


class RespectfulHttpClient:
    """HTTP client for scrapers: rate limiting + transient retries (5xx / timeouts only)."""

    def __init__(
        self,
        config: Optional[ScraperConfig] = None,
        *,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        """
        Args:
            config: Base configuration (merged with optional overrides).
            max_retries: Override ``config.max_retries`` when set.
            backoff_factor: Override ``config.backoff_factor`` when set.
            client: Optional pre-built ``httpx.Client`` (e.g. MockTransport in tests).
        """
        base = config or ScraperConfig()
        if max_retries is not None or backoff_factor is not None:
            self.config = ScraperConfig(
                user_agent=base.user_agent,
                timeout_seconds=base.timeout_seconds,
                min_delay_seconds=base.min_delay_seconds,
                max_retries=max_retries if max_retries is not None else base.max_retries,
                backoff_factor=backoff_factor if backoff_factor is not None else base.backoff_factor,
            )
        else:
            self.config = base
        self._last_request_at: Optional[float] = None
        self._client = client or httpx.Client(
            headers={"User-Agent": self.config.user_agent},
            timeout=self.config.timeout_seconds,
            follow_redirects=True,
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _sleep_if_needed(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.config.min_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get_text(self, url: str) -> str:
        """GET *url* and return response text. Retries only on 5xx, timeouts, and connection errors."""
        max_attempts = max(1, self.config.max_retries + 1)
        last_exc: BaseException | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                self._sleep_if_needed()
                resp = self._client.get(url)
                self._last_request_at = time.monotonic()

                if resp.is_success:
                    return resp.text
                if resp.status_code < 500:
                    resp.raise_for_status()

                last_exc = httpx.HTTPStatusError(
                    f"Server error {resp.status_code} for url={url!r}",
                    request=resp.request,
                    response=resp,
                )
                if attempt >= max_attempts:
                    raise last_exc
                delay = _transient_backoff_seconds(attempt, self.config.backoff_factor)
                logger.warning(
                    "Transient HTTP %s for %s (attempt %s/%s); retrying in %.1fs",
                    resp.status_code,
                    url,
                    attempt,
                    max_attempts,
                    delay,
                )
                time.sleep(delay)

            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response is None or exc.response.status_code < 500:
                    raise
                if attempt >= max_attempts:
                    raise
                delay = _transient_backoff_seconds(attempt, self.config.backoff_factor)
                logger.warning(
                    "HTTPStatusError for %s (attempt %s/%s): %s; retrying in %.1fs",
                    url,
                    attempt,
                    max_attempts,
                    exc,
                    delay,
                )
                time.sleep(delay)

            except httpx.RequestError as exc:
                last_exc = exc
                if attempt >= max_attempts:
                    raise
                delay = _transient_backoff_seconds(attempt, self.config.backoff_factor)
                logger.warning(
                    "%s for %s (attempt %s/%s); retrying in %.1fs",
                    type(exc).__name__,
                    url,
                    attempt,
                    max_attempts,
                    delay,
                )
                time.sleep(delay)

        assert last_exc is not None
        raise last_exc
