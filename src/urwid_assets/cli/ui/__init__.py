import logging

import click
from injector import Injector

from urwid_assets.cli.ui.ui_module import UIModule
from urwid_assets.cli.ui.ui_types import ContentView, ShowLogPanel
from urwid_assets.ui.ui import UI

_LOGGER = logging.getLogger(__name__)


@click.command(help='Start the UI')
@click.option('-p', '--show-log-panel',
              help=u'Show the log panel',
              is_flag=True)
@click.pass_context
def ui(ctx: click.Context, show_log_panel: bool) -> None:
    _LOGGER.info('show_log_panel: %s', show_log_panel)
    cli_module = ctx.obj
    injector = Injector([cli_module, UIModule(show_log_panel)])
    injector.get(UI)
