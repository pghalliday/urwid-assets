from asyncio import AbstractEventLoop, get_event_loop
from pathlib import Path

from injector import Module, singleton, provider

from urwid_assets.cli.cli_types import SaltFile, DataFile
from urwid_assets.data.data import INITIAL_STATE
from urwid_assets.lib.data_sources.data_source import DataSource
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.store import Store
from urwid_assets.state.state import State, reducer


class CLIModule(Module):
    def __init__(self,
                 salt_file: Path,
                 data_file: Path,
                 init_with_test_data: bool,
                 data_sources: tuple[DataSource, ...]):
        self._salt_file = salt_file
        self._data_file = data_file
        self._init_with_test_data = init_with_test_data
        self._data_sources = data_sources

    @singleton
    @provider
    def provide_loop(self) -> AbstractEventLoop:
        return get_event_loop()

    @singleton
    @provider
    def provide_salt_file(self) -> SaltFile:
        return SaltFile(self._salt_file)

    @singleton
    @provider
    def provide_data_file(self) -> DataFile:
        return DataFile(self._data_file)

    @singleton
    @provider
    def provide_store(self) -> Store[State]:
        return Store(reducer, INITIAL_STATE if self._init_with_test_data else None)

    @singleton
    @provider
    def provide_data_source_registry(self, store: Store[State]) -> DataSourceRegistry:
        data_source_registry = DataSourceRegistry(store)
        for data_source in self._data_sources:
            data_source_registry.register(data_source)
        return data_source_registry
