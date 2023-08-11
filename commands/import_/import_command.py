from argparse import ArgumentParser
from pathlib import Path

from injector import ClassAssistedBuilder, inject

from base_parser import Command
from commands.export.export_command import DEFAULT_EXPORT_FILE
from commands.import_.import_ import Import


class ImportCommand(Command):
    @inject
    def __init__(self,
                 import_builder: ClassAssistedBuilder[Import]):
        self._import_builder = import_builder

    def get_name(self) -> str:
        return u'import'

    def get_description(self) -> str:
        return u'Import a JSON export'

    def configure(self, sub_parser: ArgumentParser):
        sub_parser.add_argument('--from',
                                help=u'The file to import',
                                dest='input_file',
                                type=Path,
                                default=DEFAULT_EXPORT_FILE)
        sub_parser.set_defaults(func=self._import)

    def _import(self):
        self._import_builder.build()
