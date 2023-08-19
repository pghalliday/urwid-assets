from dataclasses import replace
from uuid import UUID

from injector import singleton, inject

from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField, DataSourceConfig, \
    StringDataSourceConfig, DataSourceEndpoint
from urwid_assets.lib.redux.store import Store
from urwid_assets.selectors.selectors import select_data_sources
from urwid_assets.state.saved.data_sources.data_sources import DataSourceInstance
from urwid_assets.state.state import State
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField, \
    ChoiceConfigField, ConfigFieldChoice
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue, ChoiceConfigValue


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


def create_field_config_from_data_source(field: DataSourceConfigField) -> ConfigField:
    if isinstance(field, StringDataSourceConfigField):
        return StringConfigField(
            name=field.name,
            display_name=field.display_name,
            value=field.default,
            secret=field.secret,
        )
    raise UnknownDataSourceConfigFieldType(field)


def create_endpoint_config(endpoints: tuple[DataSourceEndpoint, ...]) -> ChoiceConfigField:
    return ChoiceConfigField(
        name='endpoint',
        display_name=u'Endpoint',
        value=endpoints[0].name,
        choices=tuple(ConfigFieldChoice(
            value=endpoint.name,
            display_text=endpoint.display_name,
            sub_fields=tuple(create_field_config_from_data_source(field) for field in endpoint.config_fields)
        ) for endpoint in endpoints)
    )


def apply_data_source_config(field: tuple[ConfigField, DataSourceConfig]) -> ConfigField:
    (config_field, data_source_config) = field
    assert config_field.name == data_source_config.name
    if isinstance(config_field, StringConfigField):
        assert isinstance(data_source_config, StringDataSourceConfig)
        return replace(config_field, value=data_source_config.value)
    raise UnknownConfigFieldType(config_field)


def apply_data_source_config_choice(
        choice: ConfigFieldChoice,
        config: tuple[DataSourceConfig, ...]
) -> ConfigFieldChoice:
    zipped_sub_fields = zip(choice.sub_fields, config)
    return replace(choice,
                   sub_fields=tuple(apply_data_source_config(field) for field in zipped_sub_fields))


def apply_endpoint(data_source_choice: ConfigFieldChoice,
                   endpoint: str,
                   config: tuple[DataSourceConfig, ...]) -> ConfigFieldChoice:
    endpoint_config = data_source_choice.sub_fields[0]
    assert isinstance(endpoint_config, ChoiceConfigField)
    return replace(data_source_choice,
                   sub_fields=(replace(endpoint_config,
                                       value=endpoint,
                                       choices=tuple(apply_data_source_config_choice(choice, config)
                                                     if endpoint == choice.value else choice
                                                     for choice in endpoint_config.choices)),))


def apply_data_source(data_source_config: ChoiceConfigField,
                      data_source: UUID,
                      endpoint: str,
                      config: tuple[DataSourceConfig, ...]) -> ChoiceConfigField:
    return replace(data_source_config,
                   value=data_source,
                   choices=tuple(apply_endpoint(choice, endpoint, config)
                                 if data_source == choice.value else choice
                                 for choice in data_source_config.choices))


def data_source_config_from_value(config_value: ConfigValue) -> DataSourceConfig:
    if isinstance(config_value, StringConfigValue):
        return StringDataSourceConfig(
            name=config_value.name,
            value=config_value.value,
        )
    raise UnknownConfigValueType(config_value)


def _data_source_config_from_choice(
        config_value: ChoiceConfigValue
) -> tuple[str, tuple[DataSourceConfig, ...]]:
    return (
        config_value.value,
        tuple(data_source_config_from_value(config_value)
              for config_value in config_value.sub_values),
    )


def data_source_from_config_value(
        data_source_config_value: ChoiceConfigValue
) -> tuple[UUID, str, tuple[DataSourceConfig, ...]]:
    endpoint_config_value = data_source_config_value.sub_values[0]
    assert isinstance(endpoint_config_value, ChoiceConfigValue)
    (endpoint_name, endpoint_config) = _data_source_config_from_choice(endpoint_config_value)
    return (
        data_source_config_value.value,
        endpoint_name,
        endpoint_config,
    )


@singleton
class DataSourceConfigFactory:
    @inject
    def __init__(self, data_source_registry: DataSourceRegistry, store: Store[State]):
        self._data_source_registry = data_source_registry
        self._store = store

    def _create_data_source_choice(
            self,
            data_source_instance: DataSourceInstance
    ) -> ConfigFieldChoice:
        data_source = self._data_source_registry.get_data_source(data_source_instance.type)
        return ConfigFieldChoice(
            value=data_source_instance.uuid,
            display_text=data_source_instance.name,
            sub_fields=(create_endpoint_config(data_source.get_endpoints()),)
        )

    def create_data_source_config(self, name: str, display_name: str) -> ChoiceConfigField:
        data_sources = select_data_sources(self._store.get_state())
        return ChoiceConfigField(
            name=name,
            display_name=display_name,
            value=data_sources[0].uuid,
            choices=tuple(self._create_data_source_choice(data_source) for data_source in data_sources)
        )
