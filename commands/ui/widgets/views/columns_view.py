from dataclasses import dataclass

from urwid import Columns

from commands.ui.widgets.views.view import View


@dataclass(frozen=True)
class Column:
    weight: int
    view: View


class ColumnsView(View):
    def __init__(self, columns: tuple[Column, ...]):
        self._columns = columns
        super().__init__(Columns([('weight', column.weight, column.view)
                                  for column in self._columns]))

    def activate(self) -> None:
        for column in self._columns:
            column.view.activate()

    def deactivate(self) -> None:
        for column in self._columns:
            column.view.deactivate()
