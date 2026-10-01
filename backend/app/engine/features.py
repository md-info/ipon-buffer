"""Pure, trailing-window features. No I/O, real-time clock, or future observations."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, localcontext
from fractions import Fraction
from math import ceil

from app.engine.types import Txn


@dataclass(frozen=True)
class Features:
    as_of: date
    currency: str
    coverage_days: int
    window_start: date
    income_event_count: int
    distinct_income_dates: int
    completed_gap_count: int
    routine_expense_count: int
    routine_daily_minor: int
    median_income_gap_days: Fraction | None
    p75_income_gap_days: int | None
    income_cv: Decimal | None
    insufficient_history: bool
    income_events: tuple[Txn, ...]
    buffer_net_additions_30d_minor: int
    buffer_observation_days: int


def compute_features(
    txns: tuple[Txn, ...],
    *,
    coverage_start: date,
    as_of: date,
    currency: str,
) -> Features:
    if type(coverage_start) is not date or type(as_of) is not date or coverage_start > as_of:
        raise ValueError("Coverage start/as_of must be calendar dates in order")
    if len(currency) != 3 or not currency.isascii() or not currency.isupper():
        raise ValueError("Currency must be a three-letter ISO-style code")
    if len({txn.id for txn in txns}) != len(txns):
        raise ValueError("Duplicate transaction IDs")
    for txn in txns:
        if txn.currency != currency:
            raise ValueError("Mixed transaction currencies")
        if txn.date > as_of or txn.date < coverage_start:
            raise ValueError("Transaction outside the declared observation coverage")
    start = max(coverage_start, as_of - timedelta(days=89))
    days = (as_of - start).days + 1
    window = tuple(txn for txn in txns if start <= txn.date <= as_of)
    incomes = tuple(
        sorted(
            (txn for txn in window if txn.kind == "income"),
            key=lambda txn: (txn.date, txn.id),
        )
    )
    dates = sorted({txn.date for txn in incomes})
    gaps = sorted((right - left).days for left, right in zip(dates, dates[1:], strict=False))
    median_gap = None
    p75_gap = None
    if gaps:
        middle = len(gaps) // 2
        median_gap = (
            Fraction(gaps[middle])
            if len(gaps) % 2
            else Fraction(gaps[middle - 1] + gaps[middle], 2)
        )
        p75_gap = gaps[ceil(Fraction(3 * len(gaps), 4)) - 1]
    cv = None
    if len(incomes) >= 2:
        with localcontext() as context:
            context.prec = 40
            amounts = [Decimal(txn.amount_minor) for txn in incomes]
            mean = sum(amounts) / len(amounts)
            variance = sum((value - mean) ** 2 for value in amounts) / len(amounts)
            cv = variance.sqrt() / mean
    routine = [txn for txn in window if txn.kind == "routine_essential"]
    daily = ceil(Fraction(-sum(txn.amount_minor for txn in routine), days))
    recent = [txn for txn in window if txn.date >= as_of - timedelta(days=29)]
    net = -sum(
        txn.amount_minor
        for txn in recent
        if txn.kind in {"transfer_in_buffer", "transfer_out_buffer"}
    )
    return Features(
        as_of=as_of,
        currency=currency,
        coverage_days=days,
        window_start=start,
        income_event_count=len(incomes),
        distinct_income_dates=len(dates),
        completed_gap_count=len(gaps),
        routine_expense_count=len(routine),
        routine_daily_minor=daily,
        median_income_gap_days=median_gap,
        p75_income_gap_days=p75_gap,
        income_cv=cv,
        insufficient_history=days < 30 or len(dates) < 3,
        income_events=incomes,
        buffer_net_additions_30d_minor=net,
        buffer_observation_days=min(30, days),
    )
