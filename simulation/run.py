"""Fixed synthetic scenarios. No behavioural effect or population inference."""

import csv
import hashlib
import json
import random
import sys
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import load_config  # noqa: E402
from app.engine.buffer import recommend  # noqa: E402
from app.engine.features import compute_features  # noqa: E402
from app.engine.types import (  # noqa: E402
    Balances,
    EssentialPlan,
    IncomeSelection,
    Obligation,
    Txn,
)

START = date(2026, 1, 1)
PATTERNS = ("regular", "variable_amount", "variable_gap")
SCENARIOS = ("base", "delayed_income", "missing_bill", "higher_essentials", "larger_shocks")
STRATEGIES = ("none", "fixed_10pct", "ipon")
SEED = 20260928


def path_for(person: int, scenario: str) -> list[dict]:
    rng = random.Random(SEED + person)
    pattern = PATTERNS[person % 3]
    days = [
        {
            "day": n,
            "income": 0,
            "routine": 25000,
            "bill": 0,
            "discretionary": rng.randint(20, 80) * 100,
            "shock": 0,
        }
        for n in range(-30, 180)
    ]
    n = -30
    while n < 180:
        days[n + 30]["income"] += (
            rng.randint(650, 1750) * 100 if pattern == "variable_amount" else 120000
        )
        n += rng.randint(2, 6) if pattern == "variable_gap" else 4
    for row in days:
        n = row["day"]
        if n >= 0 and n % 30 == 10:
            row["bill"] = 60000
        if n >= 0 and rng.randrange(60) == 0:
            row["shock"] = rng.choice([75000, 150000, 300000])
    if scenario == "delayed_income":
        for row in list(days):
            n = row["day"]
            if 60 <= n < 70 and row["income"]:
                amount = row["income"]
                row["income"] = 0
                days[n + 33]["income"] += amount
                break
    for row in days:
        if row["day"] >= 60 and scenario == "higher_essentials":
            row["routine"] = 30000
        if scenario == "larger_shocks":
            row["shock"] *= 2
    return days


