from datetime import datetime

from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, DateTimeConfigField, \
    CheckBoxConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, DateTimeConfigValue, \
    CheckBoxConfigValue


def timestamp_from_config_values(config_values: tuple[ConfigValue, ...]) -> datetime | None:
    use_timestamp_value = config_values[0]
    assert isinstance(use_timestamp_value, CheckBoxConfigValue)
    use_timestamp = use_timestamp_value.value
    if use_timestamp:
        timestamp_value = use_timestamp_value.sub_values[0]
        assert isinstance(timestamp_value, DateTimeConfigValue)
        return timestamp_value.value
    return None


def create_timestamp_dialog_config(timestamp: datetime | None) -> tuple[ConfigField, ...]:
    return (
        CheckBoxConfigField(
            name='use_timestamp',
            display_name='Use timestamp',
            value=timestamp is not None,
            sub_fields=(
                DateTimeConfigField(
                    name='timestamp',
                    display_name=u'Timestamp',
                    value=datetime.now() if timestamp is None else timestamp,
                ),
            ),
        ),
    )
