"""Configuration, scenario mathematics, and currency-independent explanations."""

import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest
from app.config import Market, Rules
from app.engine.buffer import REASON_CODES, recommend
from app.engine.explain import explain, format_money
from app.engine.shock import shock_coverage
from app.engine.types import Balances, EssentialPlan
from pydantic import ValidationError


def test_scenario_boundaries_and_rounding(config):
    _, rules = config
    ladder = tuple(rate.fraction for rate in rules.shock_ladder)
    coverage = shock_coverage(50, 100, ladder)
    assert coverage.covered == 2
    assert [item.amount_minor for item in coverage.scenarios] == [25, 50, 100]
    assert shock_coverage(25, 101, ladder).covered == 0
    assert shock_coverage(26, 101, ladder).covered == 1
    assert not shock_coverage(100, 0, ladder).available
    assert shock_coverage(100, 0, ladder).covered is None


@pytest.mark.parametrize("balance,monthly", [(-1, 100), (1, -1), (1.1, 100), (True, 100)])
def test_invalid_scenario_amounts(balance, monthly):
    with pytest.raises(ValueError):
        shock_coverage(balance, monthly, (Fraction(1, 4),))


@pytest.mark.parametrize(
    "change",
    [
        {"rounding_step_minor": 0},
        {"min_transfer_minor": 2001},
        {"currency": "php"},
        {"languages": ()},
        {"default_language": "fil"},
        {"minor_unit_exponent": 1.5},
        {"unrecognised": 1},
    ],
)
def test_rejects_invalid_market(config, change):
    with pytest.raises(ValidationError):
        Market.model_validate({**config[0].model_dump(), **change})


@pytest.mark.parametrize(
    "change",
    [
        {"stages_days": [7, 7, 90]},
        {"stages_days": [14, 7]},
        {"stages_days": []},
        {"reserve_margin": {"numerator": 9, "denominator": 10}},
        {"max_pct_of_income_event": {"numerator": 2, "denominator": 1}},
        {"capture_rate_low": {"numerator": 1, "denominator": 0}},
    ],
)
def test_rejects_invalid_rules(config, change):
    with pytest.raises(ValidationError):
        Rules.model_validate({**config[1].model_dump(), **change})


@pytest.mark.parametrize("amount", [-1, 1.2, True, "100"])
def test_balance_requires_nonnegative_integer(amount):
    with pytest.raises(ValidationError):
        Balances(currency="PHP", available_minor=amount, buffer_minor=0)


def test_duplicate_bills_and_mixed_currency_rejected(golden):
    plan = golden[3]
    with pytest.raises(ValidationError):
        EssentialPlan.model_validate({**dict(plan), "obligations": plan.obligations * 2})
    with pytest.raises(ValidationError):
        EssentialPlan.model_validate({**dict(plan), "currency": "USD"})


def test_templates_cover_every_reason_without_placeholders(golden, config):
    market, rules = config
    rec = recommend(*golden, rules, market)
    language_dir = Path(__file__).resolve().parents[2] / "web/src/i18n"
    for language in market.languages:
        templates = json.loads((language_dir / f"reasons.{language}.json").read_text())
        assert set(REASON_CODES) <= templates.keys()
        for code in REASON_CODES:
            lines = explain(replace(rec, reason_codes=(code,)), market, language, templates)
            assert 0 < len(lines) <= 3
            assert "{" not in lines[0] and "}" not in lines[0]
    assert "PHP 120.00" in explain(rec, market, "en", templates)[0]


def test_currency_formatting_uses_exponent(config):
    market = config[0]
    assert format_money(12000, market) == "PHP 120.00"
    assert format_money(-5, market) == "PHP -0.05"
    zero_exponent = Market.model_validate(
        {**market.model_dump(), "currency": "VND", "minor_unit_exponent": 0}
    )
    assert format_money(12000, zero_exponent) == "VND 12,000"
