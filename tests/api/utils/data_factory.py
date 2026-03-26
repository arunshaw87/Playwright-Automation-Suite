"""
Test data factory using Faker to generate realistic, randomised payloads.

Usage::

    from utils.data_factory import make_user_payload, make_product_payload

    user = make_user_payload()
    product = make_product_payload(price=9.99)
"""
from __future__ import annotations

import random
from typing import Any

from faker import Faker

fake = Faker()


def make_user_payload(
    *,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> dict[str, Any]:
    """Generate a valid user creation payload."""
    return {
        "username": username or fake.user_name(),
        "email": email or fake.unique.email(),
        "password": password or fake.password(length=12),
    }


def make_product_payload(
    *,
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    stock: int | None = None,
) -> dict[str, Any]:
    """Generate a valid product creation payload."""
    return {
        "name": name or fake.catch_phrase(),
        "description": description or fake.paragraph(nb_sentences=2),
        "price": price if price is not None else round(random.uniform(1.0, 999.99), 2),
        "stock": stock if stock is not None else random.randint(0, 500),
    }


def make_login_payload(
    *,
    username: str = "admin",
    password: str = "password",
) -> dict[str, Any]:
    """Generate a login credentials payload."""
    return {"username": username, "password": password}


def make_partial_user_payload(**overrides: Any) -> dict[str, Any]:
    """Generate a partial user payload for PATCH/PUT updates."""
    base = {
        "username": fake.user_name(),
        "email": fake.unique.email(),
    }
    base.update(overrides)
    return base


def make_partial_product_payload(**overrides: Any) -> dict[str, Any]:
    """Generate a partial product payload for PATCH/PUT updates."""
    base = {
        "name": fake.catch_phrase(),
        "price": round(random.uniform(1.0, 999.99), 2),
    }
    base.update(overrides)
    return base
