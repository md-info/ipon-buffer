"""Independent worked examples and edge cases for proposed deposits."""

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from fractions import Fraction

import pytest
from app.engine.buffer import current_stage, estimate_eta, recommend
from app.engine.types import Balances, EssentialPlan, IncomeSelection, Obligation


def calculate(golden, config, **changes):
    features, balances, selection, plan = golden
    market, rules = config
    return recommend(
        changes.get("features", features),
        changes.get("balances", balances),
        changes.get("selection", selection),
        changes.get("plan", plan),
        rules,
        market,
    )


def plan_with(plan, **changes):
    return EssentialPlan.model_validate({**dict(plan), **changes})


def test_golden_120_pesos(golden, config):
    rec = calculate(golden, config)
    assert rec.horizon_days == 4
    assert rec.protected_essentials_minor == 160_000
    assert rec.reserve_minor == 176_000
    assert rec.estimated_surplus_minor == 24_000
    assert rec.amount_minor == 12_000
    assert rec.estimated_room_per_day_minor == 3000
    assert rec.stage.days == 7
    assert rec.stage.target_minor == 175_000
    assert rec.buffer_days == Fraction(2)
    assert rec.reason_codes == ("TRANSFER_RECOMMENDED",)
    assert all(check.passed for check in rec.guardrail_results)
    assert rec.eta_days is None


def test_omitted_300_peso_bill_causes_zero(golden, config):
    features, _, _, plan = golden
    school = Obligation(
        id="school",
        amount_minor=30_000,
        currency="PHP",
        due_date=features.as_of + timedelta(days=1),
    )
    rec = calculate(golden, config, plan=plan_with(plan, obligations=(*plan.obligations, school)))
    assert rec.reserve_minor == 209_000
    assert rec.shortfall_minor == 9000
    assert rec.amount_minor == 0
    assert rec.estimated_room_per_day_minor == 0
    assert rec.reason_codes == ("NOT_ENOUGH_SAFE_SURPLUS",)
    assert all(check.passed for check in rec.guardrail_results)


@pytest.mark.parametrize("offset,expected", [(0, 176_000), (4, 176_000), (5, 110_000)])
def test_bill_due_date_boundaries(golden, config, offset, expected):
    features, _, _, plan = golden
    bill = Obligation(
        id="edge",
        amount_minor=60_000,
        currency="PHP",
        due_date=features.as_of + timedelta(days=offset),
    )
    rec = calculate(golden, config, plan=plan_with(plan, obligations=(bill,)))
    assert rec.reserve_minor == expected


@pytest.mark.parametrize("field", ["paid", "included_in_daily"])
def test_paid_or_already_included_bill_not_counted_twice(golden, config, field):
    plan = golden[3]
    bill = Obligation.model_validate({**dict(plan.obligations[0]), field: True})
    rec = calculate(golden, config, plan=plan_with(plan, obligations=(bill,)))
    assert rec.reserve_minor == 110_000


def test_recurring_monthly_bill_in_stage_estimate(golden, config):
    plan = golden[3]
    bill = Obligation.model_validate({**dict(plan.obligations[0]), "recurrence": "monthly"})
    rec = calculate(golden, config, plan=plan_with(plan, obligations=(bill,)))
    assert rec.monthly_essentials_minor == 810_000
    assert rec.stage.target_minor == 189_000


@pytest.mark.parametrize(
    "blocker", ["history", "plan", "essentials", "late_income", "overdue_bill"]
)
def test_blockers_force_zero_and_hide_room(golden, config, blocker):
    features, _, _, plan = golden
    updates = {}
    expected = {
        "history": "INSUFFICIENT_HISTORY",
        "plan": "PLAN_REQUIRED",
        "essentials": "ESSENTIALS_UNKNOWN",
        "late_income": "INCOME_DATE_PASSED",
        "overdue_bill": "OVERDUE_BILL_REVIEW",
    }[blocker]
    if blocker == "history":
        updates["features"] = replace(features, insufficient_history=True)
    elif blocker == "plan":
        updates["plan"] = plan_with(plan, confirmed=False)
    elif blocker == "essentials":
        updates["plan"] = plan_with(plan, routine_daily_minor=0, obligations=())
    elif blocker == "late_income":
        updates["plan"] = plan_with(plan, next_expected_income=features.as_of - timedelta(days=1))
    else:
        bill = Obligation(
            id="overdue",
            amount_minor=100,
            currency="PHP",
            due_date=features.as_of - timedelta(days=1),
        )
        updates["plan"] = plan_with(plan, obligations=(bill,))
    rec = calculate(golden, config, **updates)
    assert rec.amount_minor == 0
    assert expected in rec.reason_codes
    assert rec.estimated_room_per_day_minor is None
    assert rec.eta_days is None


