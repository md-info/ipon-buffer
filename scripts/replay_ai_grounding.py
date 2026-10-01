"""Replay saved synthetic model outputs through current guards; no new inference."""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.assistant.grounding import GROUNDING_VERSION, ground_proposal  # noqa: E402
from app.assistant.service import Proposal  # noqa: E402


def main():
    corpus = json.loads((ROOT / "evaluation/ai_cases.json").read_text())
    cases = {c["id"]: c for c in corpus["cases"]}
    run = json.loads((ROOT / "reports/ai_run_v3.json").read_text())
    rows, counts = [], Counter()
    for row in run["results"]:
        if not row["schema_valid"]:
            counts["previously_rejected"] += 1
            rows.append({"id": row["id"], "previously_rejected": True})
            continue
        case = cases[row["id"]]
        before = Proposal.model_validate(row["proposal"])
        after = ground_proposal(before, case["text"], date.fromisoformat(case["reference_date"]))
        counts[after.status] += 1
        counts["income_dates_removed"] += bool(before.expected_income_date) and not bool(
            after.expected_income_date
        )
        counts["candidates_removed"] += len(before.candidates) - len(after.candidates)
        rows.append({"id": row["id"], "before": before.model_dump(), "after": after.model_dump()})
    result = {
        "type": "deterministic replay of saved real-model outputs; NOT new model inference",
        "grounding_version": GROUNDING_VERSION,
        "source": "ai_run_v3.json",
        "counts": dict(counts),
        "limitation": "Changes and rejection counts are not accuracy scores.",
        "results": rows,
    }
    (ROOT / "reports/ai_grounding_replay.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["counts"], indent=2))
    # The live run retained raw proposals, so later guard edits can be checked
    # without silently labelling replay as fresh inference.
    live = json.loads((ROOT / "reports/ai_grounding_live.json").read_text())
    smoke = json.loads((ROOT / "evaluation/ai_grounding_cases.json").read_text())
    for row, case in zip(live["results"], smoke["cases"], strict=True):
        raw = Proposal.model_validate(row["runtime_metrics"]["raw_proposal"])
        current = ground_proposal(raw, case["text"], date.fromisoformat(case["reference_date"]))
        assert current.model_dump() == row["proposal"], f"Guard output changed: {row['id']}"
    print("Current guard output matches all 12 captured live results.")


if __name__ == "__main__":
    main()
