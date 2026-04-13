"""RespectfulHttpClient retry policy: 5xx and RequestError retry; 4xx does not."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

_WEEK = Path(__file__).resolve().parents[1]
if str(_WEEK) not in sys.path:
    sys.path.insert(0, str(_WEEK))

from events.scrapers.http_client import RespectfulHttpClient, ScraperConfig


def test_404_no_retry_single_get() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(404, request=request, text="missing")

    transport = httpx.MockTransport(handler)
    inner = httpx.Client(transport=transport, follow_redirects=True)
    client = RespectfulHttpClient(
        ScraperConfig(min_delay_seconds=0.0, max_retries=3, backoff_factor=1.0),
        client=inner,
    )
    try:
        with patch("events.scrapers.http_client.time.sleep"):
            with pytest.raises(httpx.HTTPStatusError) as ei:
                client.get_text("https://example.test/missing")
        assert ei.value.response.status_code == 404
        assert len(calls) == 1
    finally:
        client.close()


def test_503_retries_then_success() -> None:
    state = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] < 3:
            return httpx.Response(503, request=request, text="unavailable")
        return httpx.Response(200, request=request, text="ok body")

    transport = httpx.MockTransport(handler)
    inner = httpx.Client(transport=transport, follow_redirects=True)
    client = RespectfulHttpClient(
        ScraperConfig(min_delay_seconds=0.0, max_retries=3, backoff_factor=1.0),
        client=inner,
    )
    try:
        with patch("events.scrapers.http_client.time.sleep"):
            text = client.get_text("https://example.test/flaky")
        assert text == "ok body"
        assert state["n"] == 3
    finally:
        client.close()


def test_connect_error_retries() -> None:
    state = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] < 2:
            raise httpx.ConnectError("refused", request=request)
        return httpx.Response(200, request=request, text="recovered")

    transport = httpx.MockTransport(handler)
    inner = httpx.Client(transport=transport, follow_redirects=True)
    client = RespectfulHttpClient(
        ScraperConfig(min_delay_seconds=0.0, max_retries=3, backoff_factor=1.0),
        client=inner,
    )
    try:
        with patch("events.scrapers.http_client.time.sleep"):
            assert client.get_text("https://example.test/down") == "recovered"
        assert state["n"] == 2
    finally:
        client.close()


def test_constructor_overrides_max_retries_and_backoff_factor() -> None:
    c = RespectfulHttpClient(max_retries=1, backoff_factor=2.0)
    assert c.config.max_retries == 1
    assert c.config.backoff_factor == 2.0
    c.close()
