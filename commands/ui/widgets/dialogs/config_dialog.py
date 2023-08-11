from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from urwid import Text, Divider, Columns, Button, Pile, Edit, WidgetWrap, connect_signal, WidgetPlaceholder
from urwid.numedit import FloatEdit

from commands.ui.widgets.drop_down import DropDown, DropDownChoice
from commands.ui.widgets.views.view import View


@dataclass(frozen=True)
class ConfigFieldChoice:
    value: Any
    display_text: str
    sub_fields: tuple[ConfigField, ...]


@dataclass(frozen=True)
class ConfigField:
    name: str
    display_name: str

    def get_edit(self, caption_column_width: int) -> _ConfigEdit:
        pass

    def get_caption_width(self) -> int:
        pass


@dataclass(frozen=True)
class StringConfigField(ConfigField):
    value: str
    secret: bool = False

    def get_edit(self, caption_column_width: int) -> _StringConfigEdit:
        return _StringConfigEdit(self, caption_column_width)

    def get_caption_width(self) -> int:
        return len(self.display_name)


@dataclass(frozen=True)
class DecimalConfigField(ConfigField):
    value: Decimal

    def get_edit(self, caption_column_width: int) -> _DecimalConfigEdit:
        return _DecimalConfigEdit(self, caption_column_width)

    def get_caption_width(self) -> int:
        return len(self.display_name)


@dataclass(frozen=True)
class ChoiceConfigField(ConfigField):
    value: Any
    choices: tuple[ConfigFieldChoice, ...]

    def get_edit(self, caption_column_width: int) -> _ChoiceConfigEdit:
        return _ChoiceConfigEdit(self, caption_column_width)

    def get_caption_width(self) -> int:
        return max(len(self.display_name), max(tuple(max(field.get_caption_width()
                                                         for field in choice.sub_fields)
                                                     for choice in self.choices)))


@dataclass(frozen=True)
class DateTimeConfigField(ConfigField):
    value: datetime

    def get_edit(self, caption_column_width: int) -> _DateTimeConfigEdit:
        return _DateTimeConfigEdit(self, caption_column_width)

    def get_caption_width(self) -> int:
        return len(self.display_name)


class _ConfigEdit(WidgetWrap):
    def get_value(self) -> ConfigValue:
        pass


class _StringConfigEdit(_ConfigEdit):
    def __init__(self, config_field: StringConfigField, caption_column_width: int):
        self._name = config_field.name
        self._edit = Edit(edit_text=config_field.value, mask=u'*' if config_field.secret else None)
        super().__init__(Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._edit,
        )))

    def get_value(self) -> ConfigValue:
        return StringConfigValue(self._name, self._edit.get_edit_text())


class _DecimalConfigEdit(_ConfigEdit):
    def __init__(self, config_field: DecimalConfigField, caption_column_width: int):
        self._name = config_field.name
        self._float_edit = FloatEdit(default=config_field.value)
        super().__init__(Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._float_edit,
        )))

    def get_value(self) -> ConfigValue:
        return DecimalConfigValue(self._name, self._float_edit.value())


class _ChoiceConfigEdit(_ConfigEdit):
    def __init__(self, config_field: ChoiceConfigField, caption_column_width: int):
        selected = tuple(choice.value for choice in config_field.choices).index(config_field.value)
        self._name = config_field.name
        self._drop_down = DropDown(choices=tuple(DropDownChoice(choice.display_text, choice.value)
                                                 for choice in config_field.choices),
                                   selected=selected)
        self._sub_edits = tuple(tuple(field.get_edit(caption_column_width)
                                      for field in choice.sub_fields)
                                for choice in config_field.choices)
        self._widget_placeholder = WidgetPlaceholder(Pile(self._sub_edits[selected]))
        connect_signal(self._drop_down, 'select', self._on_select)
        super().__init__(Pile([
            Columns((
                (caption_column_width, Text(config_field.display_name)),
                (2, Text(u': ')),
                self._drop_down,
            )),
            self._widget_placeholder
        ]))

    def _on_select(self, _, selected: int) -> None:
        self._widget_placeholder.original_widget = Pile(self._sub_edits[selected])

    def get_value(self) -> ConfigValue:
        return ChoiceConfigValue(
            self._name,
            self._drop_down.get_value(),
            tuple(edit.get_value() for edit in self._sub_edits[self._drop_down.get_selected()])
        )


class _DateTimeConfigEdit(_ConfigEdit):
    def __init__(self, config_field: DateTimeConfigField, caption_column_width: int):
        self._name = config_field.name
        self._edit = Edit(edit_text=config_field.value.isoformat())
        super().__init__(Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._edit,
        )))

    def get_value(self) -> ConfigValue:
        return DateTimeConfigValue(self._name, datetime.fromisoformat(self._edit.get_edit_text()))


@dataclass(frozen=True)
class ConfigValue:
    name: str


@dataclass(frozen=True)
class StringConfigValue(ConfigValue):
    value: str


@dataclass(frozen=True)
class DecimalConfigValue(ConfigValue):
    value: Decimal


@dataclass(frozen=True)
class ChoiceConfigValue(ConfigValue):
    value: Any
    sub_values: tuple[ConfigValue, ...]


@dataclass(frozen=True)
class DateTimeConfigValue(ConfigValue):
    value: datetime


class ConfigDialog(View):
    signals = [
        'ok',
        'cancel',
    ]

    def __init__(self,
                 title: str,
                 config_fields: tuple[ConfigField, ...],
                 message: str | None = None, ) -> None:
        buttons = Columns([
            Text(u''),
            Button(u'Ok', self._ok),
            Button(u'Cancel', self._cancel),
        ])
        message_widgets = tuple() if message is None else (
            Text(message),
            Text(u''),
        )
        caption_column_width = max(config_field.get_caption_width() for config_field in config_fields)
        self._edits = tuple(config_field.get_edit(caption_column_width) for config_field in config_fields)
        super().__init__(Pile((
                                  Text(title),
                                  Divider(u'-'),
                              ) + message_widgets + self._edits + (
                                  Divider(u'-'),
                                  buttons
                              )))

    def _ok(self, _):
        values = tuple(edit.get_value() for edit in self._edits)
        self._emit('ok', values)

    def _cancel(self, _):
        self._emit('cancel')
