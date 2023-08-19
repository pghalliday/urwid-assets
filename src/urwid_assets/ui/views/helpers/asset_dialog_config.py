from _decimal import Decimal
from dataclasses import replace
from uuid import UUID

from injector import inject, singleton

from urwid_assets.state.saved.assets.assets import Asset
from urwid_assets.ui.views.helpers.symbol_config import SymbolConfigFactory, apply_symbol
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField, \
    DecimalConfigField, ChoiceConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue, \
    DecimalConfigValue, ChoiceConfigValue


def apply_asset_to_asset_dialog_config(asset_dialog_config: tuple[ConfigField, ...],
                                       asset: Asset) -> tuple[ConfigField, ...]:
    name_config = asset_dialog_config[0]
    assert isinstance(name_config, StringConfigField)
    amount_config = asset_dialog_config[1]
    assert isinstance(amount_config, DecimalConfigField)
    symbol_config = asset_dialog_config[2]
    assert isinstance(symbol_config, ChoiceConfigField)
    return (
        replace(name_config, value=asset.name),
        replace(amount_config, value=asset.amount),
        apply_symbol(symbol_config, asset.symbol)
    )


def asset_from_config_values(uuid: UUID, config_values: tuple[ConfigValue, ...]) -> Asset:
    name_config_value = config_values[0]
    assert isinstance(name_config_value, StringConfigValue)
    amount_config_value = config_values[1]
    assert isinstance(amount_config_value, DecimalConfigValue)
    symbol_config_value = config_values[2]
    assert isinstance(symbol_config_value, ChoiceConfigValue)
    return Asset(
        uuid=uuid,
        name=name_config_value.value,
        amount=amount_config_value.value,
        symbol=symbol_config_value.value,
    )


@singleton
class DefaultAssetDialogConfigFactory:
    @inject
    def __init__(self, symbol_config_factory: SymbolConfigFactory):
        self._symbol_config_factory = symbol_config_factory

    def create(self) -> tuple[ConfigField, ...]:
        return (
            StringConfigField('name', u'Name', u'New asset'),
            DecimalConfigField('amount', u'Amount', Decimal(0.0)),
            self._symbol_config_factory.create_symbol_config('symbol', u'Symbol'),
        )
