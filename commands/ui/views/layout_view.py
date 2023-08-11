from injector import inject, singleton

from commands.ui.ui_types import ContentView
from commands.ui.views.side_bar_view import SideBarView
from commands.ui.widgets.views.columns_view import ColumnsView, Column
from commands.ui.widgets.views.view_wrap import ViewWrap


@singleton
class LayoutView(ViewWrap):
    @inject
    def __init__(self, side_bar_view: SideBarView, content_view: ContentView):
        super().__init__(ColumnsView((
            Column(2, side_bar_view),
            Column(9, content_view),
        )))
