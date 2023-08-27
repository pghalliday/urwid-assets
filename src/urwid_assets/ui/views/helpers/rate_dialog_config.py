from dataclasses import replace
from uuid import UUID

from injector import inject, singleton

from urwid_assets.state.saved.rates.rates import Rate
from urwid_assets.ui.views.helpers.data_source_config import DataSourceConfigFactory, data_source_from_config_value, \
    apply_data_source
from urwid_assets.ui.views.helpers.symbol_config import SymbolConfigFactory, apply_symbol
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField, \
    IntegerConfigField, ChoiceConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue, \
    IntegerConfigValue, ChoiceConfigValue


def apply_rate_to_rate_dialog_config(rate_dialog_config: tuple[ConfigField, ...],
                                     rate: Rate) -> tuple[ConfigField, ...]:
    name_config = rate_dialog_config[0]
    assert isinstance(name_config, StringConfigField)
    cost_config = rate_dialog_config[1]
    assert isinstance(cost_config, IntegerConfigField)
    from_symbol_config = rate_dialog_config[2]
    assert isinstance(from_symbol_config, ChoiceConfigField)
    to_symbol_config = rate_dialog_config[3]
    assert isinstance(to_symbol_config, ChoiceConfigField)
    data_source_config = rate_dialog_config[4]
    assert isinstance(data_source_config, ChoiceConfigField)
    return (
        replace(name_config, value=rate.name),
        replace(cost_config, value=rate.cost),
        apply_symbol(from_symbol_config, rate.from_symbol),
        apply_symbol(to_symbol_config, rate.to_symbol),
        apply_data_source(data_source_config, rate.data_source, rate.endpoint, rate.config)
    )


def rate_from_config_values(uuid: UUID, config_values: tuple[ConfigValue, ...]) -> Rate:
    name_config_value = config_values[0]
    assert isinstance(name_config_value, StringConfigValue)
    cost_config_value = config_values[1]
    assert isinstance(cost_config_value, IntegerConfigValue)
    from_symbol_config_value = config_values[2]
    assert isinstance(from_symbol_config_value, ChoiceConfigValue)
    to_symbol_config_value = config_values[3]
    assert isinstance(to_symbol_config_value, ChoiceConfigValue)
    data_source_config_value = config_values[4]
    assert isinstance(data_source_config_value, ChoiceConfigValue)
    (data_source, endpoint, config) = data_source_from_config_value(data_source_config_value)
    return Rate(
        uuid=uuid,
        name=name_config_value.value,
        cost=cost_config_value.value,
        from_symbol=from_symbol_config_value.value,
        to_symbol=to_symbol_config_value.value,
        data_source=data_source,
        endpoint=endpoint,
        config=config,
    )


@singleton
class DefaultRateDialogConfigFactory:
    @inject
    def __init__(self,
                 data_source_config_factory: DataSourceConfigFactory,
                 symbol_config_factory: SymbolConfigFactory):
        self._data_source_config_factory = data_source_config_factory
        self._symbol_config_factory = symbol_config_factory

    def create(self) -> tuple[ConfigField, ...]:
        return (
            StringConfigField('name', u'Name', u'New rate'),
            IntegerConfigField('cost', u'Cost', 1),
            self._symbol_config_factory.create_symbol_config('from_symbol', u'From symbol'),
            self._symbol_config_factory.create_symbol_config('to_symbol', u'To symbol'),
            self._data_source_config_factory.create_data_source_config('data_source', u'Data source'),
        )
