from _decimal import Decimal
from uuid import UUID

from injector import inject, singleton

from urwid_assets.ui.views.helpers.data_source_config import apply_data_source_config_choice, \
    data_source_config_from_choice, \
    create_endpoint_config
from urwid_assets.ui.widgets.dialogs.config_dialog import StringConfigField, ConfigField, ChoiceConfigField, \
    ConfigFieldChoice, \
    DecimalConfigField, ConfigValue, StringConfigValue, DecimalConfigValue, ChoiceConfigValue
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.store import Store
from urwid_assets.state.assets.assets import AssetDataSource, Asset
from urwid_assets.state.data_sources.data_sources import DataSourceInstance
from urwid_assets.state.state import State


def _apply_asset_to_endpoint_config(data_source_choice: ConfigFieldChoice,
                                    asset_data_source: AssetDataSource) -> ConfigFieldChoice:
    endpoint_config = data_source_choice.sub_fields[0]
    assert isinstance(endpoint_config, ChoiceConfigField)
    return ConfigFieldChoice(
        value=data_source_choice.value,
        display_text=data_source_choice.display_text,
        sub_fields=(ChoiceConfigField(
            name=endpoint_config.name,
            display_name=endpoint_config.display_name,
            value=asset_data_source.endpoint,
            choices=tuple(apply_data_source_config_choice(choice, asset_data_source.config)
                          if asset_data_source.endpoint == choice.value else choice
                          for choice in endpoint_config.choices)
        ),)
    )


def _apply_asset_to_data_source_config(data_source_config: ConfigField,
                                       asset_data_source: AssetDataSource) -> ChoiceConfigField:
    assert isinstance(data_source_config, ChoiceConfigField)
    return ChoiceConfigField(
        name=data_source_config.name,
        display_name=data_source_config.display_name,
        value=asset_data_source.uuid,
        choices=tuple(_apply_asset_to_endpoint_config(choice, asset_data_source)
                      if asset_data_source.uuid == choice.value else choice
                      for choice in data_source_config.choices)
    )


def apply_asset_to_asset_dialog_config(asset_dialog_config: tuple[ConfigField, ...],
                                       asset: Asset) -> tuple[ConfigField, ...]:
    return (
        StringConfigField(asset_dialog_config[0].name, asset_dialog_config[0].display_name, asset.name),
        DecimalConfigField(asset_dialog_config[1].name, asset_dialog_config[1].display_name, asset.amount),
        _apply_asset_to_data_source_config(asset_dialog_config[2], asset.data_source)
    )


def _asset_data_source_from_config_value(data_source_config_value: ChoiceConfigValue) -> AssetDataSource:
    endpoint_config_value = data_source_config_value.sub_values[0]
    assert isinstance(endpoint_config_value, ChoiceConfigValue)
    (endpoint_name, endpoint_config) = data_source_config_from_choice(endpoint_config_value)
    return AssetDataSource(
        uuid=data_source_config_value.value,
        endpoint=endpoint_name,
        config=endpoint_config,
    )


def asset_from_config_values(uuid: UUID, config_values: tuple[ConfigValue, ...]) -> Asset:
    name_config_value = config_values[0]
    assert isinstance(name_config_value, StringConfigValue)
    amount_config_value = config_values[1]
    assert isinstance(amount_config_value, DecimalConfigValue)
    data_source_config_value = config_values[2]
    assert isinstance(data_source_config_value, ChoiceConfigValue)
    return Asset(
        uuid=uuid,
        name=name_config_value.value,
        amount=amount_config_value.value,
        data_source=_asset_data_source_from_config_value(data_source_config_value),
    )


@singleton
class DefaultAssetDialogConfigFactory:
    @inject
    def __init__(self, data_source_registry: DataSourceRegistry, store: Store[State]):
        self._data_source_registry = data_source_registry
        self._store = store

    def _create_data_source_choice(
            self,
            data_source_state: DataSourceInstance
    ) -> ConfigFieldChoice:
        data_source = self._data_source_registry.get_data_source(data_source_state.type)
        return ConfigFieldChoice(
            value=data_source_state.uuid,
            display_text=data_source_state.name,
            sub_fields=(create_endpoint_config(data_source.get_endpoints()),)
        )

    def _create_data_source_config(self) -> ChoiceConfigField:
        data_source_states = self._store.get_state().data_sources
        return ChoiceConfigField(
            name='data_sources',
            display_name=u'Data source',
            value=data_source_states[0].uuid,
            choices=tuple(self._create_data_source_choice(data_source) for data_source in data_source_states)
        )

    def create(self) -> tuple[ConfigField, ...]:
        return (
            StringConfigField('name', u'Name', u'New asset'),
            DecimalConfigField('amount', u'Amount', Decimal(0.0)),
            self._create_data_source_config(),
        )
