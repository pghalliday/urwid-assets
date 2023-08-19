from __future__ import annotations

from datetime import datetime
from pathlib import Path

from injector import inject, ClassAssistedBuilder, singleton
from urwid import WidgetWrap, Edit, Columns, Text, IntEdit, WidgetPlaceholder, Pile, connect_signal, CheckBox
from urwid.numedit import FloatEdit

from urwid_assets.ui.widgets.choice import Choice, DropDownChoice
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import StringConfigField, DecimalConfigField, \
    IntegerConfigField, ChoiceConfigField, DateTimeConfigField, PathConfigField, ConfigFieldVisitor, CheckBoxConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue, \
    DecimalConfigValue, IntegerConfigValue, ChoiceConfigValue, DateTimeConfigValue, PathConfigValue, CheckBoxConfigValue


class ConfigEdit(WidgetWrap):
    def get_value(self) -> ConfigValue:
        pass


class StringConfigEdit(ConfigEdit):
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


class DecimalConfigEdit(ConfigEdit):
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


class IntegerConfigEdit(ConfigEdit):
    def __init__(self, config_field: IntegerConfigField, caption_column_width: int):
        self._name = config_field.name
        self._int_edit = IntEdit(default=config_field.value)
        super().__init__(Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._int_edit,
        )))

    def get_value(self) -> ConfigValue:
        return IntegerConfigValue(self._name, self._int_edit.value())


class CheckBoxConfigEdit(ConfigEdit):
    @inject
    def __init__(self,
                 edit_visitor_builder: ClassAssistedBuilder[EditVisitor],
                 config_field: CheckBoxConfigField,
                 caption_column_width: int):
        edit_visitor = edit_visitor_builder.build(caption_column_width=caption_column_width)
        self._name = config_field.name
        self._check_box = CheckBox('', config_field.value)
        connect_signal(self._check_box, 'change', self._on_change)
        self._check_box_columns = Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._check_box,
        ))
        self._sub_edits = tuple(field.visit(edit_visitor)
                                for field in config_field.sub_fields)
        self._widget_placeholder = WidgetPlaceholder(self._create_pile(config_field.value))
        super().__init__(self._widget_placeholder)

    def _create_pile(self, checked: bool) -> Pile:
        if checked:
            return Pile((
                            self._check_box_columns,
                        ) + self._sub_edits)
        return Pile((
            self._check_box_columns,
        ))

    def _on_change(self, _, value: bool) -> None:
        self._widget_placeholder.original_widget = self._create_pile(value)

    def get_value(self) -> ConfigValue:
        value = self._check_box.get_state()
        return CheckBoxConfigValue(
            self._name,
            value,
            tuple(edit.get_value() for edit in self._sub_edits) if value else None
        )


class ChoiceConfigEdit(ConfigEdit):
    @inject
    def __init__(self,
                 choice_builder: ClassAssistedBuilder[Choice],
                 edit_visitor_builder: ClassAssistedBuilder[EditVisitor],
                 config_field: ChoiceConfigField,
                 caption_column_width: int):
        edit_visitor = edit_visitor_builder.build(caption_column_width=caption_column_width)
        selected = tuple(choice.value for choice in config_field.choices).index(config_field.value)
        self._name = config_field.name
        self._choice = choice_builder.build(title=config_field.display_name,
                                            choices=tuple(DropDownChoice(choice.display_text, choice.value)
                                                          for choice in config_field.choices),
                                            selected=selected)
        self._sub_edits = tuple(tuple(field.visit(edit_visitor)
                                      for field in choice.sub_fields)
                                for choice in config_field.choices)
        self._widget_placeholder = WidgetPlaceholder(Pile(self._sub_edits[selected]))
        connect_signal(self._choice, 'select', self._on_select)
        super().__init__(Pile([
            Columns((
                (caption_column_width, Text(config_field.display_name)),
                (2, Text(u': ')),
                self._choice,
            )),
            self._widget_placeholder
        ]))

    def _on_select(self, _, selected: int) -> None:
        self._widget_placeholder.original_widget = Pile(self._sub_edits[selected])

    def get_value(self) -> ConfigValue:
        return ChoiceConfigValue(
            self._name,
            self._choice.get_value(),
            tuple(edit.get_value() for edit in self._sub_edits[self._choice.get_selected()])
        )


class DateTimeConfigEdit(ConfigEdit):
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


class PathConfigEdit(ConfigEdit):
    def __init__(self, config_field: PathConfigField, caption_column_width: int):
        self._name = config_field.name
        self._edit = Edit(edit_text=str(config_field.value))
        super().__init__(Columns((
            (caption_column_width, Text(config_field.display_name)),
            (2, Text(u': ')),
            self._edit,
        )))

    def get_value(self) -> ConfigValue:
        return PathConfigValue(self._name, Path(self._edit.get_edit_text()))


@singleton
class EditVisitor(ConfigFieldVisitor[ConfigEdit]):
    @inject
    def __init__(self,
                 choice_config_edit_builder: ClassAssistedBuilder[ChoiceConfigEdit],
                 check_box_config_edit_builder: ClassAssistedBuilder[CheckBoxConfigEdit],
                 caption_column_width: int):
        self._choice_config_edit_builder = choice_config_edit_builder
        self._check_box_config_edit_builder = check_box_config_edit_builder
        self._caption_column_width = caption_column_width

    def do_string(self, config_field: StringConfigField) -> StringConfigEdit:
        return StringConfigEdit(config_field, self._caption_column_width)

    def do_decimal(self, config_field: DecimalConfigField) -> DecimalConfigEdit:
        return DecimalConfigEdit(config_field, self._caption_column_width)

    def do_integer(self, config_field: IntegerConfigField) -> IntegerConfigEdit:
        return IntegerConfigEdit(config_field, self._caption_column_width)

    def do_choice(self, config_field: ChoiceConfigField) -> ChoiceConfigEdit:
        return self._choice_config_edit_builder.build(config_field=config_field,
                                                      caption_column_width=self._caption_column_width)

    def do_check_box(self, config_field: CheckBoxConfigField) -> ChoiceConfigEdit:
        return self._check_box_config_edit_builder.build(config_field=config_field,
                                                         caption_column_width=self._caption_column_width)

    def do_date_time(self, config_field: DateTimeConfigField) -> DateTimeConfigEdit:
        return DateTimeConfigEdit(config_field, self._caption_column_width)

    def do_path(self, config_field: PathConfigField) -> PathConfigEdit:
        return PathConfigEdit(config_field, self._caption_column_width)
