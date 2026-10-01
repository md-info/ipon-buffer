"""Print reproducible synthetic golden examples; does not start an API or move money."""

import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.config import load_config  # noqa: E402
from app.engine.buffer import recommend  # noqa: E402
from app.engine.types import EssentialPlan, Obligation  # noqa: E402
from app.sandbox.personas import golden_fixture  # noqa: E402


def main() -> None:
    market, rules = load_config()
    features, balances, selection, plan = golden_fixture()
    normal = recommend(features, balances, selection, plan, rules, market)
    school = Obligation(
        id="school",
        amount_minor=30_000,
        currency="PHP",
        due_date=features.as_of + timedelta(days=1),
    )
    changed_plan = EssentialPlan.model_validate(
        {**dict(plan), "obligations": (*plan.obligations, school)}
    )
    changed = recommend(features, balances, selection, changed_plan, rules, market)
    print(
        json.dumps(
            {
                "notice": "SYNTHETIC hand-computed fixture; engine output only, no money moved",
                "currency": market.currency,
                "as_of": features.as_of.isoformat(),
                "normal": {
                    "reserve_minor": normal.reserve_minor,
                    "suggestion_minor": normal.amount_minor,
                    "room_per_day_minor": normal.estimated_room_per_day_minor,
                    "reasons": normal.reason_codes,
                },
                "added_school_bill": {
                    "reserve_minor": changed.reserve_minor,
                    "suggestion_minor": changed.amount_minor,
                    "shortfall_minor": changed.shortfall_minor,
                    "reasons": changed.reason_codes,
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
