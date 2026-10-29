"""Unit tests for order-service. The CI pipeline runs these before building any image.

product-service is not running in CI, so we replace the HTTP call with a fake one.
"""
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


class FakeResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


def test_health():
    r = client.get("/api/orders/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_order_total_uses_price_from_product_service(monkeypatch):
    monkeypatch.setattr(main.httpx, "get",
                        lambda url, timeout: FakeResponse(200, {"id": 2, "name": "Kubernetes Mug", "price": 299}))
    r = client.post("/api/orders", json={"product_id": 2, "quantity": 3})
    assert r.status_code == 201
    assert r.json()["total"] == 897


def test_unknown_product_returns_404(monkeypatch):
    monkeypatch.setattr(main.httpx, "get", lambda url, timeout: FakeResponse(404))
    r = client.post("/api/orders", json={"product_id": 999, "quantity": 1})
    assert r.status_code == 404


def test_quantity_limit():
    r = client.post("/api/orders", json={"product_id": 1, "quantity": 50})
    assert r.status_code == 422
