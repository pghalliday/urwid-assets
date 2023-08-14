from urwid_assets.ui.widgets.dialogs.config_dialog import ConfigField, ConfigValue, StringConfigField, \
    ChoiceConfigField, \
    ConfigFieldChoice, StringConfigValue, ChoiceConfigValue
from urwid_assets.lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField, DataSourceConfig, \
    StringDataSourceConfig, DataSourceEndpoint


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
        return StringConfigField(
            name=config_field.name,
            display_name=config_field.display_name,
            value=data_source_config.value,
            secret=config_field.secret,
        )
    raise UnknownConfigFieldType(config_field)


def apply_data_source_config_choice(
        choice: ConfigFieldChoice,
        config: tuple[DataSourceConfig, ...]
) -> ConfigFieldChoice:
    zipped_sub_fields = zip(choice.sub_fields, config)
    return ConfigFieldChoice(
        value=choice.value,
        display_text=choice.display_text,
        sub_fields=tuple(apply_data_source_config(field) for field in zipped_sub_fields)
    )


def data_source_config_from_value(config_value: ConfigValue) -> DataSourceConfig:
    if isinstance(config_value, StringConfigValue):
        return StringDataSourceConfig(
            name=config_value.name,
            value=config_value.value,
        )
    raise UnknownConfigValueType(config_value)


def data_source_config_from_choice(
        config_value: ChoiceConfigValue
) -> tuple[str, tuple[DataSourceConfig, ...]]:
    return (
        config_value.value,
        tuple(data_source_config_from_value(config_value)
              for config_value in config_value.sub_values),
    )
