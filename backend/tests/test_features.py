"""Hand-checked time windows, statistical definitions, and malformed inputs."""

from datetime import date, timedelta
from decimal import Decimal, localcontext
from fractions import Fraction

import pytest
from app.engine.features import compute_features
from app.engine.types import Txn
from pydantic import ValidationError

NOW = date(2026, 9, 28)


def transaction(id, days_ago, amount=10_000, kind="income", currency="PHP"):
    return Txn(
        id=id,
        date=NOW - timedelta(days=days_ago),
        amount_minor=amount,
        kind=kind,
        currency=currency,
    )


def test_hand_computed_features():
    txns = (
        transaction("a", 29, 100),
        transaction("b", 25, 300),
        transaction("c", 19, 100),
        transaction("d", 19, 300),
        transaction("expense", 0, -301, "routine_essential"),
        transaction("rent", 0, -9000, "scheduled_bill"),
    )
    result = compute_features(
        txns, coverage_start=NOW - timedelta(days=29), as_of=NOW, currency="PHP"
    )
    assert result.coverage_days == 30
    assert result.routine_daily_minor == 11  # ceil(301 / 30); excludes the separate bill.
    assert result.income_event_count == 4
    assert result.distinct_income_dates == 3
    assert result.completed_gap_count == 2
    assert result.median_income_gap_days == Fraction(5)
    assert result.p75_income_gap_days == 6
    assert result.income_cv == Decimal("0.5")  # population std 100 / mean 200
    assert not result.insufficient_history


def test_fractional_median_and_nearest_rank():
    result = compute_features(
        (transaction("a", 29), transaction("b", 25), transaction("c", 20)),
        coverage_start=NOW - timedelta(days=29),
        as_of=NOW,
        currency="PHP",
    )
    assert result.median_income_gap_days == Fraction(9, 2)
    assert result.p75_income_gap_days == 5


def test_trailing_90_days_and_30_day_net_additions():
    txns = (
        transaction("old", 90, -999_999, "routine_essential"),
        transaction("edge", 89, -900, "routine_essential"),
        transaction("deposit", 29, -10_000, "transfer_in_buffer"),
        transaction("excluded", 30, -80_000, "transfer_in_buffer"),
        transaction("withdrawal", 0, 3000, "transfer_out_buffer"),
    )
    result = compute_features(
        txns, coverage_start=NOW - timedelta(days=100), as_of=NOW, currency="PHP"
    )
    assert result.coverage_days == 90
    assert result.routine_daily_minor == 10
    assert result.buffer_net_additions_30d_minor == 7000
    assert result.buffer_observation_days == 30


def test_no_income_and_one_income_are_unknown():
    for txns in ((), (transaction("one", 0),)):
        result = compute_features(
            txns, coverage_start=NOW - timedelta(days=29), as_of=NOW, currency="PHP"
        )
        assert result.insufficient_history
        assert result.income_cv is None
        assert result.median_income_gap_days is None
        assert result.p75_income_gap_days is None


def test_same_day_incomes_do_not_create_history():
    result = compute_features(
        tuple(transaction(str(i), 0) for i in range(20)),
        coverage_start=NOW - timedelta(days=60),
        as_of=NOW,
        currency="PHP",
    )
    assert result.income_event_count == 20
    assert result.distinct_income_dates == 1
    assert result.completed_gap_count == 0
    assert result.insufficient_history


def test_decimal_context_does_not_change_features():
    txns = (transaction("a", 10, 123), transaction("b", 2, 379))
    with localcontext() as context:
        context.prec = 6
        first = compute_features(
            txns, coverage_start=NOW - timedelta(days=29), as_of=NOW, currency="PHP"
        )
        context.prec = 50
        second = compute_features(
            txns, coverage_start=NOW - timedelta(days=29), as_of=NOW, currency="PHP"
        )
    assert first == second


@pytest.mark.parametrize(
    "txns",
    [
        (transaction("future", -1),),
        (transaction("outside", 31),),
        (transaction("a", 0), transaction("a", 1)),
        (transaction("mixed", 0, currency="USD"),),
    ],
)
def test_rejects_invalid_history(txns):
    with pytest.raises(ValueError):
        compute_features(txns, coverage_start=NOW - timedelta(days=29), as_of=NOW, currency="PHP")


@pytest.mark.parametrize(
    "amount,kind",
    [
        (0, "income"),
        (-1, "income"),
        (1, "routine_essential"),
        (1, "transfer_in_buffer"),
        (-1, "transfer_out_buffer"),
        (1.5, "income"),
        (True, "income"),
        ("100", "income"),
    ],
)
def test_strict_amount_and_sign_validation(amount, kind):
    with pytest.raises(ValidationError):
        transaction("invalid", 0, amount, kind)


def test_invalid_coverage():
    with pytest.raises(ValueError):
        compute_features((), coverage_start=NOW + timedelta(days=1), as_of=NOW, currency="PHP")
