from injector import inject
from urwid import LineBox, ListBox, SimpleFocusListWalker, Button

from urwid_assets.cli.ui import ContentView
from urwid_assets.ui.views.assets_view import AssetsView
from urwid_assets.ui.views.data_sources_view import DataSourcesView
from urwid_assets.ui.views.snapshots_view import SnapshotsView
from urwid_assets.ui.widgets.views.view import View


class SideBarView(View):
    @inject
    def __init__(
            self,
            content_view: ContentView,
            assets_view: AssetsView,
            data_sources_view: DataSourcesView,
            snapshots_view: SnapshotsView,
    ) -> None:
        self._content_view = content_view
        super().__init__(LineBox(ListBox(SimpleFocusListWalker((
            Button(u'Assets', lambda _: self._content_view.set_view(assets_view)),
            Button(u'Data sources', lambda _: self._content_view.set_view(data_sources_view)),
            Button(u'Snapshots', lambda _: self._content_view.set_view(snapshots_view)),
        )))))