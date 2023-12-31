import logging

from urwid import Text, Divider, Columns, Button, Pile, ListBox, SimpleFocusListWalker, AttrMap, connect_signal, Frame

from urwid_assets.ui.widgets.selectable_text import SelectableText
from urwid_assets.ui.widgets.views.view import View

LOGGER = logging.getLogger()


class _SimpleList(ListBox):
    signals = [
        'select',
    ]

    def __init__(self, entries: tuple[str, ...], selected: int):
        self._list_walker = SimpleFocusListWalker(tuple(AttrMap(SelectableText(entry), None, 'reversed')
                                                        for entry in entries))
        self._list_walker.set_focus(selected)
        super().__init__(self._list_walker)

    def keypress(self, size, key) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('enter', ' '):
            self._emit('select', self._list_walker.focus)
            return None
        return key


class _Frame(Frame):
    signals = [
        'cancel'
    ]

    def __init__(self, title: str, simple_list: _SimpleList):
        super().__init__(
            simple_list,
            Pile((
                Text(title),
                Divider(u'-'),
            )),
            Pile((
                Divider(u'-'),
                Columns((
                    Text(u''),
                    Text(u''),
                    Button(u'Cancel', lambda _: self._emit('cancel')),
                )),
            )),
        )

    def keypress(self, size, key):
        if super().keypress(size, key) is None:
            return None
        if key in ('down',) and self.focus_position == 'body':
            self.focus_position = 'footer'
            return None
        if key in ('up',) and self.focus_position == 'footer':
            self.focus_position = 'body'
            return None
        return key


class ListDialog(View):
    signals = [
        'cancel',
        'select',
    ]

    def __init__(self,
                 title: str,
                 entries: tuple[str, ...],
                 selected: int) -> None:
        self._simple_list = _SimpleList(entries, selected)
        connect_signal(self._simple_list, 'select', self._select)
        frame = _Frame(title, self._simple_list)
        connect_signal(frame, 'cancel', self._cancel)
        super().__init__(frame)

    def _cancel(self, _):
        self._emit('cancel')

    def _select(self, _, selected: int):
        self._emit('select', selected)
