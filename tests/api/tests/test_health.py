"""
Health endpoint tests.

Covers: GET /api/healthz
- 200 status
- JSON response with correct Content-Type
- Response body matches HealthStatusResponse schema
- ``status`` field equals "ok"
"""
import pytest
import httpx

from models.responses import HealthStatusResponse
from utils.validators import assert_status, assert_schema, assert_content_type_json


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.health
class TestHealthEndpoint:
    def test_healthz_returns_200(self, api_client: httpx.Client) -> None:
        response = api_client.get("/api/healthz")
        assert_status(response, 200)

    def test_healthz_content_type_is_json(self, api_client: httpx.Client) -> None:
        response = api_client.get("/api/healthz")
        assert_content_type_json(response)

    def test_healthz_schema_valid(self, api_client: httpx.Client) -> None:
        response = api_client.get("/api/healthz")
        assert_status(response, 200)
        data = assert_schema(response, HealthStatusResponse)
        assert isinstance(data.status, str), "status field must be a string"

    def test_healthz_status_is_ok(self, api_client: httpx.Client) -> None:
        response = api_client.get("/api/healthz")
        assert_status(response, 200)
        data = assert_schema(response, HealthStatusResponse)
        assert data.status == "ok", f"Expected status 'ok', got '{data.status}'"

    def test_healthz_response_time_acceptable(self, api_client: httpx.Client) -> None:
        import time

        start = time.monotonic()
        response = api_client.get("/api/healthz")
        elapsed = time.monotonic() - start
        assert_status(response, 200)
        assert elapsed < 5.0, f"Health check took {elapsed:.2f}s — exceeds 5s threshold"

    def test_healthz_unauthenticated_still_returns_200(
        self, unauth_client: httpx.Client
    ) -> None:
        """Health endpoint should be publicly accessible without a token."""
        response = unauth_client.get("/api/healthz")
        assert_status(response, 200)
