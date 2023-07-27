import urwid


class UIManager(urwid.WidgetPlaceholder):
    def __init__(self) -> None:
        super().__init__(urwid.SolidFill(u'#'))
        self.views = {}

    def register_view(self, name: str, view: urwid.Widget):
        self.views[name] = view

    def switch_to_view(self, name: str):
        self.original_widget = self.views[name]
