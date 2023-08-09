from uuid import UUID

from injector import inject, singleton

import state.data_sources
from lib.data_source import DataSourceConfigField, StringDataSourceConfigField, DataSource
from lib.widgets.dialogs.config_dialog import StringConfigField, ConfigField, ChoiceConfigField, ConfigFieldChoice, \
    ConfigValue, StringConfigValue, ChoiceConfigValue


class UnknownDataSourceConfigFieldType(Exception):
    field: DataSourceConfigField

    def __init__(self, field: DataSourceConfigField):
        super().__init__()
        self.field = field


class UnknownConfigFieldType(Exception):
    field: ConfigField

    def __init__(self, field: ConfigField):
        super().__init__()
        self.field = field


class UnknownConfigValueType(Exception):
    value: ConfigValue

    def __init__(self, value: ConfigValue):
        super().__init__()
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


def _create_field_config_from_config(
        field: tuple[ConfigField, state.data_sources.DataSourceConfigField]
) -> ConfigField:
    (config_field, data_source_config_field) = field
    assert config_field.name == data_source_config_field.name
    if isinstance(config_field, StringConfigField):
        assert isinstance(data_source_config_field, state.data_sources.StringDataSourceConfigField)
        return StringConfigField(
            name=config_field.name,
            display_name=config_field.display_name,
            value=data_source_config_field.value,
            secret=config_field.secret,
        )
    raise UnknownConfigFieldType(config_field)


def _apply_data_source_to_config_sub_fields(
        endpoint_choice: ConfigFieldChoice,
        config: tuple[state.data_sources.DataSourceConfigField, ...],
) -> ConfigFieldChoice:
    zipped_sub_fields = zip(endpoint_choice.sub_fields, config)
    return ConfigFieldChoice(
        value=endpoint_choice.value,
        display_text=endpoint_choice.display_text,
        sub_fields=tuple(_create_field_config_from_config(field) for field in zipped_sub_fields)
    )


def apply_data_source_to_data_source_dialog_config(
        data_source_dialog_config: tuple[ConfigField, ...],
        data_source: state.data_sources.DataSource,
) -> tuple[ConfigField, ...]:
    name_config = data_source_dialog_config[0]
    type_config = data_source_dialog_config[1]
    assert isinstance(type_config, ChoiceConfigField)
    return (
        StringConfigField(name_config.name, name_config.display_name, data_source.name),
        ChoiceConfigField(
            name=data_source_dialog_config[1].name,
            display_name=data_source_dialog_config[1].display_name,
            value=data_source.type,
            choices=tuple(_apply_data_source_to_config_sub_fields(choice, data_source.config)
                          if data_source.type == choice.value else choice
                          for choice in type_config.choices),
        ),

    )


def _data_source_config_field_from_config_value(
        config_value: ConfigValue
) -> state.data_sources.DataSourceConfigField:
    if isinstance(config_value, StringConfigValue):
        return state.data_sources.StringDataSourceConfigField(
            name=config_value.name,
            value=config_value.value,
        )
    raise UnknownConfigValueType(config_value)


def data_source_from_config_values(
        uuid: UUID,
        config_values: tuple[ConfigValue, ...]
) -> state.data_sources.DataSource:
    name_config_value = config_values[0]
    assert isinstance(name_config_value, StringConfigValue)
    type_config_value = config_values[1]
    assert isinstance(type_config_value, ChoiceConfigValue)
    return state.data_sources.DataSource(
        uuid=uuid,
        name=name_config_value.value,
        type=type_config_value.value,
        config=tuple(_data_source_config_field_from_config_value(config_value)
                     for config_value in type_config_value.sub_values),
    )


@singleton
class DefaultDataSourceDialogConfigFactory:
    _data_sources: tuple[DataSource, ...]

    @inject
    def __init__(self, data_sources: tuple[DataSource, ...]):
        self._data_sources = data_sources

    def _create_data_source_config(self) -> ChoiceConfigField:
        return ChoiceConfigField(
            name='type',
            display_name=u'Type',
            value=self._data_sources[0].get_name(),
            choices=tuple(ConfigFieldChoice(
                data_source.get_name(),
                data_source.get_display_name(),
                tuple(_create_field_config_from_data_source(field)
                      for field in data_source.get_global_config_fields())
            ) for data_source in self._data_sources)
        )

    def create(self) -> tuple[ConfigField, ...]:
        return (
            StringConfigField('name', u'Name', u'New data source'),
            self._create_data_source_config(),
        )
