from asyncio import get_event_loop, AbstractEventLoop
from pathlib import Path
from typing import NewType

from injector import Module, singleton, provider

from data_sources.crypto_compare.crypto_compare import CryptoCompare
from data_sources.tiingo.tiingo import Tiingo
from lib.data_sources.data_source import DataSource
from lib.redux.store import Store
from lib.widgets.views.placeholder_view import PlaceholderView
from lib.widgets.views.view_manager import ViewManager
from state.state import State, reducer
from test_data import INITIAL_STATE
from views.current_assets_view import CurrentAssetsView
from views.splash_view import SplashView

ContentView = NewType('ContentView', PlaceholderView)
SaltFile = NewType('SaltFile', Path)
DataFile = NewType('DataFile', Path)
ShowLogPanel = NewType('ShowLogPanel', bool)


class ApplicationModule(Module):
    _salt_file: Path
    _data_file: Path
    _show_log_panel: bool
    _init_with_test_data: bool

    def __init__(self,
                 salt_file: Path,
                 data_file: Path,
                 show_log_panel: bool,
                 init_with_test_data: bool):
        self._salt_file = salt_file
        self._data_file = data_file
        self._show_log_panel = show_log_panel
        self._init_with_test_data = init_with_test_data

    @singleton
    @provider
    def provide_loop(self) -> AbstractEventLoop:
        return get_event_loop()

    @singleton
    @provider
    def provide_salt_file(self) -> SaltFile:
        return SaltFile(self._salt_file)

    @singleton
    @provider
    def provide_data_file(self) -> DataFile:
        return DataFile(self._data_file)

    @singleton
    @provider
    def provide_store(self) -> Store[State]:
        return Store(reducer, INITIAL_STATE if self._init_with_test_data else None)

    @singleton
    @provider
    def provide_view_manager(self, splash_screen: SplashView) -> ViewManager:
        return ViewManager(splash_screen)

    @singleton
    @provider
    def provide_data_sources(self, crypto_compare: CryptoCompare, tiingo: Tiingo) -> tuple[DataSource, ...]:
        return (
            crypto_compare,
            tiingo,
        )

    @singleton
    @provider
    def provide_content_view(self, current_assets_view: CurrentAssetsView) -> ContentView:
        return ContentView(PlaceholderView(current_assets_view))

    @singleton
    @provider
    def provide_show_log_panel(self) -> ShowLogPanel:
        return ShowLogPanel(self._show_log_panel)
