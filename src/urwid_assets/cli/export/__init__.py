import logging
from pathlib import Path

import click
from injector import Injector

from urwid_assets.cli.export.export_module import ExportModule
from urwid_assets.cli.export.export_types import OutputFile
from urwid_assets.export.export import Export

_LOGGER = logging.getLogger(__name__)

_DEFAULT_EXPORT_FILE: Path = Path('export.json')


@click.command(help='Decrypt the data file and save to a JSON file')
@click.option('--to',
              help=u'The file to export to',
              show_default=True,
              type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
              default=_DEFAULT_EXPORT_FILE)
@click.pass_context
def export(ctx: click.Context, to: Path) -> None:
    _LOGGER.info('to: %s', to)
    cli_module = ctx.obj
    injector = Injector([cli_module, ExportModule(to)])
    injector.get(Export)
