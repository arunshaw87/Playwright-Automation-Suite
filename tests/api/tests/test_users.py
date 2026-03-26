"""
User CRUD endpoint tests.

Covers: GET /api/users, GET /api/users/{id},
        POST /api/users, PUT /api/users/{id}, DELETE /api/users/{id}

Every response is validated against a Pydantic v2 schema:
- Success responses → UserResponse / UserListResponse
- Error responses   → ErrorResponse

All tests are skipped when the /api/users endpoint returns 404,
meaning they are not implemented on the target server.
"""
from __future__ import annotations

import pytest
import httpx

from models.responses import UserResponse, UserListResponse, ErrorResponse
from utils.validators import (
    assert_status,
    assert_schema,
    assert_pagination,
    assert_error_response,
    assert_content_type_json,
)
from utils.data_factory import make_user_payload, make_partial_user_payload

USERS_PATH = "/api/users"


def _users_available(client: httpx.Client) -> bool:
    """Return True when endpoint exists (not 404). Non-404 errors propagate as failures."""
    r = client.get(USERS_PATH)
    return r.status_code != 404


def _skip_if_unavailable(client: httpx.Client) -> None:
    if not _users_available(client):
        pytest.skip("Users endpoint not available on target server")


# ---------------------------------------------------------------------------
# GET /api/users
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.users
class TestGetUsers:
    def test_list_users_returns_200(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(USERS_PATH)
        assert_status(response, 200)
        assert_schema(response, UserListResponse)

    def test_list_users_content_type_json(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(USERS_PATH)
        assert_content_type_json(response)

    def test_list_users_schema_valid(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(USERS_PATH)
        assert_status(response, 200)
        data = assert_schema(response, UserListResponse)
        assert isinstance(data.data, list), "data field must be a list"

    def test_list_users_pagination_fields_present(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(USERS_PATH)
        data = assert_schema(response, UserListResponse)
        assert_pagination(data)

    def test_list_users_unauthenticated_returns_401(
        self, unauth_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(unauth_client)
        response = unauth_client.get(USERS_PATH)
        assert_error_response(response, 401)
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# GET /api/users/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.users
class TestGetSingleUser:
    def test_get_existing_user_returns_200(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        list_resp = api_client.get(USERS_PATH)
        assert_status(list_resp, 200)
        users = list_resp.json().get("data", [])
        if not users:
            pytest.skip("No users available to fetch individually")
        user_id = users[0]["id"]
        response = api_client.get(f"{USERS_PATH}/{user_id}")
        assert_status(response, 200)
        data = assert_schema(response, UserResponse)
        assert str(data.id) == str(user_id)

    def test_get_nonexistent_user_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(f"{USERS_PATH}/999999999")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)

    def test_get_invalid_user_id_returns_4xx(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(f"{USERS_PATH}/not-a-valid-id-xyz")
        assert response.status_code in (400, 404, 422), (
            f"Expected 4xx for invalid user ID, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# POST /api/users
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.users
class TestCreateUser:
    def test_create_user_returns_201(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        payload = make_user_payload()
        response = api_client.post(USERS_PATH, json=payload)
        assert_status(response, 201)
        assert_schema(response, UserResponse)

    def test_create_user_response_schema_valid(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = make_user_payload()
        response = api_client.post(USERS_PATH, json=payload)
        assert_status(response, 201)
        data = assert_schema(response, UserResponse)
        assert data.email == payload["email"]
        assert data.username == payload["username"]

    def test_create_user_duplicate_email_returns_409(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = make_user_payload()
        api_client.post(USERS_PATH, json=payload)
        response = api_client.post(USERS_PATH, json=payload)
        assert response.status_code in (400, 409, 422), (
            f"Expected 4xx for duplicate email, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_user_missing_email_returns_422(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = {"username": "noemail_user", "password": "pass123"}
        response = api_client.post(USERS_PATH, json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for missing email, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_user_empty_body_returns_422(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.post(USERS_PATH, json={})
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for empty body, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_user_unauthenticated_returns_401(
        self, unauth_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(unauth_client)
        response = unauth_client.post(USERS_PATH, json=make_user_payload())
        assert_error_response(response, 401)
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# PUT /api/users/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.users
class TestUpdateUser:
    def _create_user(self, client: httpx.Client) -> dict:
        payload = make_user_payload()
        r = client.post(USERS_PATH, json=payload)
        if r.status_code != 201:
            pytest.skip("User creation not available — cannot test update")
        return r.json()

    def test_update_user_returns_200(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        user = self._create_user(api_client)
        update_payload = make_partial_user_payload()
        response = api_client.put(f"{USERS_PATH}/{user['id']}", json=update_payload)
        assert_status(response, 200)
        assert_schema(response, UserResponse)

    def test_update_user_reflects_changes(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        user = self._create_user(api_client)
        new_username = "updated_username_xyz"
        update_payload = make_partial_user_payload(username=new_username)
        response = api_client.put(f"{USERS_PATH}/{user['id']}", json=update_payload)
        assert_status(response, 200)
        data = assert_schema(response, UserResponse)
        assert data.username == new_username, (
            f"Expected username '{new_username}', got '{data.username}'"
        )

    def test_update_nonexistent_user_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.put(
            f"{USERS_PATH}/999999999", json=make_partial_user_payload()
        )
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# DELETE /api/users/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.users
class TestDeleteUser:
    def _create_user(self, client: httpx.Client) -> dict:
        payload = make_user_payload()
        r = client.post(USERS_PATH, json=payload)
        if r.status_code != 201:
            pytest.skip("User creation not available — cannot test delete")
        return r.json()

    def test_delete_user_returns_204_or_200(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        user = self._create_user(api_client)
        response = api_client.delete(f"{USERS_PATH}/{user['id']}")
        assert response.status_code in (200, 204), (
            f"Expected 200 or 204 on delete, got {response.status_code}"
        )
        if response.status_code == 204:
            assert response.content == b"", (
                "HTTP 204 must have no response body"
            )
        else:
            assert_schema(response, UserResponse)

    def test_delete_user_then_get_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        user = self._create_user(api_client)
        api_client.delete(f"{USERS_PATH}/{user['id']}")
        response = api_client.get(f"{USERS_PATH}/{user['id']}")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)

    def test_delete_nonexistent_user_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.delete(f"{USERS_PATH}/999999999")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)
