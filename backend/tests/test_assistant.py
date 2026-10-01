"""Transport fixtures validate adapter boundaries, not real-model quality."""

import io
import json
from datetime import date

import pytest
from app.assistant.service import ModelAdapter, minor_units


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-1", "0", "1.001", "1000001"])
def test_invalid_model_amounts(amount):
    with pytest.raises(ValueError):
        minor_units(amount)


@pytest.mark.parametrize(
    "base", ["https://example.com", "http://192.168.1.2:11434", "http://user:pass@localhost:11434"]
)
def test_remote_or_credential_endpoint_rejected(monkeypatch, base):
    monkeypatch.setenv("IPON_AI_BASE_URL", base)
    with pytest.raises(ValueError):
        ModelAdapter()


@pytest.mark.parametrize(
    "response", [{"done": False}, {"done": True, "message": {"content": "{}"}}]
)
def test_incomplete_or_invalid_response(monkeypatch, response):
    monkeypatch.setenv("IPON_AI_MODEL", "transport-fixture-only")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **k: io.BytesIO(json.dumps(response).encode())
    )
    with pytest.raises((ValueError, KeyError)):
        ModelAdapter().parse("School tomorrow", date(2026, 9, 28))


@pytest.mark.parametrize("done_reason", ["stop", "length"])
def test_completed_draft_and_truncated_draft(monkeypatch, done_reason):
    """Only a complete response may become a reviewable draft."""
    proposal = {
        "status": "needs_clarification",
        "candidates": [
            {
                "label": "School",
                "amount": "300",
                "currency": "PHP",
                "due_date": "2026-09-29",
                "recurrence": "unknown",
                "included_in_daily": None,
                "source_excerpt": "School 300 tomorrow",
            }
        ],
        "expected_income_date": None,
        "income_tentative": False,
        "clarification": "Is this one time and outside your daily budget?",
    }
    response = {
        "done": True,
        "done_reason": done_reason,
        "message": {"content": json.dumps(proposal)},
        "eval_count": 100,
    }
    monkeypatch.setenv("IPON_AI_MODEL", "transport-fixture-only")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **k: io.BytesIO(json.dumps(response).encode())
    )
    metrics = {}
    if done_reason == "length":
        with pytest.raises(ValueError, match="Incomplete"):
            ModelAdapter().parse("School 300 tomorrow", date(2026, 9, 28), metrics=metrics)
    else:
        draft = ModelAdapter().parse("School 300 tomorrow", date(2026, 9, 28), metrics=metrics)
        assert draft.candidates[0].amount == "300"
        assert draft.candidates[0].included_in_daily is None
        assert metrics["eval_count"] == 100
