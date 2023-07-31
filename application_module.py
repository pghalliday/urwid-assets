from injector import Module, singleton, provider

from lib.redux.store import Store
from lib.widgets.view_manager import ViewManager
from state.reducer import reducer
from views.splash_screen import SplashScreen


class ApplicationModule(Module):
    @singleton
    @provider
    def provide_store(self) -> Store:
        return Store(reducer)

    @singleton
    @provider
    def provide_view_manager(self, splash_screen: SplashScreen) -> ViewManager:
        return ViewManager(splash_screen)
