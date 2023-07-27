from typing import Any
from typing import Callable

import urwid

WidgetGenerator = Callable[[Any], urwid.Widget]


class UIManager(urwid.WidgetPlaceholder):
    def __init__(self) -> None:
        super().__init__(urwid.SolidFill(u'#'))
        self.view_generators = {}

    def register_view(self, name: str, view_generator: WidgetGenerator):
        self.view_generators[name] = view_generator

    def switch_to_view(self, name: str, data: Any):
        self.original_widget = self.view_generators[name](data)
