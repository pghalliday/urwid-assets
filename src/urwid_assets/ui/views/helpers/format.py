from datetime import datetime
from decimal import Decimal
from uuid import UUID

from urwid_assets.state.ui.ui import LoadedRate, get_loaded_rate, UnknownLoadedRate


def format_amount(amount: Decimal) -> str:
    return f'{amount:,.2f}'


def format_currency(currency: Decimal) -> str:
    return f'{currency:,.2f}'


def format_timestamp(timestamp: datetime | None) -> str:
    if timestamp is None:
        return u'[No timestamp]'
    return timestamp.isoformat()


NOT_AVAILABLE_TEXT = u'Not Available'
NOT_LOADED_TEXT = u'Not Loaded'


def get_value_text(rate: Decimal | None, amount: Decimal) -> str:
    if rate is None:
        return NOT_AVAILABLE_TEXT
    return format_currency(rate * amount)


def get_price_text(rate: Decimal | None) -> str:
    if rate is None:
        return NOT_AVAILABLE_TEXT
    return format_currency(rate)


def get_loaded_rate_text(uuid: UUID, loaded_rates: tuple[LoadedRate, ...]) -> str:
    try:
        loaded_rate = get_loaded_rate(uuid, loaded_rates)
    except UnknownLoadedRate:
        return NOT_LOADED_TEXT
    if loaded_rate.rate is None:
        return loaded_rate.error
    return format_currency(loaded_rate.rate)
