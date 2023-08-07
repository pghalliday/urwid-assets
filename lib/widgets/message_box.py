from enum import Enum, auto

from urwid import Text, Divider, Columns, Button, Pile

from lib.widgets.view import View


class MessageBoxButtons(Enum):
    OK_ONLY = auto()
    OK_CANCEL = auto()


def _get_message_widget(message: str | tuple[str, ...]):
    if isinstance(message, str):
        return Text(message)
    return Pile(tuple(Text(line) for line in message))


class MessageBox(View):
    signals = [
        'ok',
        'cancel',
    ]

    def __init__(self,
                 title: str,
                 message: str | tuple[str, ...],
                 buttons: MessageBoxButtons = MessageBoxButtons.OK_ONLY) -> None:
        (button_columns, default_button) = self._button_columns(buttons)
        message = _get_message_widget(message)
        super().__init__(Pile([
            Text(title),
            Divider(u'-'),
            message,
            Divider(u'-'),
            button_columns
        ]))
        button_columns.set_focus_column(default_button)

    def _button_columns(self, buttons: MessageBoxButtons) -> (Columns, int):
        if buttons == MessageBoxButtons.OK_ONLY:
            return (Columns((
                Text(u''),
                Text(u''),
                Button(u'Ok', self._ok),
            )), 2)
        elif buttons == MessageBoxButtons.OK_CANCEL:
            return (Columns((
                Text(u''),
                Button(u'Ok', self._ok),
                Button(u'Cancel', self._cancel),
            )), 2)

    def _ok(self, _):
        self._emit('ok')

    def _cancel(self, _):
        self._emit('cancel')
