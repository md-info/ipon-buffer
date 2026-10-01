"""Calendar-aware monthly occurrences, anchored to the original day of month."""

from calendar import monthrange
from datetime import date

from app.engine.types import Obligation


def due_amount(bill: Obligation, start: date, end: date) -> int:
    if end < start:
        raise ValueError("Obligation window ends before it starts")
    if bill.included_in_daily:
        return 0
    if bill.recurrence == "one_off":
        return bill.amount_minor if not bill.paid and start <= bill.due_date <= end else 0
    first_month = bill.due_date.year * 12 + bill.due_date.month - 1
    start_month = max(first_month, start.year * 12 + start.month - 1)
    end_month = end.year * 12 + end.month - 1
    occurrences = 0
    for month_index in range(start_month, end_month + 1):
        year, month_zero = divmod(month_index, 12)
        month = month_zero + 1
        day = min(bill.due_date.day, monthrange(year, month)[1])
        occurrence = date(year, month, day)
        if start <= occurrence <= end and not (bill.paid and month_index == first_month):
            occurrences += 1
    return occurrences * bill.amount_minor
