"""HTTP contract for the local service."""

from app.main import app
from fastapi.testclient import TestClient


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_rejects_other_origins():
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "https://untrusted.example"})
    assert "access-control-allow-origin" not in response.headers
