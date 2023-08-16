import logging
from importlib import metadata
from pathlib import Path

import click

from urwid_assets.cli.cli_module import CLIModule
from urwid_assets.cli.cli_types import SaltFile, DataFile
from urwid_assets.cli.export import export
from urwid_assets.cli.import_ import import_
from urwid_assets.cli.ui import ui
from urwid_assets.data_sources.crypto_compare.crypto_compare import CryptoCompare
from urwid_assets.data_sources.tiingo.tiingo import Tiingo

_DOT_FOLDER = '.urwid-assets'
_DATA_FILE = 'data'
_SALT_FILE = 'salt'
_LOG_FILE = 'log'

_DEFAULT_DATA_FILE: Path = Path.home() / _DOT_FOLDER / _DATA_FILE
_DEFAULT_SALT_FILE: Path = Path.home() / _DOT_FOLDER / _SALT_FILE
_DEFAULT_LOG_FILE: Path = Path.home() / _DOT_FOLDER / _LOG_FILE
_DEFAULT_LOG_LEVEL: str = 'INFO'

_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

_LOGGER = logging.getLogger(__name__)


def _setup_logger(log_level: str, log_file: Path) -> None:
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s'))
    logger.addHandler(handler)


@click.group(help='Terminal application for tracking asset portfolios')
@click.version_option(version=metadata.version('urwid-assets'), prog_name="urwid-assets")
@click.option('-d', '--data-file',
              help='Path to the data file',
              show_default=True,
              type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
              default=_DEFAULT_DATA_FILE)
@click.option('-s', '--salt-file',
              help=u'Path to the salt file to use in encryption, the salt file should be stored '
                   u'somewhere safe as it forms a part of the encryption key along with the '
                   u'passphrase supplied on startup',
              show_default=True,
              type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
              default=_DEFAULT_SALT_FILE)
@click.option('-f', '--log-file',
              help=u'Path to the log file',
              show_default=True,
              type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
              default=_DEFAULT_LOG_FILE)
@click.option('-l', '--log-level',
              help=u'The log level',
              show_default=True,
              type=click.Choice(_LOG_LEVELS),
              default=_DEFAULT_LOG_LEVEL)
@click.option('-i', '--init-with-test-data',
              help=u'Initialise with test data',
              is_flag=True)
@click.pass_context
def cli(ctx: click.Context,
        data_file: Path,
        salt_file: Path,
        log_file: Path,
        log_level: str,
        init_with_test_data: bool) -> None:
    _setup_logger(log_level, log_file)
    _LOGGER.info('data_file: %s', data_file)
    _LOGGER.info('salt_file: %s', salt_file)
    _LOGGER.info('init_with_test_data: %s', init_with_test_data)
    ctx.obj = CLIModule(data_file, salt_file, init_with_test_data, Tiingo(), CryptoCompare())


cli.add_command(ui)
cli.add_command(export)
cli.add_command(import_)
