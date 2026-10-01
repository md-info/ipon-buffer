"""Pure savings suggestions. These are estimates, not affordability guarantees."""

from dataclasses import dataclass
from datetime import date, timedelta
from fractions import Fraction
from math import ceil, floor

from app.config import Market, Rules
from app.engine.features import Features
from app.engine.guardrails import GuardrailResult, apply_guardrails
from app.engine.obligations import due_amount
from app.engine.types import Balances, EssentialPlan, IncomeSelection

REASON_CODES = (
    "INSUFFICIENT_HISTORY",
    "PLAN_REQUIRED",
    "ESSENTIALS_UNKNOWN",
    "INCOME_DATE_PASSED",
    "OVERDUE_BILL_REVIEW",
    "TRANSFER_RECOMMENDED",
    "TARGET_REACHED",
    "EVENT_CAP_REACHED",
    "NOT_ENOUGH_SAFE_SURPLUS",
    "HIGH_VOLATILITY_SMALLER_STEPS",
    "GUARDRAIL_FAILED",
)


@dataclass(frozen=True)
class Stage:
    days: int
    target_minor: int
    reached: bool


@dataclass(frozen=True)
class Recommendation:
    currency: str
    as_of: date
    income_event_id: str
    amount_minor: int
    horizon_days: int
    protected_through: date
    daily_routine_minor: int
    monthly_essentials_minor: int
    protected_essentials_minor: int
    reserve_minor: int
    shortfall_minor: int
    estimated_surplus_minor: int
    estimated_room_per_day_minor: int | None
    remaining_event_cap_minor: int
    stage: Stage | None
    buffer_days: Fraction | None
    eta_days: int | None
    volatility_class: str
    reason_codes: tuple[str, ...]
    guardrail_results: tuple[GuardrailResult, ...]


def current_stage(buffer: int, daily_essentials: int, stages: tuple[int, ...]) -> Stage | None:
    if type(buffer) is not int or type(daily_essentials) is not int:
        raise ValueError("Stage amounts must be integer minor units")
    if buffer < 0 or daily_essentials < 0 or not stages:
        raise ValueError("Invalid stage inputs")
    if daily_essentials == 0:
        return None
    for days in stages:
        if days * daily_essentials > buffer:
            return Stage(days, days * daily_essentials, False)
    return Stage(stages[-1], stages[-1] * daily_essentials, True)


def estimate_eta(remaining: int, net_additions_30d: int, observation_days: int) -> int | None:
    if any(type(n) is not int for n in (remaining, net_additions_30d, observation_days)):
        raise ValueError("ETA requires integer observations")
    if remaining < 0 or observation_days < 0:
        raise ValueError("Invalid ETA input")
    if remaining == 0:
        return None  # UI displays target reached instead.
    if observation_days < 30 or net_additions_30d <= 0:
        return None
    return ceil(Fraction(remaining * 30, net_additions_30d))


