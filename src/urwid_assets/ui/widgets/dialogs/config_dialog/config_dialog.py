from __future__ import annotations

from injector import inject, ClassAssistedBuilder, singleton
from urwid import Text, Divider, Columns, Button, Pile

from urwid_assets.ui.widgets.dialogs.config_dialog.config_edit import EditVisitor
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, ChoiceConfigField, \
    CheckBoxConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.default_config_field_visitor import DefaultConfigFieldVisitor
from urwid_assets.ui.widgets.views.view import View


class ConfigDialog(View):
    signals = [
        'ok',
        'cancel',
    ]

    @inject
    def __init__(self,
                 caption_width_visitor: CaptionWidthVisitor,
                 edit_visitor_builder: ClassAssistedBuilder[EditVisitor],
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
        caption_column_width = max(config_field.visit(caption_width_visitor) for config_field in config_fields)
        edit_visitor = edit_visitor_builder.build(caption_column_width=caption_column_width)
        self._edits = tuple(config_field.visit(edit_visitor) for config_field in config_fields)
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


@singleton
class CaptionWidthVisitor(DefaultConfigFieldVisitor[int]):
    def __init__(self):
        super().__init__(lambda config_field: len(config_field.display_name))

    def do_choice(self, config_field: ChoiceConfigField) -> int:
        return max(
            len(config_field.display_name),
            max(max(field.visit(self)
                    for field in choice.sub_fields) if len(choice.sub_fields) > 0 else 0
                for choice in config_field.choices)
        )

    def do_check_box(self, config_field: CheckBoxConfigField) -> int:
        return max(
            len(config_field.display_name),
            max(field.visit(self)
                for field in config_field.sub_fields) if len(config_field.sub_fields) > 0 else 0,
        )
