from urwid import WidgetWrap, Widget


class View(WidgetWrap):
    def __init__(self, widget: Widget):
        super().__init__(widget)

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass
