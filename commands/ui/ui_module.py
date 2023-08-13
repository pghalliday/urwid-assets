from argparse import Namespace
from typing import Type

from injector import singleton, provider

from app import AppModule
from base_parser import Command
from commands.ui.ui_command import UICommand
from commands.ui.ui_types import ContentView, ShowLogPanel
from commands.ui.views.assets_view import AssetsView
from commands.ui.views.splash_view import SplashView
from commands.ui.widgets.views.placeholder_view import PlaceholderView
from commands.ui.widgets.views.view_manager import ViewManager


class UIModule(AppModule):
    def __init__(self):
        self._args: Namespace | None = None

    def apply_args(self, args: Namespace):
        self._args = args

    def get_command_type(self) -> Type[Command] | None:
        return UICommand

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
        return ShowLogPanel(self._args.show_log_panel)
