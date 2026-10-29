"""QuickCart product-service.

Owns the product catalog. The catalog itself is NOT in this code: it comes
from a Kubernetes ConfigMap mounted as a file, so prices can change through
Git without building a new image.

Endpoints (the ALB sends every /api/products request here):
  GET /api/products          all products
  GET /api/products/{id}     one product (order-service calls this)
  GET /api/products/health   health check for Kubernetes and the ALB
"""
import json
import os
import socket

from fastapi import FastAPI, HTTPException

# Change this, push, and watch the new version roll out through the pipeline.
APP_VERSION = "1.0.0"

CATALOG_FILE = os.getenv("CATALOG_FILE", "/config/products.json")

# Used only when the ConfigMap is not mounted (for example on your laptop).
DEFAULT_CATALOG = [
    {"id": 1, "name": "GitOps T-Shirt", "price": 499},
    {"id": 2, "name": "Kubernetes Mug", "price": 299},
]

app = FastAPI(title="QuickCart product-service", version=APP_VERSION)


def load_catalog():
    """Read the catalog on every request, so ConfigMap changes show up live."""
    try:
        with open(CATALOG_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return DEFAULT_CATALOG


@app.get("/api/products/health")
def health():
    return {"status": "ok", "service": "product-service", "version": APP_VERSION}


@app.get("/api/products")
def list_products():
    return {
        "service": "product-service",
        "version": APP_VERSION,
        "pod": socket.gethostname(),
        "products": load_catalog(),
    }


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    for product in load_catalog():
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="product not found")
