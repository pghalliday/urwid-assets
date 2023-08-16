import logging
from pathlib import Path

import click
from injector import Injector

from urwid_assets.cli.import_.import_module import ImportModule
from urwid_assets.cli.import_.import_types import InputFile
from urwid_assets.import_.import_ import Import

_LOGGER = logging.getLogger(__name__)

_DEFAULT_EXPORT_FILE: Path = Path('export.json')


@click.command('import', help='Import a JSON export')
@click.option('--from', 'from_',
              help=u'The file to import from',
              show_default=True,
              type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
              default=_DEFAULT_EXPORT_FILE)
@click.pass_context
def import_(ctx: click.Context, from_: Path) -> None:
    _LOGGER.info('from: %s', from_)
    cli_module = ctx.obj
    injector = Injector([cli_module, ImportModule(from_)])
    injector.get(Import)
