from argparse import Namespace
from typing import Type

from injector import singleton, provider

from app import AppModule
from base_parser import Command
from commands.import_.import_command import ImportCommand
from commands.import_.import_types import InputFile


class ImportModule(AppModule):
    def get_command_type(self) -> Type[Command] | None:
        return ImportCommand

    def apply_args(self, args: Namespace):
        self._args = args

    @singleton
    @provider
    def provide_salt_file(self) -> InputFile:
        return InputFile(self._args.input_file)
