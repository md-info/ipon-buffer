"""End-to-end mock ledger, consent, privacy, and AI confirmation contracts."""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from app.api.routes import create_app
from app.assistant.service import Candidate, Proposal
from app.db import audit, sessions, snapshots
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, update

SCOPES = ["transactions:read", "balance:read", "buffer:transfer", "ai:parse"]


class FixtureModel:
    mode = "fixture"

    def parse(self, text, reference_date):
        return Proposal(
            status="needs_clarification",
            candidates=[
                Candidate(
                    label="School",
                    amount="300",
                    currency="PHP",
                    due_date="2026-09-29",
                    recurrence="one_off",
                    included_in_daily=None,
                    source_excerpt=text,
                )
            ],
            expected_income_date=None,
            income_tentative=False,
            clarification="Is this already included in everyday essentials?",
        )


@pytest.fixture
def client():
    app = create_app("sqlite:///:memory:", FixtureModel())
    with TestClient(app) as result:
        yield result


def begin(client, consent=True, confirm=True):
    token = client.post("/api/v1/sandbox/start").json()["token"]
    headers = {"X-Demo-Session": token}
    if consent:
        assert (
            client.post("/api/v1/consents", headers=headers, json={"scopes": SCOPES}).status_code
            == 200
        )
    if confirm:
        plan = client.get("/api/v1/summary", headers=headers).json()["plan"]
        plan["confirmed"] = True
        assert client.put("/api/v1/plan", headers=headers, json=plan).status_code == 200
    return headers


def deposit_request(client, headers):
    rec = client.post("/api/v1/recommendation", headers=headers).json()
    return {
        "amount_minor": rec["amount_minor"],
        "recommendation_id": rec["id"],
        "confirmed": True,
        "idempotency_key": "deposit-first",
    }


def test_complete_flow_and_accounting(client):
    headers = begin(client)
    summary = client.get("/api/v1/summary", headers=headers).json()
    assert summary["amount_minor"] == 12_000
    request = deposit_request(client, headers)
    deposit = client.post("/api/v1/buffer/transfer", headers=headers, json=request).json()
    assert deposit["available_minor"] == 188_000 and deposit["buffer_minor"] == 62_000
    assert client.post("/api/v1/buffer/transfer", headers=headers, json=request).json() == deposit
    withdraw = client.post(
        "/api/v1/buffer/withdraw",
        headers=headers,
        json={"amount_minor": 60_000, "confirmed": True, "idempotency_key": "withdraw-1"},
    ).json()
    assert withdraw["available_minor"] == 248_000 and withdraw["buffer_minor"] == 2000
    assert withdraw["refill"] == {"weekly_minor": 7500, "estimated_weeks": 8}
    pay = client.post(
        "/api/v1/sandbox/pay-emergency",
        headers=headers,
        json={"amount_minor": 60_000, "confirmed": True, "idempotency_key": "payment-1"},
    ).json()
    assert pay["available_minor"] + pay["buffer_minor"] == 190_000
    assert client.get("/api/v1/audit", headers=headers).json()["verified"]


@pytest.mark.parametrize(
    "daily,deposit,reserve,wallet_after",
    [(25_000, 12_000, 176_000, "PHP 1,880.00"), (27_500, 6500, 187_000, "PHP 1,935.00")],
)
def test_explanation_distinguishes_wallet_after_deposit_from_reserve(
    client, daily, deposit, reserve, wallet_after
):
    headers = begin(client)
    plan = client.get("/api/v1/summary", headers=headers).json()["plan"]
    plan["routine_daily_minor"] = daily
    response = client.put("/api/v1/plan", headers=headers, json=plan)
    assert response.status_code == 200
    summary = response.json()
    assert summary["amount_minor"] == deposit
    assert summary["reserve_minor"] == reserve
    assert (
        f"This would leave {wallet_after} in your wallet, including an estimated"
        in summary["reasons"][0]
    )
    # A suggestion and its explanation must not move money.
    assert summary["available_minor"] == 200_000
    assert summary["buffer_minor"] == 50_000


def test_scenario_basis_and_fraction_match_expenses(client):
    headers = begin(client)
    summary = client.get("/api/v1/summary", headers=headers).json()
    coverage = summary["coverage"]
    assert coverage["monthly_essentials_minor"] == 750_000
    assert coverage["scenarios"] == [
        {"amount_minor": 187_500, "covered": False, "month_fraction": "1/4"},
        {"amount_minor": 375_000, "covered": False, "month_fraction": "1/2"},
        {"amount_minor": 750_000, "covered": False, "month_fraction": "1"},
    ]


def test_consent_gate_and_revoke_withdraw(client):
    headers = begin(client, consent=False, confirm=False)
    assert client.get("/api/v1/summary", headers=headers).status_code == 403
    client.post("/api/v1/consents", headers=headers, json={"scopes": SCOPES})
    client.get("/api/v1/summary", headers=headers)
    client.delete("/api/v1/consents", headers=headers)
    assert client.get("/api/v1/summary", headers=headers).status_code == 403
    response = client.post(
        "/api/v1/buffer/withdraw",
        headers=headers,
        json={"amount_minor": 100, "confirmed": True, "idempotency_key": "withdraw-1"},
    )
    assert response.status_code == 200
    assert response.json()["refill"] is None
    with client.app.state.store.engine.connect() as connection:
        assert connection.execute(select(snapshots)).first() is None


