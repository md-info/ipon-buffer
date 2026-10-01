"""Synthetic wallet API. Single-process demo identity; no real payments."""

import hashlib
import json
import secrets
import time
from contextlib import contextmanager
from dataclasses import asdict
from datetime import date, timedelta
from fractions import Fraction
from math import ceil
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from sqlalchemy import delete, select, update

from app.assistant.service import ModelAdapter
from app.config import load_config
from app.db import Store, audit, canonical, idempotency, sessions, snapshots
from app.engine.buffer import recommend
from app.engine.explain import explain
from app.engine.shock import shock_coverage
from app.engine.types import Balances, EssentialPlan, IncomeSelection, Obligation
from app.sandbox.personas import AS_OF, golden_fixture

Token = Annotated[str | None, Header(alias="X-Demo-Session")]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConsentInput(Input):
    scopes: list[Literal["transactions:read", "balance:read", "buffer:transfer", "ai:parse"]]
    days: Literal[30, 90, 180] = 90


class BillInput(Input):
    id: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=80)
    amount_minor: int = Field(strict=True, gt=0, le=100_000_000)
    due_date: date
    recurrence: Literal["one_off", "monthly"] = "one_off"
    included_in_daily: StrictBool = False
    paid: StrictBool = False


class PlanInput(Input):
    version: int = Field(strict=True, ge=0)
    confirmed: StrictBool
    routine_daily_minor: int = Field(strict=True, ge=0, le=100_000_000)
    next_expected_income: date
    obligations: list[BillInput] = Field(max_length=30)


