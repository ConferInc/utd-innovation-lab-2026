from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from typing import Optional

import httpx


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
    max_retries: int = _env_int("EVENT_SCRAPER_MAX_RETRIES", 3)
    backoff_base_seconds: float = _env_float("EVENT_SCRAPER_BACKOFF_BASE_SECONDS", 0.8)


class RespectfulHttpClient:
    def __init__(self, config: Optional[ScraperConfig] = None) -> None:
        self.config = config or ScraperConfig()
        self._last_request_at: Optional[float] = None
        self._client = httpx.Client(
            headers={"User-Agent": self.config.user_agent},
            timeout=self.config.timeout_seconds,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def _sleep_if_needed(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.config.min_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get_text(self, url: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                self._sleep_if_needed()
                resp = self._client.get(url)
                self._last_request_at = time.monotonic()
                resp.raise_for_status()
                return resp.text
            except Exception as exc:
                last_exc = exc
                if attempt >= self.config.max_retries:
                    break
                # Exponential backoff with jitter.
                base = self.config.backoff_base_seconds * (2 ** (attempt - 1))
                jitter = random.random() * 0.25 * base
                time.sleep(base + jitter)
        assert last_exc is not None
        raise last_exc

