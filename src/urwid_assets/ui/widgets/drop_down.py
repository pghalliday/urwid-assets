import logging
from dataclasses import dataclass
from typing import Any

from urwid import PopUpLauncher, Button, ListBox, AttrMap, WidgetWrap, LineBox, SimpleFocusListWalker, connect_signal

from urwid_assets.ui.widgets.selectable_text import SelectableText

LOGGER = logging.getLogger(__name__)


def _create_choice(choice: str):
    return AttrMap(SelectableText(choice), None, focus_map='reversed')


class _PopUp(WidgetWrap):
    signals = ['select']

    def __init__(self, choices: tuple[str, ...], selected: int):
        self._list_walker = SimpleFocusListWalker([_create_choice(choice) for choice in choices])
        self._list_walker.set_focus(selected)
        super().__init__(LineBox(ListBox(self._list_walker)))

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('enter', ' '):
            self._emit('select', self._list_walker.focus)


@dataclass(frozen=True)
class DropDownChoice:
    text: str
    value: Any


class DropDown(PopUpLauncher):
    signals = ['select']

    def __init__(self, choices: tuple[DropDownChoice, ...], selected: int) -> None:
        self._choices = choices
        self._selected = selected
        self._button = Button(self._choices[selected].text)
        connect_signal(self._button, 'click', lambda _: self.open_pop_up())
        super().__init__(self._button)

    def get_selected(self) -> int:
        return self._selected

    def get_value(self) -> Any:
        return self._choices[self._selected].value

    def create_pop_up(self):
        pop_up = _PopUp(tuple(choice.text for choice in self._choices), self._selected)
        connect_signal(pop_up, 'select', self._select)
        return pop_up

    def _select(self, _, selected: int) -> None:
        self.close_pop_up()
        self._selected = selected
        self._button.set_label(self._choices[selected].text)
        self._emit('select', selected)

    def get_pop_up_parameters(self):
        return {
            'left': 1,
            'top': -1,
            'overlay_width': self._calculate_pop_up_width(),
            'overlay_height': self._calculate_pop_up_height(),
        }

    def _calculate_pop_up_width(self) -> int:
        return 2 + max(tuple(len(choice.text) for choice in self._choices))

    def _calculate_pop_up_height(self) -> int:
        return 2 + len(self._choices)
