from urwid import Text, Divider, Columns, Button, Pile

from lib.widgets.view import View


class MessageBox(View):
    signals = [
        'ok',
        'cancel',
    ]

    def __init__(self,
                 title: str,
                 message: str) -> None:
        buttons = Columns([
            Text(u''),
            Button(u'Ok', self._ok),
            Button(u'Cancel', self._cancel),
        ])
        super().__init__(Pile([
            Text(title),
            Divider(u'-'),
            Text(message),
            Divider(u'-'),
            buttons
        ]))
        buttons.set_focus_column(2)

    def _ok(self, _):
        self._emit('ok')

    def _cancel(self, _):
        self._emit('cancel')
