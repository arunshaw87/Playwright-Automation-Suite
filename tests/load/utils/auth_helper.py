"""
Auth helper for Locust HttpUser classes.

Handles token acquisition from the API auth endpoint and
injects the Authorization header into the Locust client for
subsequent authenticated requests.

Usage (inside a Locust HttpUser subclass)::

    from utils.auth_helper import acquire_token, inject_auth_header

    class MyUser(HttpUser):
        def on_start(self):
            token = acquire_token(self.client, "/api/auth/login",
                                  username="admin", password="password")
            if token:
                inject_auth_header(self.client, token)
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

AUTH_PATH = os.environ.get("API_AUTH_PATH", "/api/auth/login")
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password")


def acquire_token(
    client: Any,
    auth_path: str = AUTH_PATH,
    *,
    username: str = API_USERNAME,
    password: str = API_PASSWORD,
) -> str | None:
    """
    POST to ``auth_path`` with credentials and return the Bearer token string.

    Returns None (and logs a warning) if login fails or the endpoint is absent.
    Suitable for use in ``HttpUser.on_start()``.
    """
    with client.post(
        auth_path,
        json={"username": username, "password": password},
        catch_response=True,
        name="[auth] POST /auth/login",
    ) as response:
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                response.success()
                logger.debug("Auth token acquired for user %s", username)
                return str(token)
            response.failure("Auth response missing token field")
            return None
        elif response.status_code == 404:
            response.success()
            logger.info("Auth endpoint not found — running unauthenticated")
            return None
        else:
            response.failure(
                f"Login failed: HTTP {response.status_code}"
            )
            return None


def inject_auth_header(client: Any, token: str) -> None:
    """Add the Authorization Bearer header to the Locust client session."""
    client.headers.update({"Authorization": f"Bearer {token}"})
    logger.debug("Authorization header injected into Locust client")
