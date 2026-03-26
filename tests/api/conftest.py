"""
API test framework conftest.

Fixtures
--------
base_url         : session — read from env or default to localhost
auth_token       : session — obtains a Bearer token once per session
api_client       : session — pre-configured httpx.Client with auth header
unauth_client    : function — httpx.Client with no auth header (for negative tests)
"""
from __future__ import annotations

import logging
import os
import pytest
import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:80")
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password")
AUTH_PATH = os.environ.get("API_AUTH_PATH", "/api/auth/login")
REQUEST_TIMEOUT = float(os.environ.get("API_TIMEOUT", "10"))


def pytest_configure(config: pytest.Config) -> None:
    for directory in ("reports/html", "reports/junit"):
        os.makedirs(directory, exist_ok=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the API base URL (configurable via API_BASE_URL env var)."""
    url = DEFAULT_BASE_URL.rstrip("/")
    logger.info("API base URL: %s", url)
    return url


@pytest.fixture(scope="session")
def auth_token(base_url: str) -> str | None:
    """
    Session-scoped fixture that obtains a Bearer token once per session.

    Attempts POST ``/api/auth/login``.
    - Returns a token string on HTTP 200.
    - Returns None silently on HTTP 404 (endpoint not implemented on this server).
    - Raises on any other HTTP error or unexpected status (fail fast).
    - Returns None on network-level errors (ConnectError/Timeout) — appropriate
      for a session setup fixture where the API may be starting up.
    """
    payload = {"username": API_USERNAME, "password": API_PASSWORD}
    try:
        with httpx.Client(base_url=base_url, timeout=REQUEST_TIMEOUT) as client:
            response = client.post(AUTH_PATH, json=payload)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        logger.warning("Could not reach auth endpoint: %s", exc)
        return None

    if response.status_code == 200:
        data = response.json()
        token = data.get("token") or data.get("access_token")
        if token:
            logger.info("Auth token acquired successfully")
            return str(token)
        logger.warning("Auth response missing token field")
        return None

    if response.status_code == 404:
        logger.info("Auth endpoint not found (404) — running without token")
        return None

    # Unexpected status (e.g., 500, 503) — log and fail fast so the root cause
    # is clearly visible rather than cascading into auth-dependent test failures.
    raise RuntimeError(
        f"Auth endpoint returned unexpected HTTP {response.status_code} "
        f"during session setup. URL: {AUTH_PATH}. "
        f"Fix the server or update API credentials."
    )


@pytest.fixture(scope="session")
def api_client(base_url: str, auth_token: str | None) -> httpx.Client:
    """
    Session-scoped httpx.Client pre-configured with:
    - base_url from ``base_url`` fixture
    - Authorization: Bearer <token> header (when token available)
    - Default timeout
    - JSON Accept header
    """
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    client = httpx.Client(
        base_url=base_url,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def unauth_client(base_url: str) -> httpx.Client:
    """
    Function-scoped httpx.Client with NO Authorization header.
    Used for negative tests (401 Unauthorized scenarios).
    """
    client = httpx.Client(
        base_url=base_url,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
    )
    yield client
    client.close()
