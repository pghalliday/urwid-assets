from injector import Module, singleton, provider

from data_sources.test import Test
from data_sources.tiingo import Tiingo
from lib.data_source.data_source import DataSource
from lib.redux.store import Store
from lib.widgets.view_manager import ViewManager
from state.models import State
from state.reducer import reducer
from views.splash_screen import SplashScreen


class ApplicationModule(Module):
    @singleton
    @provider
    def provide_store(self) -> Store[State]:
        return Store(reducer)

    @singleton
    @provider
    def provide_view_manager(self, splash_screen: SplashScreen) -> ViewManager:
        return ViewManager(splash_screen)

    @singleton
    @provider
    def provide_data_sources(self) -> tuple[DataSource, ...]:
        return (
            Tiingo(),
            Test(),
        )
