"""Hand-computed synthetic golden fixture; not a real user's finances."""

from datetime import date, timedelta

from app.engine.features import compute_features
from app.engine.types import Balances, EssentialPlan, IncomeSelection, Obligation, Txn

AS_OF = date(2026, 9, 28)


def golden_fixture():
    start = AS_OF - timedelta(days=60)
    txns = []
    for offset in range(61):
        day = start + timedelta(days=offset)
        txns.append(
            Txn(
                id=f"routine-{offset}",
                date=day,
                amount_minor=-25_000,
                currency="PHP",
                kind="routine_essential",
            )
        )
        if offset % 4 == 0:
            txns.append(
                Txn(
                    id=f"income-{offset}",
                    date=day,
                    amount_minor=100_000,
                    currency="PHP",
                    kind="income",
                )
            )
    features = compute_features(tuple(txns), coverage_start=start, as_of=AS_OF, currency="PHP")
    plan = EssentialPlan(
        currency="PHP",
        confirmed=True,
        next_expected_income=AS_OF + timedelta(days=4),
        obligations=(
            Obligation(
                id="bill", amount_minor=60_000, currency="PHP", due_date=AS_OF + timedelta(days=2)
            ),
        ),
    )
    return (
        features,
        Balances(currency="PHP", available_minor=200_000, buffer_minor=50_000),
        IncomeSelection(event_id="income-60"),
        plan,
    )
