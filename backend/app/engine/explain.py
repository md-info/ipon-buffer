"""Pure template rendering; language packs are loaded by the application boundary."""

from collections.abc import Mapping

from app.config import Market
from app.engine.buffer import Recommendation


def format_money(amount_minor: int, market: Market) -> str:
    if type(amount_minor) is not int:
        raise ValueError("Money must use integer minor units")
    exponent = market.minor_unit_exponent
    sign = "-" if amount_minor < 0 else ""
    major, minor = divmod(abs(amount_minor), 10**exponent)
    value = f"{major:,}" + (f".{minor:0{exponent}d}" if exponent else "")
    return f"{market.currency} {sign}{value}"


def explain(
    rec: Recommendation, market: Market, language: str, templates: Mapping[str, str]
) -> tuple[str, ...]:
    if language not in market.languages:
        raise ValueError("Language is not enabled in the market")
    if rec.currency != market.currency:
        raise ValueError("Explanation market does not match recommendation")
    fields = {
        "amount": format_money(rec.amount_minor, market),
        "reserve": format_money(rec.reserve_minor, market),
        "date": rec.protected_through.isoformat(),
    }
    return tuple(templates[code].format_map(fields) for code in rec.reason_codes[:3])
