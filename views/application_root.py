from injector import inject, singleton, ClassAssistedBuilder

from lib.widgets.columnar_view import ColumnarView, Column
from lib.widgets.view import View
from lib.widgets.view_manager import ViewManager
from views.current_assets_screen import CurrentAssetsScreen
from views.log_screen import LogScreen


@singleton
class ApplicationRoot(View):
    _view_manager: ViewManager

    @inject
    def __init__(self,
                 log_screen: LogScreen,
                 view_manager: ViewManager,
                 assets_screen_builder: ClassAssistedBuilder[CurrentAssetsScreen]):
        self._view_manager = view_manager
        self._assets_screen_builder = assets_screen_builder
        # TODO: collect path and passphrase
        self._view_manager.set_screen(self._assets_screen_builder.build())
        super().__init__(ColumnarView((Column(2, self._view_manager), Column(1, log_screen))))

    def activate(self) -> None:
        super().activate()
        self._view_manager.activate()

    def deactivate(self) -> None:
        self._view_manager.deactivate()
        super().deactivate()
