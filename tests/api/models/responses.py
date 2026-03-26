"""
Pydantic v2 response models used for schema validation across all API tests.
Each model reflects the expected shape of a real API response. Tests use
``utils.validators.assert_schema()`` to validate responses against these models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Generic wrappers
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response envelope."""

    data: list[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple message-only response."""

    message: str


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthStatusResponse(BaseModel):
    """GET /api/healthz — matches the OpenAPI HealthStatus schema."""

    status: str


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class AuthResponse(BaseModel):
    """POST /api/auth/login — successful auth response containing a JWT token."""

    token: str = Field(min_length=10)
    token_type: str = Field(default="Bearer")
    expires_in: int | None = None


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class UserResponse(BaseModel):
    """Single user resource response."""

    id: int | str
    username: str
    email: str
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None


class UserListResponse(BaseModel):
    """GET /api/users — paginated user list."""

    data: list[UserResponse]
    total: int
    page: int
    per_page: int


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


class ProductResponse(BaseModel):
    """Single product resource response."""

    id: int | str
    name: str
    description: str | None = None
    price: float
    stock: int | None = None
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None


class ProductListResponse(BaseModel):
    """GET /api/products — paginated product list."""

    data: list[ProductResponse]
    total: int
    page: int
    per_page: int


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard error response body for 4xx / 5xx status codes."""

    error: str | None = None
    message: str | None = None
    detail: str | list[Any] | None = None
    status_code: int | None = None

    model_config = {"extra": "allow"}
