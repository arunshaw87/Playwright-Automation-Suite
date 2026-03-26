"""
Retry utilities for flaky API calls (e.g., waiting for eventual consistency
or server startup in CI environments).

Usage::

    from utils.retry import retry_on_status, wait_for_api

    response = retry_on_status(lambda: client.get("/api/healthz"), expected=200)
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def retry_on_status(
    fn: Callable[[], httpx.Response],
    *,
    expected: int = 200,
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> httpx.Response:
    """Call ``fn()`` and retry up to ``retries`` times if status != expected.

    Uses exponential back-off (delay × backoff^attempt).
    Raises ``AssertionError`` if all attempts fail.
    """
    last_response: httpx.Response | None = None
    current_delay = delay

    for attempt in range(1, retries + 1):
        response = fn()
        if response.status_code == expected:
            return response
        last_response = response
        logger.warning(
            "Attempt %d/%d: expected HTTP %d, got %d — retrying in %.1fs",
            attempt,
            retries,
            expected,
            response.status_code,
            current_delay,
        )
        if attempt < retries:
            time.sleep(current_delay)
            current_delay *= backoff

    assert last_response is not None
    raise AssertionError(
        f"After {retries} attempts, expected HTTP {expected}, "
        f"last status was {last_response.status_code}.\n"
        f"URL: {last_response.request.url}"
    )


def wait_for_api(
    base_url: str,
    *,
    path: str = "/api/healthz",
    timeout: float = 30.0,
    interval: float = 1.0,
) -> None:
    """Poll ``base_url + path`` until it returns HTTP 200 or timeout is reached.

    Useful in CI before starting the test suite to wait for the server to boot.
    Raises ``TimeoutError`` if the server does not become available in time.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with httpx.Client(base_url=base_url, timeout=5.0) as client:
                response = client.get(path)
                if response.status_code == 200:
                    logger.info("API is ready at %s%s", base_url, path)
                    return
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        time.sleep(interval)

    raise TimeoutError(
        f"API at {base_url}{path} did not become available within {timeout}s"
    )
