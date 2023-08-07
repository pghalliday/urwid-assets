from injector import inject
from urwid import LineBox, ListBox, SimpleFocusListWalker, Button

from application.application_module import ContentView
from lib.widgets.views.view import View
from views.current_assets_view import CurrentAssetsView
from views.data_sources_view import DataSourcesView


class SideBarView(View):
    _content_view: ContentView

    @inject
    def __init__(
            self,
            content_view: ContentView,
            current_assets_view: CurrentAssetsView,
            data_sources_view: DataSourcesView,
    ) -> None:
        self._content_view = content_view
        super().__init__(LineBox(ListBox(SimpleFocusListWalker((
            Button(u'Current assets', lambda _: self._content_view.set_view(current_assets_view)),
            Button(u'Data sources', lambda _: self._content_view.set_view(data_sources_view)),
        )))))