def simulate(person: int, scenario: str, strategy: str) -> dict:
    path = path_for(person, scenario)
    market, rules = load_config()
    wallet, buffer = 200000, 50000
    income_total = spent = essential_missing = shock_missing = discretionary_missing = 0
    shortfall_days = shocks = funded = transfers = 0
    max_stage = 0
    observations = []
    history = []
    for row in path:
        n = row["day"]
        today = START + timedelta(days=n)
        if row["income"]:
            history.append(
                Txn(
                    id=f"income-{n}",
                    date=today,
                    currency="PHP",
                    amount_minor=row["income"],
                    kind="income",
                )
            )
        if n < 0:
            history.append(
                Txn(
                    id=f"routine-{n}",
                    date=today,
                    currency="PHP",
                    amount_minor=-row["routine"],
                    kind="routine_essential",
                )
            )
            continue
        wallet += row["income"]
        income_total += row["income"]
        # Decision sees only income received and past paid spending, plus known bills.
        deposit = 0
        if row["income"]:
            if strategy == "fixed_10pct":
                deposit = min(wallet, row["income"] // 10)
            elif strategy == "ipon":
                features = compute_features(
                    tuple(history),
                    coverage_start=START - timedelta(days=30),
                    as_of=today,
                    currency="PHP",
                )
                known = tuple(
                    Obligation(
                        id=f"bill-{due}",
                        currency="PHP",
                        amount_minor=60000,
                        due_date=START + timedelta(days=due),
                    )
                    for due in range(10, 180, 30)
                    if due >= n and not (scenario == "missing_bill" and due == 70)
                )
                plan = EssentialPlan(
                    currency="PHP", confirmed=True, routine_daily_minor=25000, obligations=known
                )
                rec = recommend(
                    features,
                    Balances(currency="PHP", available_minor=wallet, buffer_minor=buffer),
                    IncomeSelection(event_id=f"income-{n}"),
                    plan,
                    rules,
                    market,
                )
                deposit = rec.amount_minor
                assert not deposit or all(check.passed for check in rec.guardrail_results)
            wallet -= deposit
            buffer += deposit
            transfers += deposit

        def pay(demand: int, use_buffer: bool) -> int:
            nonlocal wallet, buffer, spent
            if use_buffer:
                draw = min(buffer, max(0, demand - wallet))
                buffer -= draw
                wallet += draw
            paid = min(wallet, demand)
            wallet -= paid
            spent += paid
            return demand - paid

        missing_routine = pay(row["routine"], True)
        paid_routine = row["routine"] - missing_routine
        if paid_routine:
            history.append(
                Txn(
                    id=f"routine-{n}",
                    date=today,
                    currency="PHP",
                    amount_minor=-paid_routine,
                    kind="routine_essential",
                )
            )
        missing_bill = pay(row["bill"], True)
        essential_missing += missing_routine + missing_bill
        shortfall_days += bool(missing_routine + missing_bill)
        missing_shock = pay(row["shock"], True)
        if row["shock"]:
            shocks += 1
            funded += missing_shock == 0
        shock_missing += missing_shock
        discretionary_missing += pay(row["discretionary"], False)
        # Measured after every expense; monthly known essentials = 250*30 + 600.
        days_cover = Fraction(buffer * 30, 810000)
        observations.append(days_cover)
        max_stage = max(
            max_stage, max((s for s in rules.stages_days if days_cover >= s), default=0)
        )
        assert wallet >= 0 and buffer >= 0
        assert wallet + buffer == 250000 + income_total - spent
    return {
        "person": person,
        "pattern": PATTERNS[person % 3],
        "scenario": scenario,
        "strategy": strategy,
        "path_sha256": hashlib.sha256(json.dumps(path, sort_keys=True).encode()).hexdigest(),
        "essential_shortfall_days": shortfall_days,
        "essential_unmet_minor": essential_missing,
        "shocks": shocks,
        "fully_funded_shocks": funded,
        "shock_unmet_minor": shock_missing,
        "shock_funding_rate": str(Fraction(funded, shocks)) if shocks else None,
        "discretionary_unmet_minor": discretionary_missing,
        "median_buffer_days": str(median(observations)),
        "max_stage_days": max_stage,
        "wallet_minor": wallet,
        "buffer_minor": buffer,
        "total_liquid_minor": wallet + buffer,
        "income_minor": income_total,
        "spent_minor": spent,
        "deposited_minor": transfers,
        "conservation_error_minor": wallet + buffer - (250000 + income_total - spent),
    }


def run():
    results = [
        simulate(person, scenario, strategy)
        for scenario in SCENARIOS
        for person in range(90)
        for strategy in STRATEGIES
    ]
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    with (report_dir / "simulation_results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    summary = []
    for scenario in SCENARIOS:
        for strategy in STRATEGIES:
            rows = [r for r in results if r["scenario"] == scenario and r["strategy"] == strategy]
            summary.append(
                {
                    "scenario": scenario,
                    "strategy": strategy,
                    "households": len(rows),
                    **{
                        k: sum(r[k] for r in rows)
                        for k in (
                            "essential_shortfall_days",
                            "essential_unmet_minor",
                            "shocks",
                            "fully_funded_shocks",
                            "shock_unmet_minor",
                            "discretionary_unmet_minor",
                            "total_liquid_minor",
                            "conservation_error_minor",
                        )
                    },
                    "median_household_buffer_days": str(
                        median(Fraction(r["median_buffer_days"]) for r in rows)
                    ),
                    "ever_reached_7_days": sum(r["max_stage_days"] >= 7 for r in rows),
                }
            )
    (report_dir / "simulation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [
        "# Synthetic comparison",
        "",
        "Seed 20260928; 90 synthetic households (30 per pattern); "
        "180 days after 30 days of history.",
        "No real users, behavioural benefit, model extraction, or causal impact was measured.",
        "",
        "| Scenario | Strategy | Essential shortfall days | Funded / shocks | Unmet shock PHP "
        "| Unmet discretionary PHP | Median household buffer days |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['scenario']} | {row['strategy']} | {row['essential_shortfall_days']} | "
            f"{row['fully_funded_shocks']} / {row['shocks']} | "
            f"{row['shock_unmet_minor'] / 100:.2f} | "
            f"{row['discretionary_unmet_minor'] / 100:.2f} | "
            f"{float(Fraction(row['median_household_buffer_days'])):.2f} |"
        )
    lines += [
        "",
        "See simulation/ASSUMPTIONS.md for frozen rules, measurement definitions, and limitations.",
        "All ledger reconciliations are zero. Raw rows include pattern, final liquid funds, "
        "stage attainment, and unavailable zero-shock rates.",
        "Saving moves money between accounts; it creates no income. "
        "Discretionary demand is recorded even when unpaid.",
        "Higher liquid balances can reflect suppressed discretionary spending, "
        "not greater resources or welfare.",
    ]
    (report_dir / "simulation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary[:3], indent=2))


if __name__ == "__main__":
    run()
