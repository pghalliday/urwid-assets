import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from injector import Injector

from application.application import Application
from application.application_module import ApplicationModule

_DOT_FOLDER = '.urwid-assets'
_DATA_FILE = 'data'
_SALT_FILE = 'salt'
_LOG_FILE = 'log'

_DEFAULT_DATA_FILE: Path = Path.home() / _DOT_FOLDER / _DATA_FILE
_DEFAULT_SALT_FILE: Path = Path.home() / _DOT_FOLDER / _SALT_FILE
_DEFAULT_LOG_FILE: Path = Path.home() / _DOT_FOLDER / _LOG_FILE
_DEFAULT_LOG_LEVEL: str = 'INFO'

_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog='urwid-assets',
        description=u'Terminal application for tracking asset portfolios',
    )
    parser.add_argument('-d', '--data-file',
                        help=u'Path to the data file',
                        type=Path,
                        default=_DEFAULT_DATA_FILE,
                        dest='data_file')
    parser.add_argument('-s', '--salt-file',
                        help=u'Path to the salt file to use in encryption, the salt file should be stored '
                             u'somewhere safe as it forms a part of the encryption key along with the '
                             u'passphrase supplied on startup',
                        type=Path,
                        default=_DEFAULT_SALT_FILE,
                        dest='salt_file')
    parser.add_argument('-f', '--log-file',
                        help=u'Path to the log file',
                        type=Path,
                        default=_DEFAULT_LOG_FILE,
                        dest='log_file')
    parser.add_argument('-l', '--log-level',
                        help=u'The log level',
                        choices=_LOG_LEVELS,
                        default=_DEFAULT_LOG_LEVEL,
                        dest='log_level')
    parser.add_argument('-p', '--show-log-panel',
                        help=u'Show the log panel',
                        action='store_true',
                        dest='show_log_panel')
    parser.add_argument('-i', '--init-with-test-data',
                        help=u'Initialise with test data',
                        action='store_true',
                        dest='init_with_test_data')
    return parser.parse_args()


def setup_logger(log_level: str, log_file: Path):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s'))
    logger.addHandler(handler)


if __name__ == '__main__':
    args = parse_args()
    setup_logger(args.log_level, args.log_file)
    injector = Injector(ApplicationModule(salt_file=args.salt_file,
                                          data_file=args.data_file,
                                          show_log_panel=args.show_log_panel,
                                          init_with_test_data=args.init_with_test_data))
    application = injector.get(Application)
    application.start()
