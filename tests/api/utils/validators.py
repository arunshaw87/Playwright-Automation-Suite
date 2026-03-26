"""
Reusable assertion helpers for API response validation.

Usage::

    from utils.validators import assert_status, assert_schema, assert_pagination

    response = client.get("/api/users")
    assert_status(response, 200)
    data = assert_schema(response, UserListResponse)
    assert_pagination(data)
"""
from __future__ import annotations

import logging
from typing import Any, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

M = TypeVar("M", bound=BaseModel)


def assert_status(response: httpx.Response, expected: int) -> httpx.Response:
    """Assert that the HTTP response has the expected status code.

    Returns the response for chaining.
    """
    actual = response.status_code
    if actual != expected:
        # Try to include response body for debugging
        try:
            body = response.json()
        except Exception:
            body = response.text
        raise AssertionError(
            f"Expected HTTP {expected}, got {actual}.\n"
            f"URL: {response.request.url}\n"
            f"Body: {body}"
        )
    return response


def assert_schema(response: httpx.Response, model: Type[M]) -> M:
    """Validate the JSON response body against a Pydantic v2 model.

    Returns the parsed model instance so tests can make further assertions.
    Raises ``AssertionError`` on validation failure with a descriptive message.
    """
    try:
        body = response.json()
    except Exception as exc:
        raise AssertionError(
            f"Response body is not valid JSON: {exc}\nRaw text: {response.text}"
        ) from exc

    try:
        return model.model_validate(body)
    except ValidationError as exc:
        raise AssertionError(
            f"Response body does not match schema {model.__name__}:\n{exc}\n"
            f"Raw body: {body}"
        ) from exc


def assert_pagination(data: Any) -> None:
    """Assert that a response contains the expected pagination fields."""
    required_fields = ("total", "page", "per_page")
    for field in required_fields:
        value = getattr(data, field, None)
        assert value is not None, (
            f"Pagination field '{field}' is missing or None in response"
        )
    assert data.total >= 0, f"total must be >= 0, got {data.total}"
    assert data.page >= 1, f"page must be >= 1, got {data.page}"
    assert data.per_page >= 1, f"per_page must be >= 1, got {data.per_page}"


def assert_error_response(
    response: httpx.Response,
    expected_status: int,
    expected_message_fragment: str | None = None,
) -> None:
    """Assert that the response is an error with the expected status code.

    Optionally checks that the response body contains a message fragment.
    """
    assert_status(response, expected_status)
    try:
        body = response.json()
    except Exception:
        return

    if expected_message_fragment:
        body_str = str(body).lower()
        fragment_lower = expected_message_fragment.lower()
        assert fragment_lower in body_str, (
            f"Expected '{expected_message_fragment}' in error response body, "
            f"but got: {body}"
        )


def assert_content_type_json(response: httpx.Response) -> None:
    """Assert that the response Content-Type is application/json."""
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, (
        f"Expected 'application/json' Content-Type, got '{content_type}'"
    )
