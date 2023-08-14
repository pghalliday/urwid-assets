from injector import Module, singleton, provider

from urwid_assets.cli.ui.ui_types import ContentView, ShowLogPanel
from urwid_assets.ui.views.assets_view import AssetsView
from urwid_assets.ui.views.splash_view import SplashView
from urwid_assets.ui.widgets.views.placeholder_view import PlaceholderView
from urwid_assets.ui.widgets.views.view_manager import ViewManager


class UIModule(Module):
    def __init__(self, show_log_panel: bool):
        self._show_log_panel = show_log_panel

    @singleton
    @provider
    def provide_view_manager(self, splash_screen: SplashView) -> ViewManager:
        return ViewManager(splash_screen)

    @singleton
    @provider
    def provide_content_view(self, assets_view: AssetsView) -> ContentView:
        return ContentView(PlaceholderView(assets_view))

    @singleton
    @provider
    def provide_show_log_panel(self) -> ShowLogPanel:
        return ShowLogPanel(self._show_log_panel)
