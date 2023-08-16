import functools
import logging
from typing import TypeVar, Type

_LOGGER = logging.getLogger(__name__)

T = TypeVar('T')


def selectable(cls: Type[T]) -> Type[T]:
    @functools.wraps(cls, updated=tuple())
    class Wrapped(cls):
        _selectable = True

        def keypress(self, _size: int, key: str) -> str:
            return key

        def mouse_event(self, _size: int, event: str, button: int, _col: int, _row: int, _focus: bool) -> bool:
            return False

    return Wrapped
