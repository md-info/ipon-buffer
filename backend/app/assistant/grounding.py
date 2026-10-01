"""Conservative English draft checks, not a general natural-language parser.

These checks can clear or reject model fields, never invent replacement values.
Passing them is not proof of semantic correctness; user review is still required.
"""

import calendar
import re
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .service import Proposal

GROUNDING_VERSION = "1"
INCOME = re.compile(r"\b(income|salary|wages?|earn(?:ed|ings)?|get paid|paid tomorrow)\b", re.I)
UNSUPPORTED = re.compile(
    r"\b(already paid|cancel|delete|remove|transfer|tool call|ignore .*rules)\b|\bsystem\s*:"
    r"|\b(USD|dollars?|EUR|euros?|SGD|MYR|THB|IDR|VND)\b|[$€£]",
    re.I,
)


def supported_date(value: str | None, excerpt: str, reference: date) -> bool:
    """Require a supported, unambiguous date anchor in the cited text."""
    if value is None:
        return False
    proposed = date.fromisoformat(value)
    if proposed < reference:
        return False
    source = excerpt.lower()
    if re.search(
        r"\b(next (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week)"
        r"|sometime)\b",
        source,
    ):
        return False
    anchors = set()
    if re.search(r"\btomorrow\b", source):
        anchors.add(reference + timedelta(days=1))
    if re.search(r"\btoday\b", source):
        anchors.add(reference)
    if re.search(r"\bend of (?:the|this) month\b", source):
        anchors.add(reference.replace(day=calendar.monthrange(reference.year, reference.month)[1]))
    for match in re.finditer(r"\b\d{4}-\d{2}-\d{2}\b", source):
        try:
            anchors.add(date.fromisoformat(match.group()))
        except ValueError:
            return False
    for month in range(1, 13):
        names = f"{calendar.month_name[month].lower()}|{calendar.month_abbr[month].lower()}"
        for match in re.finditer(
            rf"\b(?:{names})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?\b",
            source,
        ):
            try:
                anchors.add(date(int(match[2] or reference.year), month, int(match[1])))
            except ValueError:
                return False
    # Conflicting anchors need the user's decision, even when one matches the model.
    return anchors == {proposed}


def grounded_amount(value: str | None, excerpt: str) -> bool:
    if value is None:
        return False
    # A range or sign cannot be resolved just by finding a matching number.
    excerpt = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", excerpt)
    if re.search(r"\b(between|minus|negative|about|roughly)\b|[-−–]\s*\d", excerpt, re.I):
        return False
    numbers = re.findall(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?(?!\w|\.\d)", excerpt)
    return Decimal(value) in {Decimal(number.replace(",", "")) for number in numbers}


def ground_proposal(proposal: "Proposal", text: str, reference: date) -> "Proposal":
    """Remove unsupported suggestions and derive status from surviving fields."""
    result = proposal.model_copy(deep=True)
    if result.status == "unsupported" or UNSUPPORTED.search(text):
        result.status = "unsupported"
        result.candidates = []
        result.expected_income_date = None
        result.income_tentative = False
        result.clarification = "Please use manual planning for this request. No changes were made."
        return result
    result.candidates = [c for c in result.candidates if not INCOME.search(c.source_excerpt)]
    for candidate in result.candidates:
        source = candidate.source_excerpt.lower()
        if not grounded_amount(candidate.amount, source) or not grounded_amount(
            candidate.amount, text
        ):
            candidate.amount = None
        if not supported_date(candidate.due_date, source, reference):
            candidate.due_date = None
        evidence = {
            "one_off": bool(re.search(r"\b(one[- ]time|one[- ]off|once)\b", source)),
            "monthly": bool(re.search(r"\b(monthly|each month|every month)\b", source)),
        }
        if (
            not evidence.get(candidate.recurrence)
            or all(evidence.values())
            or re.search(r"\bnot\s+(?:a\s+)?(?:monthly|one[- ]time|one[- ]off)\b", text, re.I)
        ):
            candidate.recurrence = "unknown"
        # Always ask this separate budgeting question. Text alone cannot establish
        # whether an expense is already counted in the user's confirmed daily amount.
        candidate.included_in_daily = None
    if not INCOME.search(text) or not supported_date(result.expected_income_date, text, reference):
        result.expected_income_date = None
    result.income_tentative = bool(INCOME.search(text)) and bool(
        re.search(r"\b(maybe|might|should|possibly|expect(?:ed)?)\b", text, re.I)
    )
    if result.candidates:
        result.status = "needs_clarification"
        result.clarification = (
            "Review each bill and choose whether it is already included in everyday essentials. "
            "Fill any blank amount or date and choose a recurrence before confirming."
        )
    elif result.expected_income_date:
        result.status = "ready_for_review"
        result.clarification = "Review the expected income date before confirming."
    else:
        result.status = "needs_clarification"
        result.clarification = (
            "No complete change could be verified. Clarify your text or use manual entry."
        )
    return result
