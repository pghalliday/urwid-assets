from pathlib import Path

from commands.ui.widgets.dialogs.config_dialog import ConfigField, ConfigValue, \
    PathConfigField, PathConfigValue


def get_csv_export_path(config_values: tuple[ConfigValue, ...]) -> Path:
    output_file = config_values[0]
    assert isinstance(output_file, PathConfigValue)
    return output_file.value


def create_export_csv_dialog_config(output_file: Path) -> tuple[ConfigField, ...]:
    return (
        PathConfigField(
            name='output_file',
            display_name=u'Output file',
            value=output_file,
        ),
    )
