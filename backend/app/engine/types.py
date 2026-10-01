"""Validated immutable inputs. Monetary values are always integer minor units."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

MAX_MONEY = 9_000_000_000_000_000
Money = Annotated[int, Field(strict=True, ge=0, le=MAX_MONEY)]
PositiveMoney = Annotated[int, Field(strict=True, gt=0, le=MAX_MONEY)]
SignedMoney = Annotated[int, Field(strict=True, ge=-MAX_MONEY, le=MAX_MONEY)]
Day = Annotated[date, Field(strict=True)]
Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Txn(FrozenModel):
    id: Identifier
    date: Day
    amount_minor: SignedMoney
    currency: Currency
    kind: Literal[
        "income",
        "routine_essential",
        "scheduled_bill",
        "discretionary",
        "transfer_in_buffer",
        "transfer_out_buffer",
    ]

    @model_validator(mode="after")
    def valid_sign(self):
        positive = self.kind in {"income", "transfer_out_buffer"}
        if (positive and self.amount_minor <= 0) or (not positive and self.amount_minor >= 0):
            raise ValueError("Income/withdrawal must be positive; spending/deposit negative")
        return self


class Obligation(FrozenModel):
    """One due occurrence; monthly recurrence contributes once to stage estimates."""

    id: Identifier
    amount_minor: PositiveMoney
    currency: Currency
    due_date: Day
    paid: StrictBool = False
    included_in_daily: StrictBool = False
    recurrence: Literal["one_off", "monthly"] = "one_off"


class EssentialPlan(FrozenModel):
    currency: Currency
    confirmed: StrictBool = False
    routine_daily_minor: Money | None = None
    next_expected_income: Day | None = None
    extended_horizon_days: Annotated[int, Field(strict=True, ge=1, le=366)] | None = None
    obligations: tuple[Obligation, ...] = ()

    @model_validator(mode="after")
    def consistent_obligations(self):
        ids = [bill.id for bill in self.obligations]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate obligation IDs would double-count expenses")
        if any(bill.currency != self.currency for bill in self.obligations):
            raise ValueError("Mixed plan currencies")
        return self


class Balances(FrozenModel):
    currency: Currency
    available_minor: Money
    buffer_minor: Money


class IncomeSelection(FrozenModel):
    event_id: Identifier
    already_saved_minor: Money = 0
