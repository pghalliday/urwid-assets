from urwid import ListBox, SimpleFocusListWalker, AttrMap

from commands.ui.widgets.selectable_text import SelectableText


class TextList(ListBox):
    def __init__(self):
        self._list_walker = SimpleFocusListWalker([])
        super().__init__(self._list_walker)

    def append(self, text: str):
        self._list_walker.append(AttrMap(SelectableText(text), None, 'reversed'))
        self._list_walker.set_focus(len(self._list_walker) - 1)

    def get_selected_text(self) -> str:
        if self._list_walker.focus >= 0:
            return self._list_walker[self._list_walker.focus].original_widget.text
        return u''
