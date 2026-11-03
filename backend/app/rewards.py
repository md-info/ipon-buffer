"""Funded synthetic merchant offers. No real settlement or partner connection."""

import json
import time
from typing import Annotated, Literal

from fastapi import Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Integer, MetaData, String, Table, select

meta = MetaData()
campaigns = Table(
    "reward_campaigns",
    meta,
    Column("id", String, primary_key=True),
    Column("owner", String),
    Column("merchant", String),
    Column("item", String),
    Column("minimum", Integer),
    Column("cashback", Integer),
    Column("budget", Integer),
    Column("remaining", Integer),
    Column("expires", Integer),
)
Token = Annotated[str | None, Header(alias="X-Demo-Session")]


class Purchase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    offer_id: str
    amount_minor: int = Field(strict=True, gt=0, le=100000000)
    confirmed: Literal[True]
    idempotency_key: str = Field(min_length=8, max_length=100)


class Redeem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmed: Literal[True]
    idempotency_key: str = Field(min_length=8, max_length=100)


class Campaign(BaseModel):
    model_config = ConfigDict(extra="forbid")
    merchant: str = Field(min_length=2, max_length=80)
    item: str = Field(min_length=2, max_length=100)
    minimum: int = Field(strict=True, ge=100, le=1000000)
    cashback: int = Field(strict=True, ge=100, le=100000)
    budget: int = Field(strict=True, ge=100, le=10000000)


def install_rewards(app, store, session):
    from app.db import canonical, idempotency

    meta.create_all(store.engine)
    with store.engine.begin() as conn:
        if not conn.execute(select(campaigns.c.id).where(campaigns.c.id == "demo-grocery")).first():
            conn.execute(
                campaigns.insert().values(
                    id="demo-grocery",
                    owner="demo-partner",
                    merchant="Reyes Family Grocery · demo",
                    item="Planned grocery purchase",
                    minimum=10000,
                    cashback=1000,
                    budget=20000,
                    remaining=20000,
                    expires=int(time.time()) + 30 * 86400,
                )
            )

    def fail(code, message):
        raise HTTPException(code, {"message": message})

    def change(state):
        state["version"] += 1
        state["plan"]["version"] = state["version"]
        state["recommendation"] = None

    def prior(conn, uid, operation, key, body):
        full = uid + ":" + operation + ":" + key
        fingerprint = canonical(body)
        old = conn.execute(select(idempotency).where(idempotency.c.id == full)).mappings().first()
        if old and old["fingerprint"] != fingerprint:
            fail(409, "This request key was already used with different details.")
        return full, fingerprint, json.loads(old["result"]) if old else None

    def record(conn, uid, full, fingerprint, result):
        conn.execute(
            idempotency.insert().values(
                id=full, user_id=uid, fingerprint=fingerprint, result=json.dumps(result)
            )
        )
        return result

    @app.get("/api/v1/rewards")
    def read(token: Token = None):
        with session(token, "rewards.read") as (conn, uid, state):
            rows = [dict(r) for r in conn.execute(select(campaigns)).mappings()]
            return {
                "offers": [
                    {k: v for k, v in r.items() if k != "owner"}
                    | {"mine": r["owner"] == uid, "expired": r["expires"] < time.time()}
                    for r in rows
                ],
                "cashback_minor": state.get("cashback", 0),
                "claimed": state.get("reward_claimed", []),
                "receipts": state.get("reward_receipts", []),
            }

    @app.post("/api/v1/rewards/campaigns")
    def create(body: Campaign, token: Token = None):
        import uuid

        if not body.merchant.strip() or not body.item.strip():
            fail(422, "Merchant and eligible purchase are required.")
        if body.cashback > body.minimum or body.budget < body.cashback:
            fail(422, "Cashback must fit the purchase and campaign budget.")
        with session(token, "rewards.campaign.create") as (conn, uid, _):
            own = list(conn.execute(select(campaigns.c.id).where(campaigns.c.owner == uid)))
            if len(own) >= 5:
                fail(429, "Demo limit: five campaigns per session.")
            rid = uuid.uuid4().hex
            conn.execute(
                campaigns.insert().values(
                    id=rid,
                    owner=uid,
                    **body.model_dump(),
                    remaining=body.budget,
                    expires=int(time.time()) + 7 * 86400,
                )
            )
            return {"id": rid}

    @app.post("/api/v1/rewards/purchase")
    def purchase(body: Purchase, token: Token = None):
        with session(token, "rewards.purchase") as (conn, uid, state):
            full, fingerprint, old = prior(
                conn, uid, "reward.purchase", body.idempotency_key, body.model_dump()
            )
            if old is not None:
                return old
            offer = (
                conn.execute(select(campaigns).where(campaigns.c.id == body.offer_id))
                .mappings()
                .first()
            )
            if not offer or offer["expires"] < time.time():
                fail(409, "Offer unavailable or expired.")
            if offer["owner"] == uid:
                fail(409, "Use a different demo session to test your merchant offer.")
            if body.offer_id in state.get("reward_claimed", []):
                fail(409, "This offer has already been used by this demo session.")
            if body.amount_minor < offer["minimum"] or body.amount_minor > state["available"]:
                fail(422, "Purchase must meet the offer minimum and fit your wallet balance.")
            if offer["remaining"] < offer["cashback"]:
                fail(409, "Offer reward budget is exhausted.")
            conn.execute(
                campaigns.update()
                .where(campaigns.c.id == body.offer_id)
                .values(remaining=offer["remaining"] - offer["cashback"])
            )
            state["available"] -= body.amount_minor
            state["cashback"] = state.get("cashback", 0) + offer["cashback"]
            state.setdefault("reward_claimed", []).append(body.offer_id)
            receipt = {
                "merchant": offer["merchant"],
                "purchase_minor": body.amount_minor,
                "cashback_minor": offer["cashback"],
                "ts": int(time.time()),
            }
            state.setdefault("reward_receipts", []).append(receipt)
            change(state)
            store.log(conn, uid, "rewards.purchase.posted", receipt)
            return record(conn, uid, full, fingerprint, receipt)

    @app.post("/api/v1/rewards/to-buffer")
    def redeem(body: Redeem, token: Token = None):
        with session(token, "rewards.redeem") as (conn, uid, state):
            full, fingerprint, old = prior(
                conn, uid, "reward.redeem", body.idempotency_key, body.model_dump()
            )
            if old is not None:
                return old
            amount = state.get("cashback", 0)
            if amount <= 0:
                fail(409, "No cashback is available.")
            state["cashback"] = 0
            state["buffer"] += amount
            state["saved"] += amount
            change(state)
            result = {"amount_minor": amount, "buffer_minor": state["buffer"]}
            store.log(conn, uid, "rewards.buffer.posted", result)
            return record(conn, uid, full, fingerprint, result)
