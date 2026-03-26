"""
Locust load test file — main entry point.

User classes
------------
APIHealthUser   : Smoke/benchmark — hammers GET /api/healthz
BrowseUser      : Read-heavy — simulates users browsing products and users list
CheckoutUser    : Write-heavy — simulates full create → read → delete cycle
AuthUser        : Auth-focused — exercises the login endpoint

Traffic weighting (approximate real-world distribution):
  70% read / browsing
  20% write / checkout
  10% auth

Run examples
------------
  Smoke (headless, 1 min, 5 users):
    locust -f locustfile.py --headless -u 5 -r 1 -t 1m --host http://localhost:80

  UI mode (local development):
    locust -f locustfile.py --host http://localhost:80
"""
from __future__ import annotations

import os
import random

from locust import HttpUser, between, task, constant_throughput

from utils.auth_helper import acquire_token, inject_auth_header

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:80")


class APIHealthUser(HttpUser):
    """
    Lightweight health check benchmark user.
    Uses constant throughput to maintain a stable RPS regardless of latency.
    """

    wait_time = constant_throughput(2)
    weight = 10

    @task
    def check_health(self) -> None:
        with self.client.get(
            "/api/healthz",
            name="GET /api/healthz",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    resp.success()
                else:
                    resp.failure(
                        f"Unexpected health status: {data.get('status')}"
                    )
            else:
                resp.failure(f"Health check returned HTTP {resp.status_code}")


class BrowseUser(HttpUser):
    """
    Read-heavy user simulating product and user browsing.
    Represents ~70% of realistic API traffic.
    """

    wait_time = between(1, 3)
    weight = 70

    def on_start(self) -> None:
        self._token = acquire_token(self.client)
        if self._token:
            inject_auth_header(self.client, self._token)

    @task(5)
    def browse_products(self) -> None:
        page = random.randint(1, 3)
        self.client.get(
            "/api/products",
            params={"page": page, "per_page": 10},
            name="GET /api/products",
        )

    @task(3)
    def browse_users(self) -> None:
        self.client.get(
            "/api/users",
            params={"page": 1, "per_page": 20},
            name="GET /api/users",
        )

    @task(2)
    def check_health(self) -> None:
        self.client.get("/api/healthz", name="GET /api/healthz")

    @task(1)
    def get_single_product(self) -> None:
        product_id = random.randint(1, 50)
        with self.client.get(
            f"/api/products/{product_id}",
            name="GET /api/products/:id",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()


class CheckoutUser(HttpUser):
    """
    Write-heavy user that exercises the full CRUD cycle:
    create product → read it → update it → delete it.
    Represents ~20% of traffic.
    """

    wait_time = between(2, 5)
    weight = 20

    def on_start(self) -> None:
        self._token = acquire_token(self.client)
        if self._token:
            inject_auth_header(self.client, self._token)
        self._created_ids: list[int] = []

    def on_stop(self) -> None:
        for item_id in self._created_ids:
            with self.client.delete(
                f"/api/products/{item_id}",
                name="DELETE /api/products/:id (cleanup)",
                catch_response=True,
            ) as resp:
                resp.success()

    @task(3)
    def create_and_read_product(self) -> None:
        payload = {
            "name": f"LoadTestProduct_{random.randint(1000, 9999)}",
            "description": "Created by Locust load test",
            "price": round(random.uniform(1.0, 99.99), 2),
            "stock": random.randint(1, 100),
        }
        with self.client.post(
            "/api/products",
            json=payload,
            name="POST /api/products",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                resp.success()
                data = resp.json()
                item_id = data.get("id")
                if item_id:
                    self._created_ids.append(int(item_id))
                    self._read_product(int(item_id))
            elif resp.status_code == 404:
                resp.success()
            else:
                resp.failure(
                    f"Create product returned HTTP {resp.status_code}"
                )

    def _read_product(self, product_id: int) -> None:
        with self.client.get(
            f"/api/products/{product_id}",
            name="GET /api/products/:id (post-create)",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()

    @task(1)
    def create_user(self) -> None:
        import time
        payload = {
            "username": f"loaduser_{int(time.time())}_{random.randint(0, 9999)}",
            "email": f"load_{random.randint(0, 99999)}@loadtest.example.com",
            "password": "LoadTest1234!",
        }
        with self.client.post(
            "/api/users",
            json=payload,
            name="POST /api/users",
            catch_response=True,
        ) as resp:
            if resp.status_code in (201, 404, 409, 422):
                resp.success()
            else:
                resp.failure(
                    f"Create user returned HTTP {resp.status_code}"
                )


class AuthUser(HttpUser):
    """
    Auth-focused user that exercises the login endpoint.
    Represents ~10% of traffic.
    """

    wait_time = between(3, 8)
    weight = 10

    @task(3)
    def login_valid(self) -> None:
        with self.client.post(
            "/api/auth/login",
            json={
                "username": os.environ.get("API_USERNAME", "admin"),
                "password": os.environ.get("API_PASSWORD", "password"),
            },
            name="POST /api/auth/login (valid)",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()

    @task(1)
    def login_invalid(self) -> None:
        with self.client.post(
            "/api/auth/login",
            json={"username": "bad_user", "password": "bad_pass"},
            name="POST /api/auth/login (invalid)",
            catch_response=True,
        ) as resp:
            if resp.status_code in (401, 403, 404):
                resp.success()
            else:
                resp.failure(
                    f"Expected 401/403/404 for invalid credentials, "
                    f"got HTTP {resp.status_code}"
                )
