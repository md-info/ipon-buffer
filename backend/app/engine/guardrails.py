"""Pure final checks; zero transfers remain valid even in existing shortfalls."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    name: str
    passed: bool
    detail: str


def no_shortfall(amount: int, available: int, reserve: int) -> GuardrailResult:
    return GuardrailResult(
        "no_shortfall",
        amount == 0 or available - amount >= reserve,
        "Positive deposits leave the estimated reserve available.",
    )


def income_cap(amount: int, remaining_cap: int) -> GuardrailResult:
    return GuardrailResult(
        "income_cap",
        amount <= remaining_cap,
        "Deposit stays within this income event's remaining cap.",
    )


def not_above_target(amount: int, buffer: int, target: int) -> GuardrailResult:
    return GuardrailResult(
        "not_above_target",
        amount == 0 or buffer + amount <= target,
        "Positive deposits do not exceed the next target.",
    )


def usable_plan(amount: int, eligible: bool) -> GuardrailResult:
    return GuardrailResult(
        "usable_plan",
        amount == 0 or eligible,
        "Positive deposits require usable history and a confirmed plan.",
    )


def rounding_and_minimum(amount: int, step: int, minimum: int) -> GuardrailResult:
    return GuardrailResult(
        "rounding_and_minimum",
        amount == 0 or (amount >= minimum and amount % step == 0),
        "Deposit meets the configured minimum and rounding step.",
    )


def apply_guardrails(
    amount: int,
    *,
    available: int,
    reserve: int,
    remaining_cap: int,
    buffer: int,
    target: int,
    eligible: bool,
    step: int,
    minimum: int,
) -> tuple[int, tuple[GuardrailResult, ...]]:
    checks = (
        GuardrailResult("nonnegative", amount >= 0, "Deposit is nonnegative."),
        no_shortfall(amount, available, reserve),
        income_cap(amount, remaining_cap),
        not_above_target(amount, buffer, target),
        usable_plan(amount, eligible),
        rounding_and_minimum(amount, step, minimum),
    )
    return (amount if all(check.passed for check in checks) else 0), checks
