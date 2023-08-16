from pathlib import Path

from injector import Module, singleton, provider

from urwid_assets.cli.export.export_types import OutputFile


class ExportModule(Module):
    def __init__(self, output_file: Path):
        self._output_file = output_file

    @singleton
    @provider
    def provide_salt_file(self) -> OutputFile:
        return OutputFile(self._output_file)
