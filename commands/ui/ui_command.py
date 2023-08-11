from argparse import ArgumentParser

from injector import ClassAssistedBuilder, inject

from base_parser import Command
from commands.ui.ui import UI


class UICommand(Command):
    @inject
    def __init__(self, ui_builder: ClassAssistedBuilder[UI]):
        self._ui_builder = ui_builder

    def get_name(self) -> str:
        return u'ui'

    def get_description(self) -> str:
        return u'Start the UI'

    def configure(self, sub_parser: ArgumentParser):
        sub_parser.add_argument('-p', '--show-log-panel',
                                help=u'Show the log panel',
                                action='store_true',
                                dest='show_log_panel')
        sub_parser.set_defaults(func=self._ui)

    def _ui(self):
        self._ui_builder.build()
