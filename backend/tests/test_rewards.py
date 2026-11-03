"""Reward funding and retry invariants."""

from app.api.routes import create_app
from fastapi.testclient import TestClient


def test_purchase_and_redemption_are_atomic_and_idempotent():
    client = TestClient(create_app("sqlite:///:memory:"))
    token = client.post("/api/v1/sandbox/start").json()["token"]
    h = {"X-Demo-Session": token}
    purchase = {
        "offer_id": "demo-grocery",
        "amount_minor": 10000,
        "confirmed": True,
        "idempotency_key": "purchase-123",
    }
    for _ in range(2):
        assert client.post("/api/v1/rewards/purchase", json=purchase, headers=h).status_code == 200
    wallet = client.get("/api/v1/wallet", headers=h).json()
    assert wallet == {"available_minor": 190000, "buffer_minor": 50000}
    result = client.get("/api/v1/rewards", headers=h).json()
    assert result["cashback_minor"] == 1000
    assert result["offers"][0]["remaining"] == 19000
    assert (
        client.post(
            "/api/v1/rewards/purchase",
            json={**purchase, "idempotency_key": "purchase-456"},
            headers=h,
        ).status_code
        == 409
    )
    redeem = {"confirmed": True, "idempotency_key": "redeem-123"}
    for _ in range(2):
        assert client.post("/api/v1/rewards/to-buffer", json=redeem, headers=h).status_code == 200
    assert client.get("/api/v1/wallet", headers=h).json() == {
        "available_minor": 190000,
        "buffer_minor": 51000,
    }
    assert client.get("/api/v1/rewards", headers=h).json()["cashback_minor"] == 0


def test_invalid_purchases_and_campaign_limits():
    c = TestClient(create_app("sqlite:///:memory:"))
    h = {"X-Demo-Session": c.post("/api/v1/sandbox/start").json()["token"]}
    assert c.get("/api/v1/rewards").status_code == 401
    body = {
        "offer_id": "demo-grocery",
        "amount_minor": 5000,
        "confirmed": True,
        "idempotency_key": "invalid-123",
    }
    assert c.post("/api/v1/rewards/purchase", json=body, headers=h).status_code == 422
    campaign = {
        "merchant": "Demo shop",
        "item": "Groceries",
        "minimum": 10000,
        "cashback": 500,
        "budget": 500,
    }
    rid = c.post("/api/v1/rewards/campaigns", json=campaign, headers=h).json()["id"]
    assert (
        c.post(
            "/api/v1/rewards/purchase",
            json={**body, "offer_id": rid, "amount_minor": 10000},
            headers=h,
        ).status_code
        == 409
    )
    other = {"X-Demo-Session": c.post("/api/v1/sandbox/start").json()["token"]}
    assert (
        c.post(
            "/api/v1/rewards/purchase",
            json={**body, "offer_id": rid, "amount_minor": 10000},
            headers=other,
        ).status_code
        == 200
    )
    third = {"X-Demo-Session": c.post("/api/v1/sandbox/start").json()["token"]}
    assert (
        c.post(
            "/api/v1/rewards/purchase",
            json={**body, "offer_id": rid, "amount_minor": 10000},
            headers=third,
        ).status_code
        == 409
    )
