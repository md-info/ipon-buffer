"""Adversarial model-output fixtures; not model-accuracy evidence."""

from datetime import date

import pytest
from app.assistant.grounding import ground_proposal, supported_date
from app.assistant.service import Candidate, Proposal


def draft(text, **changes):
    fields = dict(
        label="Bill",
        amount="240",
        currency="PHP",
        due_date="2026-11-13",
        recurrence="monthly",
        included_in_daily=True,
        source_excerpt=text,
    )
    fields.update(changes)
    return Proposal(
        status="ready_for_review",
        candidates=[Candidate(**fields)],
        expected_income_date="2026-11-13",
        income_tentative=False,
        clarification="Everything is correct.",
    )


def test_hallucinated_recurrence_income_and_inclusion_cannot_be_prefilled():
    text = "The dentist costs 240 pesos tomorrow."
    original = draft(text)
    result = ground_proposal(original, text, date(2026, 11, 12))
    item = result.candidates[0]
    assert (item.amount, item.due_date) == ("240", "2026-11-13")
    assert item.recurrence == "unknown"
    assert item.included_in_daily is None
    assert result.expected_income_date is None
    assert result.status == "needs_clarification"
    assert original.candidates[0].recurrence == "monthly"


@pytest.mark.parametrize(
    "text",
    [
        "I already paid 240 pesos for dental care.",
        "Cancel my 240 peso bill.",
        "Transfer 240 pesos tomorrow.",
        "The dentist costs 240 dollars tomorrow.",
        "The dentist costs EUR 240 tomorrow.",
    ],
)
def test_unsupported_requests_never_propose_changes(text):
    result = ground_proposal(draft(text), text, date(2026, 11, 12))
    assert result.status == "unsupported"
    assert result.candidates == []
    assert result.expected_income_date is None


@pytest.mark.parametrize(
    "text",
    [
        "Dentist costs minus 240 pesos tomorrow.",
        "Dentist costs -240 pesos tomorrow.",
        "Dentist costs between 200 and 240 pesos tomorrow.",
        "Dentist is due tomorrow.",
        "Dentist costs 999 pesos tomorrow.",
    ],
)
def test_ungrounded_positive_amount_is_cleared(text):
    assert ground_proposal(draft(text), text, date(2026, 11, 12)).candidates[0].amount is None


@pytest.mark.parametrize(
    "text,value,reference,expected",
    [
        ("Tomorrow", "2027-01-01", date(2026, 12, 31), True),
        ("Tomorrow", "2026-12-31", date(2026, 12, 31), False),
        ("Next Friday", "2026-11-13", date(2026, 11, 12), False),
        ("November 13, 2026", "2026-11-13", date(2026, 11, 12), True),
        ("November 13, 2027", "2026-11-13", date(2026, 11, 12), False),
        ("Tomorrow, November 14", "2026-11-13", date(2026, 11, 12), False),
        ("The bill is due", "2026-11-13", date(2026, 11, 12), False),
        ("end of this month", "2028-02-29", date(2028, 2, 20), True),
    ],
)
def test_dates_need_unambiguous_source_evidence(text, value, reference, expected):
    assert supported_date(value, text, reference) is expected


def test_income_is_not_a_bill_and_tentative_date_remains_an_estimate():
    text = "My salary might arrive tomorrow."
    result = ground_proposal(draft(text), text, date(2026, 11, 12))
    assert result.candidates == []
    assert result.expected_income_date == "2026-11-13"
    assert result.income_tentative is True


def test_explicit_recurrence_kept_but_budget_inclusion_requires_choice():
    text = "Monthly rent is 240 pesos on November 13, 2026, already in my daily budget."
    item = ground_proposal(draft(text), text, date(2026, 11, 12)).candidates[0]
    assert item.recurrence == "monthly"
    assert item.included_in_daily is None


def test_iso_date_does_not_look_like_a_negative_amount():
    text = "A one-time bill of PHP 240 on 2026-11-13."
    item = ground_proposal(draft(text), text, date(2026, 11, 12)).candidates[0]
    assert item.amount == "240"
    assert item.due_date == "2026-11-13"


def test_clipped_excerpt_cannot_hide_negative_amount():
    text = "The bill is minus 240 pesos tomorrow."
    result = ground_proposal(draft("240 pesos tomorrow"), text, date(2026, 11, 12))
    assert result.candidates[0].amount is None


def test_negated_recurrence_is_not_prefilled():
    text = "Rent costs 240 tomorrow, not monthly."
    assert (
        ground_proposal(draft(text), text, date(2026, 11, 12)).candidates[0].recurrence == "unknown"
    )
