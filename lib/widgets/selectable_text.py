from urwid import Text


class SelectableText(Text):
    _selectable = True

    def __init__(self, text: str):
        super().__init__(text)

    def keypress(self, _size: int, key: str) -> str:
        return key

    def mouse_event(self, _size: int, event: str, button: int, _col: int, _row: int, _focus: bool) -> bool:
        return False
