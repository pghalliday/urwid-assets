from injector import singleton
from urwid import Widget, WidgetPlaceholder, Overlay, SolidFill


@singleton
class UIController(WidgetPlaceholder):
    def __init__(self) -> None:
        super().__init__(SolidFill(u'#'))

    def set_view(self, view: Widget):
        self.original_widget = view

    def open_dialog(self, dialog: Widget):
        self.original_widget = Overlay(dialog,
                                             self.original_widget,
                                             align='center', width=('relative', 80),
                                             valign='middle', height=('relative', 80),
                                             min_width=24, min_height=8,
                                             left=3,
                                             right=3,
                                             top=2,
                                             bottom=2)

    def close_dialog(self):
        self.original_widget = self.original_widget[0]
