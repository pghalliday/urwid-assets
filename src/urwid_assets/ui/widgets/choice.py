import logging
from dataclasses import dataclass
from typing import Any

from injector import inject
from urwid import Button, WidgetWrap, connect_signal

from urwid_assets.ui.widgets.dialogs.list_dialog import ListDialog
from urwid_assets.ui.widgets.views.view_manager import ViewManager

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DropDownChoice:
    text: str
    value: Any


class Choice(WidgetWrap):
    signals = ['select']

    @inject
    def __init__(self,
                 view_manager: ViewManager,
                 title: str,
                 choices: tuple[DropDownChoice, ...],
                 selected: int) -> None:
        self._view_manager = view_manager
        self._title = title
        self._choices = choices
        self._selected = selected
        self._button = Button(self._choices[selected].text)
        connect_signal(self._button, 'click', self._get_choice)
        super().__init__(self._button)

    def get_selected(self) -> int:
        return self._selected

    def get_value(self) -> Any:
        return self._choices[self._selected].value

    def _get_choice(self, _):
        choice_dialog = ListDialog(title=self._title,
                                   entries=tuple(choice.text for choice in self._choices),
                                   selected=self._selected)
        connect_signal(choice_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(choice_dialog, 'select', self._select)
        self._view_manager.open_dialog(dialog=choice_dialog,
                                       height=('relative', 60))

    def _select(self, _, selected: int) -> None:
        self._view_manager.close_dialog()
        self._selected = selected
        self._button.set_label(self._choices[selected].text)
        self._emit('select', selected)
