from lib.data_source.data_source import DataSourceConfigField, StringDataSourceConfigField, DataSource
from lib.widgets.config_dialog import StringConfigField, ConfigField, ConfigValue, StringConfigValue
from state import models


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


def _update_field_config_from_data_source(field: ConfigField, config: models.DataSourceConfigField) -> ConfigField:
    if isinstance(field, StringConfigField):
        assert isinstance(config, models.StringDataSourceConfigField)
        assert field.name == config.name
        return StringConfigField(
            name=field.name,
            display_name=field.display_name,
            value=config.value,
            secret=field.secret,
        )
    raise UnknownConfigFieldType(field)


def _create_field_config_from_data_source(field: DataSourceConfigField) -> ConfigField:
    if isinstance(field, StringDataSourceConfigField):
        return StringConfigField(
            name=field.name,
            display_name=field.display_name,
            value=field.default,
            secret=field.secret,
        )
    raise UnknownDataSourceConfigFieldType(field)


def create_data_source_dialog_config(data_source: DataSource, data_sources: tuple[models.DataSource, ...]) -> tuple[
    ConfigField, ...]:
    config_fields = tuple(
        _create_field_config_from_data_source(field) for field in data_source.get_global_config_fields())
    name = data_source.get_name()
    for data_source_config in data_sources:
        if data_source_config.name == name:
            zipped = zip(config_fields, data_source_config.config)
            config_fields = tuple(_update_field_config_from_data_source(field, config) for field, config in zipped)
            break
    return config_fields


def _data_source_config_from_config_value(config_value: ConfigValue) -> models.DataSourceConfigField:
    if isinstance(config_value, StringConfigValue):
        return models.StringDataSourceConfigField(
            name=config_value.name,
            value=config_value.value,
        )
    raise UnknownConfigValueType(config_value)


def data_source_from_config_values(name: str, config_values: tuple[ConfigValue, ...]) -> models.DataSource:
    return models.DataSource(
        name=name,
        config=tuple(_data_source_config_from_config_value(config_value) for config_value in config_values),
    )
