from argparse import ArgumentParser
from pathlib import Path

from injector import ClassAssistedBuilder, inject

from base_parser import Command
from commands.export.export import Export

DEFAULT_EXPORT_FILE: Path = Path('export.json')


class ExportCommand(Command):
    @inject
    def __init__(self,
                 export_builder: ClassAssistedBuilder[Export]):
        self._export_builder = export_builder

    def get_name(self) -> str:
        return u'export'

    def get_description(self) -> str:
        return u'Decrypt the data file and save to a JSON file'

    def configure(self, sub_parser: ArgumentParser):
        sub_parser.add_argument('--to',
                                help=u'The file to export to',
                                dest='output_file',
                                type=Path,
                                default=DEFAULT_EXPORT_FILE)
        sub_parser.set_defaults(func=self._export)

    def _export(self):
        self._export_builder.build()
