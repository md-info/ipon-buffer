"""Read config outside the engine. Rates use exact rational numbers."""

from fractions import Fraction
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import Field, model_validator

from app.engine.types import Currency, FrozenModel, PositiveMoney

PositiveInt = Annotated[int, Field(strict=True, gt=0)]


class Ratio(FrozenModel):
    numerator: Annotated[int, Field(strict=True, ge=0)]
    denominator: PositiveInt

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)


class Market(FrozenModel):
    market_code: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    currency: Currency
    minor_unit_exponent: Annotated[int, Field(strict=True, ge=0, le=4)]
    rounding_step_minor: PositiveMoney
    min_transfer_minor: PositiveMoney
    languages: tuple[str, ...]
    default_language: str

    @model_validator(mode="after")
    def valid_market(self):
        if not self.languages or self.default_language not in self.languages:
            raise ValueError("Default language must be in nonempty language list")
        if len(set(self.languages)) != len(self.languages):
            raise ValueError("Duplicate languages")
        if self.min_transfer_minor % self.rounding_step_minor:
            raise ValueError("Minimum transfer must be a rounding-step multiple")
        return self


class Rules(FrozenModel):
    capture_rate_low: Ratio
    capture_rate_high: Ratio
    max_pct_of_income_event: Ratio
    reserve_margin: Ratio
    volatility_threshold: Ratio
    stages_days: tuple[PositiveInt, ...]
    shock_ladder: tuple[Ratio, ...]

    @model_validator(mode="after")
    def valid_rules(self):
        for rate in (self.capture_rate_low, self.capture_rate_high, self.max_pct_of_income_event):
            if not 0 < rate.fraction <= 1:
                raise ValueError("Capture rates and income cap must be in (0, 1]")
        if self.capture_rate_high.fraction > self.capture_rate_low.fraction:
            raise ValueError("High-volatility capture may not exceed low-volatility capture")
        if self.reserve_margin.fraction < 1 or self.volatility_threshold.fraction < 0:
            raise ValueError("Invalid reserve margin or volatility threshold")
        if not self.stages_days or tuple(sorted(set(self.stages_days))) != self.stages_days:
            raise ValueError("Stages must be positive, unique, and increasing")
        if len(self.shock_ladder) != 3 or any(r.fraction <= 0 for r in self.shock_ladder):
            raise ValueError("Configure three positive illustrative scenarios")
        return self


def load_config(config_dir: Path | None = None) -> tuple[Market, Rules]:
    directory = config_dir or Path(__file__).resolve().parents[1] / "config"
    market = Market.model_validate(yaml.safe_load((directory / "markets/PH.yaml").read_text()))
    rules = Rules.model_validate(yaml.safe_load((directory / "rules.yaml").read_text()))
    return market, rules
