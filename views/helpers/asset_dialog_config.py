from _decimal import Decimal
from uuid import UUID

from injector import inject, singleton

from lib.data_sources.data_source import DataSource
from lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField, DataSourceEndpoint, \
    DataSourceConfig, StringDataSourceConfig
from lib.redux.store import Store
from lib.widgets.dialogs.config_dialog import StringConfigField, ConfigField, ChoiceConfigField, ConfigFieldChoice, \
    DecimalConfigField, ConfigValue, StringConfigValue, DecimalConfigValue, ChoiceConfigValue
from state.assets.assets import AssetDataSource, Asset
from state.data_sources.data_sources import DataSourceInstance
from state.state import State


class UnknownDataSource(Exception):
    name: str

    def __init__(self, name: str):
        super().__init__(u'Unknown data source: %s' % name)
        self.name = name


class UnknownDataSourceConfigFieldType(Exception):
    field: DataSourceConfigField

    def __init__(self, field: DataSourceConfigField):
        super().__init__(u'Unknown data source config field: %s' % field)
        self.field = field


class UnknownConfigFieldType(Exception):
    field: ConfigField

    def __init__(self, field: ConfigField):
        super().__init__(u'Unknown config field: %s' % field)
        self.field = field


class UnknownConfigValueType(Exception):
    value: ConfigValue

    def __init__(self, value: ConfigValue):
        super().__init__(u'Unknown config value: %s' % value)
        self.value = value


def _create_field_config_from_data_source(field: DataSourceConfigField) -> ConfigField:
    if isinstance(field, StringDataSourceConfigField):
        return StringConfigField(
            name=field.name,
            display_name=field.display_name,
            value=field.default,
            secret=field.secret,
        )
    raise UnknownDataSourceConfigFieldType(field)


def _create_endpoint_config(endpoints: tuple[DataSourceEndpoint, ...]) -> ChoiceConfigField:
    return ChoiceConfigField(
        name='endpoint',
        display_name=u'Endpoint',
        value=endpoints[0].name,
        choices=tuple(ConfigFieldChoice(
            value=endpoint.name,
            display_text=endpoint.display_name,
            sub_fields=tuple(_create_field_config_from_data_source(field) for field in endpoint.config_fields)
        ) for endpoint in endpoints)
    )


def _create_field_config_from_asset(field: tuple[ConfigField, DataSourceConfig]) -> ConfigField:
    (config_field, asset_data_source_config) = field
    assert config_field.name == asset_data_source_config.name
    if isinstance(config_field, StringConfigField):
        assert isinstance(asset_data_source_config, StringDataSourceConfig)
        return StringConfigField(
            name=config_field.name,
            display_name=config_field.display_name,
            value=asset_data_source_config.value,
            secret=config_field.secret,
        )
    raise UnknownConfigFieldType(config_field)


def _apply_asset_to_endpoint_config_sub_fields(
        endpoint_choice: ConfigFieldChoice,
        asset_endpoint_config: tuple[DataSourceConfig, ...]
) -> ConfigFieldChoice:
    zipped_sub_fields = zip(endpoint_choice.sub_fields, asset_endpoint_config)
    return ConfigFieldChoice(
        value=endpoint_choice.value,
        display_text=endpoint_choice.display_text,
        sub_fields=tuple(_create_field_config_from_asset(field) for field in zipped_sub_fields)
    )


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
            choices=tuple(_apply_asset_to_endpoint_config_sub_fields(choice, asset_data_source.config)
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


def _asset_endpoint_config_from_config_value(config_value: ConfigValue) -> DataSourceConfig:
    if isinstance(config_value, StringConfigValue):
        return StringDataSourceConfig(
            name=config_value.name,
            value=config_value.value,
        )
    raise UnknownConfigValueType(config_value)


def _asset_endpoint_from_config_value(
        endpoint_config_value: ChoiceConfigValue
) -> tuple[str, tuple[DataSourceConfig, ...]]:
    return (
        endpoint_config_value.value,
        tuple(_asset_endpoint_config_from_config_value(config_value)
              for config_value in endpoint_config_value.sub_values),
    )


def _asset_data_source_from_config_value(data_source_config_value: ChoiceConfigValue) -> AssetDataSource:
    endpoint_config_value = data_source_config_value.sub_values[0]
    assert isinstance(endpoint_config_value, ChoiceConfigValue)
    (endpoint_name, endpoint_config) = _asset_endpoint_from_config_value(endpoint_config_value)
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
    _data_sources: tuple[DataSource, ...]
    _store: Store[State]

    @inject
    def __init__(self, data_sources: tuple[DataSource, ...], store: Store[State]):
        self._data_sources = data_sources
        self._store = store

    def _get_data_source(self, name: str) -> DataSource:
        for data_source in self._data_sources:
            if data_source.get_name() == name:
                return data_source
        raise UnknownDataSource(name)

    def _create_data_source_choice(
            self,
            data_source_state: DataSourceInstance
    ) -> ConfigFieldChoice:
        data_source = self._get_data_source(data_source_state.type)
        return ConfigFieldChoice(
            value=data_source_state.uuid,
            display_text=data_source_state.name,
            sub_fields=(_create_endpoint_config(data_source.get_endpoints()),)
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
