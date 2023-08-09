from dataclasses import dataclass

from urwid import WidgetPlaceholder

from lib.widgets.views.view import View


@dataclass(frozen=True)
class Column:
    weight: int
    view: View


class PlaceholderView(View):
    _placeholder: WidgetPlaceholder
    _view: View
    _active: bool = False

    def __init__(self, initial_view: View):
        self._view = initial_view
        self._placeholder = WidgetPlaceholder(initial_view)
        super().__init__(self._placeholder)

    def activate(self) -> None:
        self._active = True
        self._view.activate()

    def deactivate(self) -> None:
        self._view.deactivate()
        self._active = False

    def set_view(self, view: View) -> None:
        self._view.deactivate()
        self._placeholder.original_widget = view
        self._view = view
        if self._active:
            self._view.activate()
