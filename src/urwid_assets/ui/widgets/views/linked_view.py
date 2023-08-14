from urwid import Widget

from urwid_assets.ui.widgets.views.view import View
from urwid_assets.lib.redux.store import Store, Unsubscribe


class LinkedView(View):
    def __init__(self, widget: Widget, store: Store):
        self._active: bool = False
        self._unsubscribe: Unsubscribe | None = None
        super().__init__(widget)
        self._store = store

    def activate(self) -> None:
        if not self._active:
            self._active = True
            self._unsubscribe = self._store.subscribe(self._update)
            self._update()

    def deactivate(self) -> None:
        if self._active:
            self._unsubscribe()
            self._active = False

    def _update(self) -> None:
        pass
