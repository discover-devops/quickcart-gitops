"""Unit tests for product-service. The CI pipeline runs these before building any image."""
import os

os.environ["CATALOG_FILE"] = "/nonexistent/products.json"  # use the built-in catalog

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)


def test_health():
    r = client.get("/api/products/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_products():
    r = client.get("/api/products")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "product-service"
    assert len(body["products"]) > 0


def test_get_one_product():
    r = client.get("/api/products/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_unknown_product_returns_404():
    r = client.get("/api/products/999")
    assert r.status_code == 404
