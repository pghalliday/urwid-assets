from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class KeyHandler:
    keys: tuple[str, ...]
    handler: Callable[[], None]


def keys(handlers: tuple[KeyHandler, ...]) -> Callable[[str], str | None]:
    def keypress(key: str) -> str | None:
        for handler in handlers:
            if key in handler.keys:
                handler.handler()
                return None
        return key

    return keypress
