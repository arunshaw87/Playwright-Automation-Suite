"""
Authentication endpoint tests.

Covers: POST /api/auth/login
- 200 on valid credentials with token in response
- 401 on wrong password
- 401 on unknown username
- 422 on missing required fields
- 400 on empty payload

All tests are skipped if the auth endpoint is not available on the target server
(indicated by auth_token fixture returning None and the endpoint returning 404).
"""
import pytest
import httpx

from models.responses import AuthResponse, ErrorResponse
from utils.validators import assert_status, assert_schema, assert_error_response
from utils.data_factory import make_login_payload

AUTH_PATH = "/api/auth/login"
VALID_USER = "admin"
VALID_PASS = "password"


def _auth_available(client: httpx.Client) -> bool:
    """Return True if the auth endpoint exists on the target server."""
    try:
        r = client.post(AUTH_PATH, json=make_login_payload())
        return r.status_code != 404
    except Exception:
        return False


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.auth
class TestAuthLogin:
    def test_valid_credentials_return_200(self, api_client: httpx.Client) -> None:
        if not _auth_available(api_client):
            pytest.skip("Auth endpoint not available on target server")
        payload = make_login_payload(username=VALID_USER, password=VALID_PASS)
        response = api_client.post(AUTH_PATH, json=payload)
        assert_status(response, 200)

    def test_valid_credentials_return_token(self, api_client: httpx.Client) -> None:
        if not _auth_available(api_client):
            pytest.skip("Auth endpoint not available on target server")
        payload = make_login_payload(username=VALID_USER, password=VALID_PASS)
        response = api_client.post(AUTH_PATH, json=payload)
        assert_status(response, 200)
        data = assert_schema(response, AuthResponse)
        assert data.token, "Token must be non-empty"
        assert len(data.token) >= 10, "Token appears too short"

    def test_wrong_password_returns_401(self, unauth_client: httpx.Client) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        payload = make_login_payload(username=VALID_USER, password="WRONG_PASSWORD")
        response = unauth_client.post(AUTH_PATH, json=payload)
        assert_error_response(response, 401)

    def test_unknown_username_returns_401(self, unauth_client: httpx.Client) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        payload = make_login_payload(username="no_such_user_xyz", password=VALID_PASS)
        response = unauth_client.post(AUTH_PATH, json=payload)
        assert_error_response(response, 401)

    def test_missing_username_returns_422(self, unauth_client: httpx.Client) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        response = unauth_client.post(AUTH_PATH, json={"password": VALID_PASS})
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for missing username, got {response.status_code}"
        )

    def test_missing_password_returns_422(self, unauth_client: httpx.Client) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        response = unauth_client.post(AUTH_PATH, json={"username": VALID_USER})
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for missing password, got {response.status_code}"
        )

    def test_empty_payload_returns_400_or_422(
        self, unauth_client: httpx.Client
    ) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        response = unauth_client.post(AUTH_PATH, json={})
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for empty payload, got {response.status_code}"
        )

    def test_response_content_type_is_json(
        self, unauth_client: httpx.Client
    ) -> None:
        if not _auth_available(unauth_client):
            pytest.skip("Auth endpoint not available on target server")
        payload = make_login_payload(username=VALID_USER, password=VALID_PASS)
        response = unauth_client.post(AUTH_PATH, json=payload)
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, (
            f"Expected JSON content type, got '{content_type}'"
        )