class TransferInput(Input):
    amount_minor: int = Field(strict=True, gt=0, le=100_000_000)
    idempotency_key: str = Field(min_length=8, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$")
    confirmed: Literal[True]
    recommendation_id: str | None = None


class ParseInput(Input):
    text: str = Field(min_length=1, max_length=2000)


class ApplyInput(Input):
    draft_id: str
    plan: PlanInput


def fail(status, code, message):
    raise HTTPException(status, {"code": code, "message": message})


def initial_state():
    return {
        "available": 200_000,
        "buffer": 50_000,
        "saved": 0,
        "version": 0,
        "consents": {},
        "recommendation": None,
        "plan": {
            "version": 0,
            "confirmed": False,
            "routine_daily_minor": 25_000,
            "next_expected_income": (AS_OF + timedelta(days=4)).isoformat(),
            "obligations": [
                {
                    "id": "bill",
                    "label": "Household bill",
                    "amount_minor": 60_000,
                    "due_date": (AS_OF + timedelta(days=2)).isoformat(),
                    "recurrence": "one_off",
                    "included_in_daily": False,
                    "paid": False,
                }
            ],
        },
    }


def engine_plan(data):
    plan = PlanInput.model_validate(data)
    return EssentialPlan(
        currency="PHP",
        confirmed=plan.confirmed,
        routine_daily_minor=plan.routine_daily_minor,
        next_expected_income=plan.next_expected_income,
        obligations=tuple(
            Obligation(currency="PHP", **bill.model_dump(exclude={"label"}))
            for bill in plan.obligations
        ),
    )


def create_app(database_url="sqlite:///ipon-demo.db", adapter=None):
    app = FastAPI(title="Ipon Buffer", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "X-Demo-Session"],
    )
    store = Store(database_url)
    model = adapter or ModelAdapter()
    app.state.store = store
    market, rules = load_config()
    templates = json.loads(
        (Path(__file__).resolve().parents[3] / "web/src/i18n/reasons.en.json").read_text()
    )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        return JSONResponse({"error": error.detail}, status_code=error.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        return JSONResponse(
            {"error": {"code": "INVALID_INPUT", "message": "Check the submitted fields."}},
            status_code=422,
        )

    @app.exception_handler(ValueError)
    async def value_error(request: Request, error: ValueError):
        return JSONResponse(
            {"error": {"code": "INVALID_INPUT", "message": str(error)}}, status_code=422
        )

    @contextmanager
    def session(token, action):
        if not token or len(token) > 200:
            fail(401, "SESSION_REQUIRED", "Start a new synthetic demo.")
        uid = hashlib.sha256(token.encode()).hexdigest()
        with store.lock, store.engine.begin() as connection:
            raw = connection.execute(select(sessions.c.state).where(sessions.c.id == uid)).scalar()
            if raw is None:
                fail(401, "SESSION_REQUIRED", "This demo session has ended.")
            state = json.loads(raw)
            yield connection, uid, state
            connection.execute(
                update(sessions).where(sessions.c.id == uid).values(state=canonical(state))
            )
            store.log(connection, uid, action)

    def require(state, *scopes):
        missing = [scope for scope in scopes if state["consents"].get(scope, 0) <= time.time()]
        if missing:
            fail(403, "CONSENT_REQUIRED", "Missing consent: " + ", ".join(missing))

    def calculate(state):
        features, _, _, _ = golden_fixture()
        return recommend(
            features,
            Balances(
                currency="PHP", available_minor=state["available"], buffer_minor=state["buffer"]
            ),
            IncomeSelection(event_id="income-60", already_saved_minor=state["saved"]),
            engine_plan(state["plan"]),
            rules,
            market,
        )

    def summary(state):
        rec = calculate(state)
        coverage = shock_coverage(
            state["buffer"],
            rec.monthly_essentials_minor,
            tuple(item.fraction for item in rules.shock_ladder),
        )
        return {
            "available_minor": state["available"],
            "buffer_minor": state["buffer"],
            "version": state["version"],
            "plan": state["plan"],
            "as_of": AS_OF.isoformat(),
            "amount_minor": rec.amount_minor,
            "reserve_minor": rec.reserve_minor,
            "shortfall_minor": rec.shortfall_minor,
            "horizon_days": rec.horizon_days,
            "protected_through": rec.protected_through.isoformat(),
            "room_per_day_minor": rec.estimated_room_per_day_minor,
            "buffer_days": float(rec.buffer_days) if rec.buffer_days is not None else None,
            "stage": asdict(rec.stage) if rec.stage else None,
            "eta_days": rec.eta_days,
            "reasons": explain(rec, market, "en", templates),
            "guardrails": [asdict(check) for check in rec.guardrail_results],
            "coverage": {
                "covered": coverage.covered,
                "total": coverage.total,
                "scenarios": [
                    {"amount_minor": item.amount_minor, "covered": item.covered}
                    for item in coverage.scenarios
                ],
            },
            "assistant_mode": model.mode,
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/v1/sandbox/start")
    def start():
        token = secrets.token_urlsafe(32)
        uid = hashlib.sha256(token.encode()).hexdigest()
        with store.lock, store.engine.begin() as connection:
            connection.execute(sessions.insert().values(id=uid, state=canonical(initial_state())))
            store.log(connection, uid, "sandbox.start")
        return {"token": token, "assistant_mode": model.mode, "as_of": AS_OF.isoformat()}

    @app.post("/api/v1/sandbox/reset")
    def reset(token: Token = None):
        with session(token, "sandbox.reset") as (connection, uid, state):
            state.clear()
            state.update(initial_state())
            connection.execute(delete(snapshots).where(snapshots.c.user_id == uid))
            connection.execute(delete(idempotency).where(idempotency.c.user_id == uid))
            store.drafts.pop(uid, None)
        return {"reset": True}

    @app.post("/api/v1/consents")
    def grant(body: ConsentInput, token: Token = None):
        with session(token, "consent.grant") as (connection, uid, state):
            state["consents"] = {
                scope: int(time.time()) + body.days * 86400 for scope in body.scopes
            }
            state["recommendation"] = None
            connection.execute(delete(snapshots).where(snapshots.c.user_id == uid))
            store.drafts.pop(uid, None)
        return {"granted": body.scopes}

    @app.get("/api/v1/consents")
    def consents(token: Token = None):
        with session(token, "consent.list") as (_, _, state):
            return {"scopes": state["consents"]}

    @app.delete("/api/v1/consents")
    def revoke(token: Token = None):
        with session(token, "consent.revoke") as (connection, uid, state):
            state["consents"] = {}
            state["recommendation"] = None
            connection.execute(delete(snapshots).where(snapshots.c.user_id == uid))
            store.drafts.pop(uid, None)
        return {"revoked": True, "withdrawal_available": True}

    @app.get("/api/v1/wallet")
    def wallet(token: Token = None):
        with session(token, "wallet.read") as (_, _, state):
            return {"available_minor": state["available"], "buffer_minor": state["buffer"]}

    @app.get("/api/v1/summary")
    def get_summary(token: Token = None):
        with session(token, "summary.read") as (connection, uid, state):
            require(state, "transactions:read", "balance:read")
            result = summary(state)
            connection.execute(delete(snapshots).where(snapshots.c.user_id == uid))
            connection.execute(
                snapshots.insert().values(
                    user_id=uid,
                    summary=canonical(
                        {
                            "reserve_minor": result["reserve_minor"],
                            "amount_minor": result["amount_minor"],
                        }
                    ),
                )
            )
            return result

    def save_plan(state, body):
        if body.version != state["version"]:
            fail(409, "REFRESH_REQUIRED", "The plan changed. Review it again.")
        engine_plan(body.model_dump(mode="json"))
        if not AS_OF <= body.next_expected_income <= AS_OF + timedelta(days=366):
            fail(422, "INVALID_DATE", "Use a current or future income date within one year.")
        state["version"] += 1
        state["plan"] = {**body.model_dump(mode="json"), "version": state["version"]}
        state["recommendation"] = None

    @app.put("/api/v1/plan")
    def put_plan(body: PlanInput, token: Token = None):
        with session(token, "plan.confirm") as (_, _, state):
            require(state, "transactions:read", "balance:read")
            save_plan(state, body)
            return summary(state)

    @app.post("/api/v1/recommendation")
    def recommendation(token: Token = None):
        with session(token, "recommendation.create") as (_, _, state):
            require(state, "transactions:read", "balance:read")
            rec = calculate(state)
            result = {
                "id": secrets.token_urlsafe(16),
                "version": state["version"],
                "amount_minor": rec.amount_minor,
            }
            state["recommendation"] = result
            return result

    def move(body, token, operation):
        with session(token, operation) as (connection, uid, state):
            key = uid + ":" + operation + ":" + body.idempotency_key
            fingerprint = hashlib.sha256(canonical(body.model_dump()).encode()).hexdigest()
            prior = connection.execute(select(idempotency).where(idempotency.c.id == key)).first()
            if prior:
                if prior.fingerprint != fingerprint:
                    fail(409, "IDEMPOTENCY_CONFLICT", "This key belongs to a different request.")
                return json.loads(prior.result)
            amount = body.amount_minor
            if operation == "buffer.deposit":
                require(state, "transactions:read", "balance:read", "buffer:transfer")
                rec = state["recommendation"]
                if (
                    not rec
                    or rec["id"] != body.recommendation_id
                    or rec["version"] != state["version"]
                ):
                    fail(
                        409, "REFRESH_REQUIRED", "Review a fresh recommendation before confirming."
                    )
                computed = calculate(state)
                if amount != computed.amount_minor or amount != rec["amount_minor"]:
                    fail(422, "GUARDRAIL_REJECTED", "Confirm only the validated suggested amount.")
                state["available"] -= amount
                state["buffer"] += amount
                state["saved"] += amount
            elif operation == "buffer.withdraw":
                if amount > state["buffer"]:
                    fail(422, "INSUFFICIENT_BUFFER", "The withdrawal exceeds your buffer.")
                state["buffer"] -= amount
                state["available"] += amount
            else:
                if amount > state["available"]:
                    fail(
                        422, "INSUFFICIENT_FUNDS", "The payment exceeds the available mock balance."
                    )
                state["available"] -= amount
            state["version"] += 1
            state["plan"]["version"] = state["version"]
            state["recommendation"] = None
            result = {
                "available_minor": state["available"],
                "buffer_minor": state["buffer"],
                "amount_minor": amount,
                "operation": operation,
            }
            if operation == "buffer.withdraw":
                weekly = min(ceil(Fraction(amount, 8)), 17_500)
                weekly = weekly // market.rounding_step_minor * market.rounding_step_minor
                result["refill"] = (
                    {"weekly_minor": weekly, "estimated_weeks": ceil(Fraction(amount, weekly))}
                    if weekly >= market.min_transfer_minor
                    and state["consents"].get("transactions:read", 0) > time.time()
                    else None
                )
            connection.execute(
                idempotency.insert().values(
                    id=key, user_id=uid, fingerprint=fingerprint, result=canonical(result)
                )
            )
            store.log(connection, uid, operation + ".posted", {"amount_minor": amount})
            return result

    @app.post("/api/v1/buffer/transfer")
    def deposit(body: TransferInput, token: Token = None):
        return move(body, token, "buffer.deposit")

    @app.post("/api/v1/buffer/withdraw")
    def withdraw(body: TransferInput, token: Token = None):
        return move(body, token, "buffer.withdraw")

    @app.post("/api/v1/sandbox/pay-emergency")
    def emergency(body: TransferInput, token: Token = None):
        return move(body, token, "emergency.pay")

    @app.get("/api/v1/audit")
    def get_audit(token: Token = None):
        with session(token, "audit.read") as (connection, uid, _):
            entries = []
            for row in connection.execute(select(audit)):
                try:
                    entry = json.loads(row.payload)
                    if isinstance(entry, dict) and entry.get("user_id") == uid:
                        entries.append(entry)
                except (ValueError, TypeError):
                    pass  # Verification below reports the tampering.
            return {
                "verified": store.verify(connection),
                "entries": entries,
            }

    @app.delete("/api/v1/privacy/data")
    def erase(token: Token = None):
        with session(token, "privacy.delete") as (connection, uid, state):
            connection.execute(delete(snapshots).where(snapshots.c.user_id == uid))
            connection.execute(delete(idempotency).where(idempotency.c.user_id == uid))
            store.drafts.pop(uid, None)
            store.rates.pop(uid, None)
            connection.execute(delete(sessions).where(sessions.c.id == uid))
        return {
            "deleted": True,
            "retained": "Pseudonymous audit metadata and simulated movement amounts remain.",
        }

    @app.post("/api/v1/assistant/parse")
    def parse(body: ParseInput, token: Token = None):
        with session(token, "assistant.request") as (_, uid, state):
            require(state, "ai:parse", "transactions:read", "balance:read")
            if time.time() - store.rates.get(uid, 0) < 2:
                fail(429, "RATE_LIMITED", "Wait a moment before trying again.")
            store.rates[uid] = time.time()
            base_version = state["version"]
            pending_id = secrets.token_urlsafe(16)
            store.drafts[uid] = {"pending_id": pending_id}
        try:
            proposal = model.parse(body.text, AS_OF)
        except Exception:
            fail(
                503,
                "AI_UNAVAILABLE",
                "AI could not draft a plan. Enter the details manually or try again.",
            )
        with session(token, "assistant.draft") as (_, uid, state):
            require(state, "ai:parse", "transactions:read", "balance:read")
            if base_version != state["version"]:
                fail(409, "REFRESH_REQUIRED", "The plan changed while AI was working. Try again.")
            if store.drafts.get(uid, {}).get("pending_id") != pending_id:
                fail(409, "DRAFT_CANCELLED", "This AI request was cancelled or replaced.")
            draft_id = secrets.token_urlsafe(16)
            store.drafts[uid] = {
                "id": draft_id,
                "version": base_version,
                "expires": time.time() + 300,
            }
            return {
                "draft_id": draft_id,
                "version": base_version,
                "proposal": proposal.model_dump(),
                "mode": model.mode,
            }

    @app.delete("/api/v1/assistant/draft")
    def discard(token: Token = None):
        with session(token, "assistant.discard") as (_, uid, _):
            store.drafts.pop(uid, None)
        return {"discarded": True}

    @app.post("/api/v1/assistant/apply")
    def apply(body: ApplyInput, token: Token = None):
        with session(token, "assistant.confirm") as (_, uid, state):
            require(state, "ai:parse", "transactions:read", "balance:read")
            draft = store.drafts.get(uid)
            if (
                not draft
                or draft.get("id") != body.draft_id
                or draft["expires"] < time.time()
                or draft["version"] != state["version"]
            ):
                fail(409, "REFRESH_REQUIRED", "This draft expired or changed. Review a new draft.")
            save_plan(state, body.plan)
            store.drafts.pop(uid, None)
            return summary(state)

    return app
