from urwid import WidgetPlaceholder, Overlay, LineBox

from lib.widgets.views.view import View


class ViewManager(View):
    _placeholder: WidgetPlaceholder
    _current_screen: View
    _current_dialogs: list[View] = []
    _active: bool = False

    def __init__(self, initial_screen: View) -> None:
        self._placeholder = WidgetPlaceholder(initial_screen)
        self._current_screen = initial_screen
        super().__init__(self._placeholder)

    def set_screen(self, screen: View):
        self._current_screen.deactivate()
        self._placeholder.original_widget = screen
        self._current_screen = screen
        if self._active:
            screen.activate()

    def open_dialog(self, dialog: View, height: int | str | tuple[str, int] = 'pack'):
        self._placeholder.original_widget = Overlay(
            LineBox(dialog),
            self._placeholder.original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=height,
        )
        self._current_dialogs.append(dialog)
        if self._active:
            dialog.activate()

    def close_dialog(self):
        self._current_dialogs.pop().deactivate()
        self._placeholder.original_widget = self._placeholder.original_widget[0]

    def _update(self) -> None:
        pass

    def activate(self) -> None:
        self._active = True
        self._current_screen.activate()
        for dialog in self._current_dialogs:
            dialog.activate()

    def deactivate(self) -> None:
        for dialog in self._current_dialogs:
            dialog.deactivate()
        self._current_screen.deactivate()
        self._active = False
