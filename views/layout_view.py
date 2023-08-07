from injector import inject, singleton

from application.application_module import ContentView
from lib.widgets.views.columns_view import ColumnsView, Column
from lib.widgets.views.view_wrap import ViewWrap
from views.side_bar_view import SideBarView


@singleton
class LayoutView(ViewWrap):
    @inject
    def __init__(self, side_bar_view: SideBarView, content_view: ContentView):
        super().__init__(ColumnsView((
            Column(2, side_bar_view),
            Column(9, content_view),
        )))
