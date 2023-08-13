from _decimal import Decimal

from state.assets.assets import Asset
from state.snapshots.snapshots import AssetSnapshot


def format_amount(amount: Decimal) -> str:
    return f'{amount:,.2f}'


def format_currency(currency: Decimal) -> str:
    return f'{currency:,.2f}'


NOT_LOADED_TEXT = u'Not loaded'


def get_value_text(asset: Asset | AssetSnapshot) -> str:
    if asset.error is None:
        if asset.price is None:
            return NOT_LOADED_TEXT
        return format_currency(asset.price * asset.amount)
    return asset.error


def get_price_text(asset: Asset | AssetSnapshot) -> str:
    if asset.error is None:
        if asset.price is None:
            return NOT_LOADED_TEXT
        return format_currency(asset.price)
    return asset.error
