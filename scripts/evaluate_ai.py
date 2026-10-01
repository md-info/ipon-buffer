"""Explicit synthetic-only real-model evaluation, outside default offline tests."""

import argparse
import json
import sys
import time
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.assistant.service import PROMPT_VERSION, ModelAdapter  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="reports/ai_run.json")
    parser.add_argument("--corpus", default="evaluation/ai_cases.json")
    args = parser.parse_args()
    model = ModelAdapter()
    if model.mode == "disabled":
        raise SystemExit("No model configured. No inference run or evaluation result produced.")
    corpus = json.loads((ROOT / args.corpus).read_text(encoding="utf-8"))
    rows = []
    for case in corpus["cases"]:
        started = time.monotonic()
        metrics = {}
        try:
            proposal = model.parse(
                case["text"], date.fromisoformat(case["reference_date"]), metrics=metrics
            )
            row = {
                "id": case["id"],
                "schema_valid": True,
                "proposal": proposal.model_dump(),
                "human_review": None,
            }
        except Exception as error:
            row = {
                "id": case["id"],
                "schema_valid": False,
                "error_type": type(error).__name__,
                "error": str(error),
                "human_review": None,
            }
        row["latency_seconds"] = round(time.monotonic() - started, 3)
        row["runtime_metrics"] = metrics
        rows.append(row)
        print(case["id"], row["schema_valid"], row["latency_seconds"], flush=True)
    result = {
        "model": model.model,
        "protocol": model.protocol,
        "prompt_version": PROMPT_VERSION,
        "corpus_version": corpus["version"],
        "run_at": datetime.now(UTC).isoformat(),
        "field_accuracy": None,
        "ambiguity_handling": None,
        "measured_usage": "Per-case Ollama token counts and nanosecond durations where returned",
        "limitation": "Schema validity is not extraction accuracy. Review every case.",
        "results": rows,
    }
    (ROOT / args.output).write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
