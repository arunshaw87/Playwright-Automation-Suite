"""
Product CRUD endpoint tests.

Covers: GET /api/products, GET /api/products/{id},
        POST /api/products, PUT /api/products/{id}, DELETE /api/products/{id}

Every response is validated against a Pydantic v2 schema:
- Success responses → ProductResponse / ProductListResponse
- Error responses   → ErrorResponse

All tests are skipped when /api/products returns 404,
meaning the endpoint is not implemented on the target server.
"""
from __future__ import annotations

import pytest
import httpx

from models.responses import ProductResponse, ProductListResponse, ErrorResponse
from utils.validators import (
    assert_status,
    assert_schema,
    assert_pagination,
    assert_error_response,
    assert_content_type_json,
)
from utils.data_factory import make_product_payload, make_partial_product_payload

PRODUCTS_PATH = "/api/products"


def _products_available(client: httpx.Client) -> bool:
    try:
        r = client.get(PRODUCTS_PATH)
        return r.status_code != 404
    except Exception:
        return False


def _skip_if_unavailable(client: httpx.Client) -> None:
    if not _products_available(client):
        pytest.skip("Products endpoint not available on target server")


# ---------------------------------------------------------------------------
# GET /api/products
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.products
class TestGetProducts:
    def test_list_products_returns_200(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(PRODUCTS_PATH)
        assert_status(response, 200)
        assert_schema(response, ProductListResponse)

    def test_list_products_content_type_json(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(PRODUCTS_PATH)
        assert_content_type_json(response)

    def test_list_products_schema_valid(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(PRODUCTS_PATH)
        assert_status(response, 200)
        data = assert_schema(response, ProductListResponse)
        assert isinstance(data.data, list)

    def test_list_products_pagination_present(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(PRODUCTS_PATH)
        data = assert_schema(response, ProductListResponse)
        assert_pagination(data)

    def test_list_products_unauthenticated_returns_401(
        self, unauth_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(unauth_client)
        response = unauth_client.get(PRODUCTS_PATH)
        assert_error_response(response, 401)
        assert_schema(response, ErrorResponse)

    def test_list_products_pagination_query_params(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(PRODUCTS_PATH, params={"page": 1, "per_page": 5})
        assert_status(response, 200)
        data = assert_schema(response, ProductListResponse)
        assert len(data.data) <= 5, "Should return at most per_page=5 items"


# ---------------------------------------------------------------------------
# GET /api/products/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.products
class TestGetSingleProduct:
    def test_get_existing_product_returns_200(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        list_resp = api_client.get(PRODUCTS_PATH)
        products = list_resp.json().get("data", [])
        if not products:
            pytest.skip("No products seeded to fetch individually")
        product_id = products[0]["id"]
        response = api_client.get(f"{PRODUCTS_PATH}/{product_id}")
        assert_status(response, 200)
        data = assert_schema(response, ProductResponse)
        assert str(data.id) == str(product_id)

    def test_get_nonexistent_product_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(f"{PRODUCTS_PATH}/999999999")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)

    def test_get_invalid_product_id_returns_4xx(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.get(f"{PRODUCTS_PATH}/not-a-valid-id")
        assert response.status_code in (400, 404, 422), (
            f"Expected 4xx for invalid product ID, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# POST /api/products
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.products
class TestCreateProduct:
    def test_create_product_returns_201(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        payload = make_product_payload()
        response = api_client.post(PRODUCTS_PATH, json=payload)
        assert_status(response, 201)
        assert_schema(response, ProductResponse)

    def test_create_product_schema_valid(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        payload = make_product_payload()
        response = api_client.post(PRODUCTS_PATH, json=payload)
        assert_status(response, 201)
        data = assert_schema(response, ProductResponse)
        assert data.name == payload["name"]
        assert abs(data.price - payload["price"]) < 0.001

    def test_create_product_missing_name_returns_422(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = make_product_payload()
        del payload["name"]
        response = api_client.post(PRODUCTS_PATH, json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for missing name, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_product_missing_price_returns_422(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = make_product_payload()
        del payload["price"]
        response = api_client.post(PRODUCTS_PATH, json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for missing price, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_product_negative_price_returns_422(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        payload = make_product_payload(price=-5.0)
        response = api_client.post(PRODUCTS_PATH, json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for negative price, got {response.status_code}"
        )
        assert_schema(response, ErrorResponse)

    def test_create_product_unauthenticated_returns_401(
        self, unauth_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(unauth_client)
        response = unauth_client.post(PRODUCTS_PATH, json=make_product_payload())
        assert_error_response(response, 401)
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# PUT /api/products/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.products
class TestUpdateProduct:
    def _create_product(self, client: httpx.Client) -> dict:
        payload = make_product_payload()
        r = client.post(PRODUCTS_PATH, json=payload)
        if r.status_code != 201:
            pytest.skip("Product creation not available — cannot test update")
        return r.json()

    def test_update_product_returns_200(self, api_client: httpx.Client) -> None:
        _skip_if_unavailable(api_client)
        product = self._create_product(api_client)
        payload = make_partial_product_payload()
        response = api_client.put(
            f"{PRODUCTS_PATH}/{product['id']}", json=payload
        )
        assert_status(response, 200)
        assert_schema(response, ProductResponse)

    def test_update_product_reflects_new_price(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        product = self._create_product(api_client)
        new_price = 123.45
        payload = make_partial_product_payload(price=new_price)
        response = api_client.put(
            f"{PRODUCTS_PATH}/{product['id']}", json=payload
        )
        assert_status(response, 200)
        data = assert_schema(response, ProductResponse)
        assert abs(data.price - new_price) < 0.001, (
            f"Expected price {new_price}, got {data.price}"
        )

    def test_update_nonexistent_product_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.put(
            f"{PRODUCTS_PATH}/999999999", json=make_partial_product_payload()
        )
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)


# ---------------------------------------------------------------------------
# DELETE /api/products/{id}
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.products
class TestDeleteProduct:
    def _create_product(self, client: httpx.Client) -> dict:
        payload = make_product_payload()
        r = client.post(PRODUCTS_PATH, json=payload)
        if r.status_code != 201:
            pytest.skip("Product creation not available — cannot test delete")
        return r.json()

    def test_delete_product_returns_200_or_204(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        product = self._create_product(api_client)
        response = api_client.delete(f"{PRODUCTS_PATH}/{product['id']}")
        assert response.status_code in (200, 204), (
            f"Expected 200 or 204 on delete, got {response.status_code}"
        )

    def test_delete_product_then_get_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        product = self._create_product(api_client)
        api_client.delete(f"{PRODUCTS_PATH}/{product['id']}")
        response = api_client.get(f"{PRODUCTS_PATH}/{product['id']}")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)

    def test_delete_nonexistent_product_returns_404(
        self, api_client: httpx.Client
    ) -> None:
        _skip_if_unavailable(api_client)
        response = api_client.delete(f"{PRODUCTS_PATH}/999999999")
        assert_error_response(response, 404)
        assert_schema(response, ErrorResponse)
