from pathlib import Path

from injector import Module, singleton, provider

from urwid_assets.cli.import_.import_types import InputFile


class ImportModule(Module):
    def __init__(self, input_file: Path):
        self._input_file = input_file

    @singleton
    @provider
    def provide_input_file(self) -> InputFile:
        return InputFile(self._input_file)
