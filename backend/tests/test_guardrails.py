"""Every safety predicate is exercised with a pass and a fail."""

import pytest
from app.engine.guardrails import (
    apply_guardrails,
    income_cap,
    no_shortfall,
    not_above_target,
    rounding_and_minimum,
    usable_plan,
)


@pytest.mark.parametrize(
    "predicate,passing,failing",
    [
        (no_shortfall, (100, 200, 100), (101, 200, 100)),
        (income_cap, (100, 100), (101, 100)),
        (not_above_target, (100, 200, 300), (101, 200, 300)),
        (usable_plan, (100, True), (100, False)),
        (rounding_and_minimum, (2000, 500, 2000), (1999, 500, 2000)),
        (rounding_and_minimum, (2000, 500, 2000), (2001, 500, 2000)),
    ],
)
def test_predicate(predicate, passing, failing):
    assert predicate(*passing).passed
    assert not predicate(*failing).passed


def test_apply_guardrails_blocks_and_preserves_failure_evidence():
    amount, checks = apply_guardrails(
        2500,
        available=3000,
        reserve=2000,
        remaining_cap=4000,
        buffer=0,
        target=9000,
        eligible=True,
        step=500,
        minimum=2000,
    )
    assert amount == 0
    assert not next(check for check in checks if check.name == "no_shortfall").passed


def test_zero_valid_despite_existing_shortfall_and_excess_buffer():
    amount, checks = apply_guardrails(
        0,
        available=1,
        reserve=100,
        remaining_cap=0,
        buffer=900,
        target=100,
        eligible=False,
        step=500,
        minimum=2000,
    )
    assert amount == 0
    assert all(check.passed for check in checks)
