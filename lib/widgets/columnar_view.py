from dataclasses import dataclass

from urwid import Columns

from lib.widgets.view import View


@dataclass(frozen=True)
class Column:
    weight: int
    view: View


class ColumnarView(View):
    _columns: tuple[Column, ...]
    _active: bool = False

    def __init__(self, columns: tuple[Column, ...]):
        self._columns = columns
        super().__init__(Columns([('weight', column.weight, column.view)
                                  for column in self._columns]))

    def activate(self) -> None:
        self._active = True
        for view in self._column_views:
            view.activate()

    def deactivate(self) -> None:
        for view in self._column_views:
            view.deactivate()
        self._active = False