def test_expiry(client):
    headers = begin(client)
    uid = hashlib.sha256(headers["X-Demo-Session"].encode()).hexdigest()
    with client.app.state.store.engine.begin() as connection:
        state = json.loads(
            connection.execute(select(sessions.c.state).where(sessions.c.id == uid)).scalar()
        )
        state["consents"] = {scope: 1 for scope in SCOPES}
        connection.execute(
            update(sessions).where(sessions.c.id == uid).values(state=json.dumps(state))
        )
    assert client.get("/api/v1/summary", headers=headers).status_code == 403


def test_stale_recommendation_and_changed_payload(client):
    headers = begin(client)
    body = deposit_request(client, headers)
    tampered = {**body, "amount_minor": 50_000}
    assert client.post("/api/v1/buffer/transfer", headers=headers, json=tampered).status_code == 422
    assert client.post("/api/v1/buffer/transfer", headers=headers, json=body).status_code == 200
    assert client.post("/api/v1/buffer/transfer", headers=headers, json=tampered).status_code == 409
    assert (
        client.post(
            "/api/v1/buffer/transfer",
            headers=headers,
            json={**body, "idempotency_key": "different-key"},
        ).status_code
        == 409
    )


def test_concurrent_confirmation_moves_once(client):
    headers = begin(client)
    body = deposit_request(client, headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda key: client.post(
                    "/api/v1/buffer/transfer",
                    headers=headers,
                    json={**body, "idempotency_key": key},
                ),
                ["request-one", "request-two"],
            )
        )
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert client.get("/api/v1/wallet", headers=headers).json()["buffer_minor"] == 62_000


def test_cumulative_event_cap(client):
    headers = begin(client)
    for i in range(10):
        body = deposit_request(client, headers)
        if not body["amount_minor"]:
            break
        body["idempotency_key"] = f"deposit-{i}"
        assert client.post("/api/v1/buffer/transfer", headers=headers, json=body).status_code == 200
    wallet = client.get("/api/v1/wallet", headers=headers).json()
    assert wallet["buffer_minor"] - 50_000 <= 20_000
    assert wallet["available_minor"] + wallet["buffer_minor"] == 250_000


def test_ai_draft_has_no_effect_until_review(client):
    headers = begin(client)
    before = client.get("/api/v1/summary", headers=headers).json()
    draft = client.post(
        "/api/v1/assistant/parse",
        headers=headers,
        json={"text": "I also need 300 pesos for school tomorrow."},
    ).json()
    after = client.get("/api/v1/summary", headers=headers).json()
    assert before == after
    assert draft["mode"] == "fixture"
    plan = after["plan"]
    plan["obligations"].append(
        {
            "id": "school",
            "label": "School",
            "amount_minor": 30_000,
            "due_date": "2026-09-29",
            "included_in_daily": False,
        }
    )
    response = client.post(
        "/api/v1/assistant/apply",
        headers=headers,
        json={"draft_id": draft["draft_id"], "plan": plan},
    )
    assert response.status_code == 200
    assert response.json()["amount_minor"] == 0
    assert response.json()["shortfall_minor"] == 9000
    assert (
        client.post(
            "/api/v1/assistant/apply",
            headers=headers,
            json={"draft_id": draft["draft_id"], "plan": plan},
        ).status_code
        == 409
    )


def test_cross_session_draft_and_delete(client):
    first, second = begin(client), begin(client)
    draft = client.post(
        "/api/v1/assistant/parse", headers=first, json={"text": "School tomorrow"}
    ).json()
    plan = client.get("/api/v1/summary", headers=second).json()["plan"]
    assert (
        client.post(
            "/api/v1/assistant/apply",
            headers=second,
            json={"draft_id": draft["draft_id"], "plan": plan},
        ).status_code
        == 409
    )
    assert client.delete("/api/v1/privacy/data", headers=first).status_code == 200
    assert client.get("/api/v1/wallet", headers=first).status_code == 401
    assert client.get("/api/v1/wallet", headers=second).status_code == 200


def test_missing_ai_and_failed_input_do_not_disable_manual_flow():
    with TestClient(create_app("sqlite:///:memory:")) as client:
        headers = begin(client)
        assert (
            client.post(
                "/api/v1/assistant/parse", headers=headers, json={"text": "School tomorrow"}
            ).status_code
            == 503
        )
        assert client.get("/api/v1/summary", headers=headers).json()["amount_minor"] == 12_000


def test_tamper_detection_and_no_transaction_table(client):
    headers = begin(client)
    store = client.app.state.store
    assert "transactions" not in inspect(store.engine).get_table_names()
    with store.engine.begin() as connection:
        connection.execute(update(audit).where(audit.c.id == 1).values(payload="{}"))
    assert not client.get("/api/v1/audit", headers=headers).json()["verified"]


@pytest.mark.parametrize("amount", [-1, 0, 0.1, "100", 100_000_001])
def test_bad_transfer_amounts(client, amount):
    headers = begin(client)
    assert (
        client.post(
            "/api/v1/buffer/withdraw",
            headers=headers,
            json={"amount_minor": amount, "confirmed": True, "idempotency_key": "request-bad"},
        ).status_code
        == 422
    )
