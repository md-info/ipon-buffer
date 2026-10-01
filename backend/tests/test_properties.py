"""Hypothesis explores financial bounds across illustrative currency configurations."""

from datetime import timedelta

from app.config import Market, load_config
from app.engine.buffer import recommend
from app.engine.features import compute_features
from app.engine.types import Balances, EssentialPlan, IncomeSelection, Obligation, Txn
from app.sandbox.personas import AS_OF
from hypothesis import given, settings
from hypothesis import strategies as st


@settings(max_examples=300, derandomize=True, deadline=None)
@given(
    available=st.integers(0, 10**9),
    buffer=st.integers(0, 10**9),
    income=st.integers(1, 10**8),
    daily=st.integers(0, 10**6),
    bill=st.integers(1, 10**7),
    gap=st.integers(1, 20),
    saved_pct=st.integers(0, 100),
    confirmed=st.booleans(),
    currency_case=st.sampled_from(
        [("PH", "PHP", 2, 500, 2000), ("ID", "IDR", 0, 1000, 1000), ("VN", "VND", 0, 100, 500)]
    ),
)
def test_recommendation_invariants(
    available, buffer, income, daily, bill, gap, saved_pct, confirmed, currency_case
):
    """ID/VN cases test arithmetic only; not market-ready configurations."""
    code, currency, exponent, step, minimum = currency_case
    market = Market(
        market_code=code,
        currency=currency,
        minor_unit_exponent=exponent,
        rounding_step_minor=step,
        min_transfer_minor=minimum,
        languages=("en",),
        default_language="en",
    )
    _, rules = load_config()
    incomes = tuple(
        Txn(
            id=str(i),
            date=AS_OF - timedelta(days=i * gap),
            amount_minor=income,
            currency=currency,
            kind="income",
        )
        for i in range(3)
    )
    features = compute_features(
        incomes, coverage_start=AS_OF - timedelta(days=60), as_of=AS_OF, currency=currency
    )
    balances = Balances(currency=currency, available_minor=available, buffer_minor=buffer)
    selection = IncomeSelection(event_id="0", already_saved_minor=income * saved_pct // 100)
    plan = EssentialPlan(
        currency=currency,
        confirmed=confirmed,
        routine_daily_minor=daily,
        obligations=(Obligation(id="b", amount_minor=bill, currency=currency, due_date=AS_OF),),
    )
    rec = recommend(features, balances, selection, plan, rules, market)
    assert rec == recommend(features, balances, selection, plan, rules, market)
    assert type(rec.amount_minor) is int
    assert rec.amount_minor >= 0
    assert rec.amount_minor <= income // 5
    assert all(check.passed for check in rec.guardrail_results)
    if rec.amount_minor > 0:
        assert rec.amount_minor % step == 0
        assert rec.amount_minor >= minimum
        assert available - rec.amount_minor >= rec.reserve_minor
        assert rec.amount_minor + selection.already_saved_minor <= income // 5
        assert buffer + rec.amount_minor <= rec.stage.target_minor
        assert confirmed and daily > 0
        # A deposit only changes accounts, never total funds.
        assert (available - rec.amount_minor) + (buffer + rec.amount_minor) == available + buffer
    if not confirmed or daily == 0:
        assert rec.amount_minor == 0
        assert rec.estimated_room_per_day_minor is None
