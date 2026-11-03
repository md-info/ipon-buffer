"""Synthetic community module. Wallet-scoped session identity; no transfer access."""

import base64
import json
import time
import uuid
from typing import Annotated, Literal

from fastapi import Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import Column, MetaData, String, Table, Text, select

meta = MetaData()
reports = Table(
    "nearby_reports",
    meta,
    Column("id", String, primary_key=True),
    Column("owner", String),
    Column("body", Text),
)
reactions = Table(
    "nearby_reactions",
    meta,
    Column("id", String, primary_key=True),
    Column("report", String),
    Column("actor", String),
    Column("kind", String),
)
Token = Annotated[str | None, Header(alias="X-Demo-Session")]


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item: str = Field(min_length=2, max_length=100)
    quantity: str = Field(min_length=1, max_length=60)
    store: str = Field(min_length=2, max_length=100)
    area: Literal["Demo Central", "Demo Riverside"]
    price_minor: int = Field(strict=True, gt=0, le=100000000)
    observed_at: int
    conditions: str = Field(max_length=200, default="")
    photo: str = Field(max_length=450000, default="")

    @field_validator("item", "quantity", "store")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("A value is required")
        return value.strip()

    @field_validator("observed_at")
    @classmethod
    def recent(cls, value):
        if not time.time() - 7 * 86400 <= value <= time.time() + 60:
            raise ValueError("Observation must be within the last seven days")
        return value

    @field_validator("photo")
    @classmethod
    def image(cls, value):
        if not value:
            return value
        prefix = "data:image/jpeg;base64,"
        if not value.startswith(prefix):
            raise ValueError("Use a JPEG photo")
        try:
            raw = base64.b64decode(value[len(prefix) :], validate=True)
        except Exception as error:
            raise ValueError("Invalid photo") from error
        if not raw.startswith(b"\xff\xd8\xff") or len(raw) > 330000:
            raise ValueError("Invalid or oversized JPEG")
        return value


class Reaction(BaseModel):
    kind: Literal["helpful", "confirmed", "changed", "flagged"]


def install_nearby(app, store, session):
    meta.create_all(store.engine)

    @app.get("/api/v1/nearby")
    def feed(token: Token = None):
        with session(token, "nearby.read") as (conn, uid, _):
            events = list(conn.execute(select(reactions)).mappings())
            rows = list(conn.execute(select(reports)).mappings())
            result = []
            points = 0
            for row in rows:
                body = json.loads(row["body"])
                counts = {
                    k: sum(e["report"] == row["id"] and e["kind"] == k for e in events)
                    for k in ["helpful", "confirmed", "changed", "flagged"]
                }
                if row["owner"] == uid and not counts["flagged"]:
                    points += min(3, counts["confirmed"]) * 5
                # Reports flagged for review are hidden from other demo users.
                if counts["flagged"] and row["owner"] != uid:
                    continue
                result.append(
                    {
                        **body,
                        "id": row["id"],
                        "mine": row["owner"] == uid,
                        "counts": counts,
                        "review_pending": bool(counts["flagged"]),
                        "stale": time.time() - body["observed_at"] > 86400,
                        "my_reactions": [
                            e["kind"]
                            for e in events
                            if e["actor"] == uid and e["report"] == row["id"]
                        ],
                    }
                )
            return {
                "reports": sorted(result, key=lambda r: r["observed_at"], reverse=True),
                "points": points,
                "identity": "Synthetic neighbor " + uid[:5],
            }

    @app.post("/api/v1/nearby")
    def publish(body: Report, token: Token = None):
        with session(token, "nearby.publish") as (conn, uid, _):
            own = list(conn.execute(select(reports).where(reports.c.owner == uid)).mappings())
            if len(own) >= 20:
                raise HTTPException(429, {"message": "Demo limit: 20 reports per identity."})
            report_id = uuid.uuid4().hex
            conn.execute(
                reports.insert().values(id=report_id, owner=uid, body=body.model_dump_json())
            )
            return {"id": report_id}

    @app.post("/api/v1/nearby/{report_id}/react")
    def react(report_id: str, body: Reaction, token: Token = None):
        with session(token, "nearby.react") as (conn, uid, _):
            row = conn.execute(select(reports).where(reports.c.id == report_id)).mappings().first()
            if not row:
                raise HTTPException(404, {"message": "Report not found"})
            if row["owner"] == uid:
                raise HTTPException(409, {"message": "You cannot react to your own report."})
            flagged = conn.execute(
                select(reactions.c.id).where(
                    reactions.c.report == report_id, reactions.c.kind == "flagged"
                )
            ).first()
            if flagged and body.kind != "flagged":
                raise HTTPException(409, {"message": "Report is pending review."})
            data = json.loads(row["body"])
            if body.kind == "confirmed" and time.time() - data["observed_at"] > 86400:
                raise HTTPException(409, {"message": "Report is old. Publish a fresh observation."})
            # Same-price and changed-price are mutually exclusive observations.
            other = "changed" if body.kind == "confirmed" else "confirmed"
            if body.kind in {"confirmed", "changed"}:
                conn.execute(
                    reactions.delete().where(
                        reactions.c.report == report_id,
                        reactions.c.actor == uid,
                        reactions.c.kind == other,
                    )
                )
            key = f"{report_id}:{uid}:{body.kind}"
            if not conn.execute(select(reactions.c.id).where(reactions.c.id == key)).first():
                conn.execute(
                    reactions.insert().values(id=key, report=report_id, actor=uid, kind=body.kind)
                )
            return {"recorded": True}

    @app.delete("/api/v1/nearby/{report_id}")
    def remove(report_id: str, token: Token = None):
        with session(token, "nearby.delete") as (conn, uid, _):
            row = conn.execute(select(reports).where(reports.c.id == report_id)).mappings().first()
            if not row or row["owner"] != uid:
                raise HTTPException(404, {"message": "Your report was not found"})
            conn.execute(reactions.delete().where(reactions.c.report == report_id))
            conn.execute(reports.delete().where(reports.c.id == report_id))
            return {"deleted": True}


def erase_nearby(conn, uid):
    owned = select(reports.c.id).where(reports.c.owner == uid)
    conn.execute(reactions.delete().where(reactions.c.report.in_(owned)))
    conn.execute(reactions.delete().where(reactions.c.actor == uid))
    conn.execute(reports.delete().where(reports.c.owner == uid))
