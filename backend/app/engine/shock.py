"""Illustrative scenario amounts, not estimates of typical emergencies."""

from dataclasses import dataclass
from fractions import Fraction
from math import ceil


@dataclass(frozen=True)
class Scenario:
    multiple: Fraction
    amount_minor: int
    covered: bool


@dataclass(frozen=True)
class ShockCoverage:
    available: bool
    covered: int | None
    total: int
    scenarios: tuple[Scenario, ...]


def shock_coverage(
    buffer_minor: int,
    monthly_essentials_minor: int,
    ladder: tuple[Fraction, ...],
) -> ShockCoverage:
    if any(type(n) is not int or n < 0 for n in (buffer_minor, monthly_essentials_minor)):
        raise ValueError("Scenario balances must be nonnegative integer minor units")
    if not ladder or any(multiple <= 0 for multiple in ladder):
        raise ValueError("Scenario multipliers must be positive")
    if monthly_essentials_minor == 0:
        return ShockCoverage(False, None, len(ladder), ())
    scenarios = tuple(
        Scenario(
            multiple,
            ceil(monthly_essentials_minor * multiple),
            buffer_minor >= ceil(monthly_essentials_minor * multiple),
        )
        for multiple in ladder
    )
    return ShockCoverage(True, sum(item.covered for item in scenarios), len(ladder), scenarios)
