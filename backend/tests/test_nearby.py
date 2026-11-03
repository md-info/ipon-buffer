"""Community invariants: identity, idempotency, evidence and wallet isolation."""

import time

from app.api.routes import create_app
from fastapi.testclient import TestClient


def setup():
    client = TestClient(create_app("sqlite:///:memory:"))

    def user():
        return {"X-Demo-Session": client.post("/api/v1/sandbox/start").json()["token"]}

    return client, user


def report():
    return {
        "item": "Demo rice",
        "quantity": "1 kg",
        "store": "Example store",
        "area": "Demo Central",
        "price_minor": 5800,
        "observed_at": int(time.time()),
    }


def test_confirmations_unique_capped_and_no_wallet_change():
    client, user = setup()
    author = user()
    before = client.get("/api/v1/wallet", headers=author).json()
    rid = client.post("/api/v1/nearby", json=report(), headers=author).json()["id"]
    url = f"/api/v1/nearby/{rid}/react"
    assert client.post(url, json={"kind": "confirmed"}, headers=author).status_code == 409
    for _ in range(4):
        shopper = user()
        for _ in range(2):
            assert client.post(url, json={"kind": "confirmed"}, headers=shopper).status_code == 200
    feed = client.get("/api/v1/nearby", headers=author).json()
    assert feed["points"] == 15
    assert feed["reports"][0]["counts"]["confirmed"] == 4
    assert client.get("/api/v1/wallet", headers=author).json() == before


def test_helpfulness_not_points_and_conflicting_observation():
    client, user = setup()
    author, shopper = user(), user()
    rid = client.post("/api/v1/nearby", json=report(), headers=author).json()["id"]
    url = f"/api/v1/nearby/{rid}/react"
    client.post(url, json={"kind": "helpful"}, headers=shopper)
    assert client.get("/api/v1/nearby", headers=author).json()["points"] == 0
    client.post(url, json={"kind": "confirmed"}, headers=shopper)
    client.post(url, json={"kind": "changed"}, headers=shopper)
    assert client.get("/api/v1/nearby", headers=author).json()["points"] == 0


def test_auth_validation_flag_and_owner_delete():
    client, user = setup()
    author, shopper = user(), user()
    assert client.get("/api/v1/nearby").status_code == 401
    assert (
        client.post(
            "/api/v1/nearby", json={**report(), "photo": "javascript:bad"}, headers=author
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/nearby", json={**report(), "price_minor": 0}, headers=author
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/nearby",
            json={**report(), "observed_at": int(time.time()) + 3600},
            headers=author,
        ).status_code
        == 422
    )
    rid = client.post("/api/v1/nearby", json=report(), headers=author).json()["id"]
    assert client.delete(f"/api/v1/nearby/{rid}", headers=shopper).status_code == 404
    client.post(f"/api/v1/nearby/{rid}/react", json={"kind": "flagged"}, headers=shopper)
    assert not client.get("/api/v1/nearby", headers=shopper).json()["reports"]
    assert client.delete(f"/api/v1/nearby/{rid}", headers=author).status_code == 200
    assert not client.get("/api/v1/nearby", headers=author).json()["reports"]


def test_stale_price_and_privacy_cleanup():
    client, user = setup()
    author, shopper = user(), user()
    data = {**report(), "observed_at": int(time.time()) - 90000}
    rid = client.post("/api/v1/nearby", json=data, headers=author).json()["id"]
    response = client.post(
        f"/api/v1/nearby/{rid}/react", json={"kind": "confirmed"}, headers=shopper
    )
    assert response.status_code == 409
    assert client.get("/api/v1/nearby", headers=shopper).json()["reports"][0]["stale"]
    assert client.delete("/api/v1/privacy/data", headers=author).status_code == 200
    assert not client.get("/api/v1/nearby", headers=shopper).json()["reports"]