def recommend(
    features: Features,
    balances: Balances,
    selection: IncomeSelection,
    plan: EssentialPlan,
    rules: Rules,
    market: Market,
) -> Recommendation:
    if any(
        code != market.currency for code in (features.currency, balances.currency, plan.currency)
    ):
        raise ValueError("Mixed currencies")
    event = next((txn for txn in features.income_events if txn.id == selection.event_id), None)
    if event is None:
        raise ValueError("Selected income event must exist in the observed window")
    if selection.already_saved_minor > event.amount_minor:
        raise ValueError("Event allocation exceeds the income event")
    volatility = (
        "unknown"
        if features.income_cv is None
        else (
            "high" if Fraction(features.income_cv) > rules.volatility_threshold.fraction else "low"
        )
    )
    gap = features.p75_income_gap_days if volatility == "high" else features.median_income_gap_days
    horizon = max(1, ceil(gap) if gap is not None else 1)
    if plan.next_expected_income is not None:
        horizon = max(horizon, (plan.next_expected_income - features.as_of).days)
    if plan.extended_horizon_days is not None:
        horizon = max(horizon, plan.extended_horizon_days)
    if horizon > 366:
        raise ValueError("Review expected income: planning horizon must not exceed 366 days")
    through = features.as_of + timedelta(days=horizon)
    routine = (
        features.routine_daily_minor
        if plan.routine_daily_minor is None
        else plan.routine_daily_minor
    )
    recurring = sum(
        bill.amount_minor
        for bill in plan.obligations
        if bill.recurrence == "monthly" and not bill.included_in_daily
    )
    monthly = routine * 30 + recurring
    due = sum(due_amount(bill, features.as_of, through) for bill in plan.obligations)
    protected = routine * horizon + due
    reserve = ceil(protected * rules.reserve_margin.fraction)
    surplus = max(0, balances.available_minor - reserve)
    stage = current_stage(balances.buffer_minor, ceil(Fraction(monthly, 30)), rules.stages_days)
    target = stage.target_minor if stage else 0
    remaining = max(0, target - balances.buffer_minor)
    remaining_cap = max(
        0,
        floor(event.amount_minor * rules.max_pct_of_income_event.fraction)
        - selection.already_saved_minor,
    )
    blockers: list[str] = []
    if features.insufficient_history:
        blockers.append("INSUFFICIENT_HISTORY")
    if not plan.confirmed:
        blockers.append("PLAN_REQUIRED")
    if monthly <= 0:
        blockers.append("ESSENTIALS_UNKNOWN")
    if plan.next_expected_income is not None and plan.next_expected_income < features.as_of:
        blockers.append("INCOME_DATE_PASSED")
    if any(not bill.paid and bill.due_date < features.as_of for bill in plan.obligations):
        blockers.append("OVERDUE_BILL_REVIEW")
    capture = rules.capture_rate_high if volatility == "high" else rules.capture_rate_low
    raw = min(floor(surplus * capture.fraction), remaining_cap, remaining)
    amount = (raw // market.rounding_step_minor) * market.rounding_step_minor
    if amount < market.min_transfer_minor or blockers:
        amount = 0
    amount, checks = apply_guardrails(
        amount,
        available=balances.available_minor,
        reserve=reserve,
        remaining_cap=remaining_cap,
        buffer=balances.buffer_minor,
        target=target,
        eligible=not blockers,
        step=market.rounding_step_minor,
        minimum=market.min_transfer_minor,
    )
    reasons = list(blockers)
    if not all(check.passed for check in checks):
        reasons.append("GUARDRAIL_FAILED")
    elif not blockers:
        if amount:
            reasons.append("TRANSFER_RECOMMENDED")
            if volatility == "high":
                reasons.append("HIGH_VOLATILITY_SMALLER_STEPS")
        elif stage and stage.reached:
            reasons.append("TARGET_REACHED")
        elif remaining_cap == 0:
            reasons.append("EVENT_CAP_REACHED")
        else:
            reasons.append("NOT_ENOUGH_SAFE_SURPLUS")
    room = None if blockers else max(0, balances.available_minor - reserve - amount) // horizon
    return Recommendation(
        currency=market.currency,
        as_of=features.as_of,
        income_event_id=event.id,
        amount_minor=amount,
        horizon_days=horizon,
        protected_through=through,
        daily_routine_minor=routine,
        monthly_essentials_minor=monthly,
        protected_essentials_minor=protected,
        reserve_minor=reserve,
        shortfall_minor=max(0, reserve - balances.available_minor),
        estimated_surplus_minor=surplus,
        estimated_room_per_day_minor=room,
        remaining_event_cap_minor=remaining_cap,
        stage=stage,
        buffer_days=Fraction(balances.buffer_minor * 30, monthly) if monthly else None,
        eta_days=(
            estimate_eta(
                remaining, features.buffer_net_additions_30d_minor, features.buffer_observation_days
            )
            if not blockers
            else None
        ),
        volatility_class=volatility,
        reason_codes=tuple(reasons),
        guardrail_results=checks,
    )
