from uuid import UUID

from injector import inject, singleton

from urwid_assets.ui.views.helpers.data_source_config import create_field_config_from_data_source, \
    data_source_config_from_value, \
    apply_data_source_config_choice
from urwid_assets.ui.widgets.dialogs.config_dialog import StringConfigField, ConfigField, ChoiceConfigField, \
    ConfigFieldChoice, \
    ConfigValue, StringConfigValue, ChoiceConfigValue
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.state.data_sources.data_sources import DataSourceInstance


def apply_data_source_to_data_source_dialog_config(
        data_source_dialog_config: tuple[ConfigField, ...],
        data_source: DataSourceInstance,
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
            choices=tuple(apply_data_source_config_choice(choice, data_source.config)
                          if data_source.type == choice.value else choice
                          for choice in type_config.choices),
        ),

    )


def data_source_from_config_values(
        uuid: UUID,
        config_values: tuple[ConfigValue, ...]
) -> DataSourceInstance:
    name_config_value = config_values[0]
    assert isinstance(name_config_value, StringConfigValue)
    type_config_value = config_values[1]
    assert isinstance(type_config_value, ChoiceConfigValue)
    return DataSourceInstance(
        uuid=uuid,
        name=name_config_value.value,
        type=type_config_value.value,
        config=tuple(data_source_config_from_value(config_value)
                     for config_value in type_config_value.sub_values),
    )


@singleton
class DefaultDataSourceDialogConfigFactory:
    @inject
    def __init__(self, data_source_registry: DataSourceRegistry):
        self._data_source_registry = data_source_registry

    def _create_data_source_config(self) -> ChoiceConfigField:
        return ChoiceConfigField(
            name='type',
            display_name=u'Type',
            value=self._data_source_registry.get_data_sources()[0].get_name(),
            choices=tuple(ConfigFieldChoice(
                data_source.get_name(),
                data_source.get_display_name(),
                tuple(create_field_config_from_data_source(field)
                      for field in data_source.get_config_fields())
            ) for data_source in self._data_source_registry.get_data_sources())
        )

    def create(self) -> tuple[ConfigField, ...]:
        return (
            StringConfigField('name', u'Name', u'New data source'),
            self._create_data_source_config(),
        )
