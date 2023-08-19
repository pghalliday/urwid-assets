from uuid import UUID

from urwid_assets.state.saved.symbols.symbols import Symbol
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue


def symbol_from_config_values(uuid: UUID,
                              config_values: tuple[ConfigValue, ...]) -> Symbol:
    name = config_values[0]
    assert isinstance(name, StringConfigValue)
    return Symbol(
        uuid=uuid,
        name=name.value,
    )


def create_symbol_dialog_config(name: str) -> tuple[ConfigField, ...]:
    return (
        StringConfigField(
            name='name',
            display_name=u'Name',
            value=name,
        ),
    )
