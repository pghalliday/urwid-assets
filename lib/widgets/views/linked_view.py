from urwid import Widget

from lib.redux.store import Store, Unsubscribe
from lib.widgets.views.view import View


class LinkedView(View):
    _store: Store
    _unsubscribe: Unsubscribe
    _active: bool = False

    def __init__(self, widget: Widget, store: Store):
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
