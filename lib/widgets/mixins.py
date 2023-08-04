from typing import Callable, TypeVar, Generic

CONTEXT = TypeVar('CONTEXT')
KeypressHandler = Callable[[CONTEXT, str], str | None]
MouseEventHandler = Callable[[CONTEXT, str, int], bool]


class KeyHandler(Generic[CONTEXT]):
    _keypress_handler: KeypressHandler = None

    def _do_keypress(self, context: CONTEXT, key: str) -> str | None:
        if self._keypress_handler is not None:
            return self._keypress_handler(context, key)
        return key

    def on_keypress(self, keypress_handler: KeypressHandler):
        self._keypress_handler = keypress_handler


class MouseHandler(Generic[CONTEXT]):
    _mouse_event_handler: MouseEventHandler = None

    def _do_mouse_event(self, context: CONTEXT, event: str, button: int) -> bool:
        if self._mouse_event_handler is not None:
            return self._mouse_event_handler(context, event, button)
        return False

    def on_mouse_event(self, mouse_event_handler: MouseEventHandler):
        self._mouse_event_handler = mouse_event_handler
