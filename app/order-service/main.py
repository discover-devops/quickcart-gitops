"""QuickCart order-service.

Takes an order, asks product-service for the real price, and returns a
confirmation. This is service-to-service communication inside Kubernetes:
order-service reaches product-service through its Service name.

Endpoints (the ALB sends every /api/orders request here):
  POST /api/orders          place an order  {"product_id": 1, "quantity": 2}
  GET  /api/orders/health   health check for Kubernetes and the ALB
"""
import os
import socket
import uuid

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = "1.0.0"

# Kubernetes DNS name of the product-service Service (set in the Deployment).
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service")

app = FastAPI(title="QuickCart order-service", version=APP_VERSION)


class OrderIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=10)


@app.get("/api/orders/health")
def health():
    return {"status": "ok", "service": "order-service", "version": APP_VERSION}


@app.post("/api/orders", status_code=201)
def place_order(order: OrderIn):
    # Never trust a price sent by the browser: ask product-service.
    try:
        resp = httpx.get(f"{PRODUCT_SERVICE_URL}/api/products/{order.product_id}", timeout=3)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"product-service unreachable: {exc}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="product not found")
    resp.raise_for_status()
    product = resp.json()

    return {
        "order_id": uuid.uuid4().hex[:8],
        "product": product["name"],
        "quantity": order.quantity,
        "unit_price": product["price"],
        "total": product["price"] * order.quantity,
        "handled_by": socket.gethostname(),
        "version": APP_VERSION,
    }
