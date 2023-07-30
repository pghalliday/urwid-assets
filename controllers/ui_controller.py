from injector import singleton
from urwid import Widget, WidgetPlaceholder, Overlay, SolidFill, LineBox


@singleton
class UIController(WidgetPlaceholder):
    def __init__(self) -> None:
        super().__init__(SolidFill(u'#'))

    def set_view(self, view: Widget):
        self.original_widget = view

    def open_dialog(self, dialog: Widget):
        self.original_widget = Overlay(LineBox(dialog),
                                       self.original_widget,
                                       align='center', width=('relative', 50),
                                       valign='middle', height=('relative', 50))

    def close_dialog(self):
        self.original_widget = self.original_widget[0]
