from argparse import ArgumentParser, Namespace
from pathlib import Path

_DOT_FOLDER = '.urwid-assets'
_DATA_FILE = 'data'
_SALT_FILE = 'salt'
_LOG_FILE = 'log'

_DEFAULT_DATA_FILE: Path = Path.home() / _DOT_FOLDER / _DATA_FILE
_DEFAULT_SALT_FILE: Path = Path.home() / _DOT_FOLDER / _SALT_FILE
_DEFAULT_LOG_FILE: Path = Path.home() / _DOT_FOLDER / _LOG_FILE
_DEFAULT_LOG_LEVEL: str = 'INFO'

_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']


class Command:
    def get_name(self) -> str:
        pass

    def get_description(self) -> str:
        pass

    def configure(self, sub_parser: ArgumentParser):
        pass


class BaseParser:
    def __init__(self):
        self._parser = ArgumentParser(
            prog='urwid-assets',
            description=u'Terminal application for tracking asset portfolios',
        )
        self._parser.add_argument('-d', '--data-file',
                                  help=u'Path to the data file',
                                  type=Path,
                                  default=_DEFAULT_DATA_FILE,
                                  dest='data_file')
        self._parser.add_argument('-s', '--salt-file',
                                  help=u'Path to the salt file to use in encryption, the salt file should be stored '
                                       u'somewhere safe as it forms a part of the encryption key along with the '
                                       u'passphrase supplied on startup',
                                  type=Path,
                                  default=_DEFAULT_SALT_FILE,
                                  dest='salt_file')
        self._parser.add_argument('-f', '--log-file',
                                  help=u'Path to the log file',
                                  type=Path,
                                  default=_DEFAULT_LOG_FILE,
                                  dest='log_file')
        self._parser.add_argument('-l', '--log-level',
                                  help=u'The log level',
                                  choices=_LOG_LEVELS,
                                  default=_DEFAULT_LOG_LEVEL,
                                  dest='log_level')
        self._parser.add_argument('-i', '--init-with-test-data',
                                  help=u'Initialise with test data',
                                  action='store_true',
                                  dest='init_with_test_data')
        self._sub_parsers = self._parser.add_subparsers(required=True,
                                                        title=u'Commands')

    def add_command(self, command: Command):
        sub_parser = self._sub_parsers.add_parser(command.get_name(),
                                                  description=command.get_description())
        command.configure(sub_parser)

    def parse(self) -> Namespace:
        return self._parser.parse_args()
