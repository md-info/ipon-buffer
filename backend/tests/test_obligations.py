"""Monthly bills recur in long planning horizons, including month-end clamping."""

from datetime import date, timedelta

import pytest
from app.engine.buffer import recommend
from app.engine.obligations import due_amount
from app.engine.types import EssentialPlan, Obligation


@pytest.mark.parametrize("paid,expected", [(False, 3000), (True, 2000)])
def test_month_end_recurrence(paid, expected):
    bill = Obligation(
        id="rent",
        amount_minor=1000,
        currency="PHP",
        due_date=date(2026, 1, 31),
        recurrence="monthly",
        paid=paid,
    )
    assert due_amount(bill, date(2026, 1, 1), date(2026, 3, 31)) == expected
    assert due_amount(bill, date(2026, 3, 1), date(2026, 3, 30)) == 0
    assert due_amount(bill, date(2026, 2, 1), date(2026, 2, 28)) == 1000


def test_year_boundary_and_leap_day():
    bill = Obligation(
        id="rent",
        amount_minor=1000,
        currency="PHP",
        due_date=date(2023, 12, 31),
        recurrence="monthly",
    )
    assert due_amount(bill, date(2024, 1, 1), date(2024, 2, 28)) == 1000
    assert due_amount(bill, date(2024, 1, 1), date(2024, 2, 29)) == 2000


def test_recommendation_reserves_multiple_occurrences(golden, config):
    features, balances, selection, plan = golden
    bill = Obligation(
        id="monthly",
        amount_minor=60_000,
        currency="PHP",
        due_date=features.as_of,
        recurrence="monthly",
    )
    plan = EssentialPlan.model_validate(
        {**dict(plan), "extended_horizon_days": 40, "obligations": (bill,)}
    )
    rec = recommend(features, balances, selection, plan, config[1], config[0])
    assert rec.protected_essentials_minor == 40 * 25_000 + 2 * 60_000


def test_rejects_unbounded_expected_income(golden, config):
    features, balances, selection, plan = golden
    plan = EssentialPlan.model_validate(
        {**dict(plan), "next_expected_income": features.as_of + timedelta(days=367)}
    )
    with pytest.raises(ValueError, match="366"):
        recommend(features, balances, selection, plan, config[1], config[0])