def test_high_volatility_uses_p75_and_smaller_capture(golden, config):
    features = replace(golden[0], income_cv=Decimal("0.6"), p75_income_gap_days=5)
    balances = Balances(currency="PHP", available_minor=400_000, buffer_minor=50_000)
    rec = calculate(golden, config, features=features, balances=balances)
    assert rec.horizon_days == 5
    assert rec.reserve_minor == 203_500
    assert rec.amount_minor == 20_000  # event cap binds
    assert "HIGH_VOLATILITY_SMALLER_STEPS" in rec.reason_codes


def test_volatility_threshold_is_inclusive_low(golden, config):
    rec = calculate(golden, config, features=replace(golden[0], income_cv=Decimal("0.5")))
    assert rec.volatility_class == "low"
    assert rec.amount_minor == 12_000


def test_partial_cap_and_rounding(golden, config):
    selection = IncomeSelection(event_id=golden[2].event_id, already_saved_minor=17_750)
    rec = calculate(golden, config, selection=selection)
    assert rec.remaining_event_cap_minor == 2250
    assert rec.amount_minor == 2000
    assert rec.estimated_room_per_day_minor == 5500
    selection = IncomeSelection(event_id=selection.event_id, already_saved_minor=18_001)
    assert calculate(golden, config, selection=selection).amount_minor == 0


def test_cap_used_up(golden, config):
    selection = IncomeSelection(event_id=golden[2].event_id, already_saved_minor=20_000)
    rec = calculate(golden, config, selection=selection)
    assert rec.amount_minor == 0
    assert rec.reason_codes == ("EVENT_CAP_REACHED",)


def test_existing_shortfall_and_above_target_are_valid_zero(golden, config):
    balances = Balances(currency="PHP", available_minor=1, buffer_minor=9_000_000)
    rec = calculate(golden, config, balances=balances)
    assert rec.amount_minor == 0
    assert rec.shortfall_minor == 175_999
    assert rec.stage.reached
    assert all(check.passed for check in rec.guardrail_results)


def test_current_stage_exact_boundary_and_final():
    assert current_stage(699, 100, (7, 14, 90)).days == 7
    assert current_stage(700, 100, (7, 14, 90)).days == 14
    assert current_stage(9000, 100, (7, 14, 90)).reached
    assert current_stage(0, 0, (7, 14, 90)) is None


def test_fractional_gap_rounds_up_and_user_can_extend(golden, config):
    features = replace(golden[0], median_income_gap_days=Fraction(9, 2))
    assert calculate(golden, config, features=features).horizon_days == 5
    plan = plan_with(golden[3], extended_horizon_days=7)
    assert calculate(golden, config, features=features, plan=plan).horizon_days == 7


@pytest.mark.parametrize(
    "remaining,net,observed,expected",
    [
        (100, 30, 30, 100),
        (101, 30, 30, 101),
        (101, 31, 30, 98),
        (100, 0, 30, None),
        (100, -1, 30, None),
        (100, 30, 29, None),
        (0, 30, 30, None),
    ],
)
def test_eta(remaining, net, observed, expected):
    assert estimate_eta(remaining, net, observed) == expected


def test_eta_uses_observed_net_additions(golden, config):
    features = replace(golden[0], buffer_net_additions_30d_minor=30_000)
    assert calculate(golden, config, features=features).eta_days == 125


def test_rejects_missing_or_nonincome_event(golden, config):
    for event_id in ("absent", "routine-60"):
        with pytest.raises(ValueError, match="income event"):
            calculate(golden, config, selection=IncomeSelection(event_id=event_id))


def test_rejects_currency_and_bad_allocation(golden, config):
    with pytest.raises(ValueError, match="currencies"):
        calculate(
            golden, config, balances=Balances(currency="USD", available_minor=1, buffer_minor=0)
        )
    with pytest.raises(ValueError, match="allocation"):
        calculate(
            golden,
            config,
            selection=IncomeSelection(event_id=golden[2].event_id, already_saved_minor=100_001),
        )
