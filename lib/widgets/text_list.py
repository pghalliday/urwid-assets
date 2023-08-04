from urwid import ListBox, SimpleFocusListWalker, AttrMap

from lib.widgets.selectable_text import SelectableText


class TextList(ListBox):
    _list_walker: SimpleFocusListWalker

    def __init__(self):
        self._list_walker = SimpleFocusListWalker([])
        super().__init__(self._list_walker)

    def append(self, text: str):
        self._list_walker.append(AttrMap(SelectableText(text), None, 'reversed'))
        self._list_walker.set_focus(len(self._list_walker) - 1)
