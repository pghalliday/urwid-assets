from argparse import Namespace
from typing import Type

from injector import singleton, provider

from app import AppModule
from base_parser import Command
from commands.export.export_command import ExportCommand
from commands.export.export_types import OutputFile


class ExportModule(AppModule):
    def __init__(self):
        self._args: Namespace | None = None

    def get_command_type(self) -> Type[Command] | None:
        return ExportCommand

    def apply_args(self, args: Namespace):
        self._args = args

    @singleton
    @provider
    def provide_salt_file(self) -> OutputFile:
        return OutputFile(self._args.output_file)
