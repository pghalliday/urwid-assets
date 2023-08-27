from typing import TypeVar, Callable

from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, ConfigFieldVisitor, \
    DecimalConfigField, StringConfigField, IntegerConfigField, ChoiceConfigField, DateTimeConfigField, PathConfigField, \
    CheckBoxConfigField

T = TypeVar('T')


class DefaultConfigFieldVisitor(ConfigFieldVisitor[T]):
    def __init__(self, default_callback: Callable[[ConfigField], T]):
        self._default_callback = default_callback

    def do_string(self, config_field: StringConfigField) -> T:
        return self._default_callback(config_field)

    def do_decimal(self, config_field: DecimalConfigField) -> T:
        return self._default_callback(config_field)

    def do_integer(self, config_field: IntegerConfigField) -> T:
        return self._default_callback(config_field)

    def do_choice(self, config_field: ChoiceConfigField) -> T:
        return self._default_callback(config_field)

    def do_check_box(self, config_field: CheckBoxConfigField) -> T:
        return self._default_callback(config_field)

    def do_date_time(self, config_field: DateTimeConfigField) -> T:
        return self._default_callback(config_field)

    def do_path(self, config_field: PathConfigField) -> T:
        return self._default_callback(config_field)
