import logging
from argparse import Namespace
from asyncio import get_event_loop, AbstractEventLoop
from pathlib import Path

from injector import singleton, provider

from app import AppModule
from base_types import SaltFile, DataFile
from lib.data_sources.data_source import DataSource
from lib.data_sources.data_source_registry import DataSourceRegistry
from lib.redux.store import Store
from state.state import State, reducer
from test_data.test_data import INITIAL_STATE


def _setup_logger(log_level: str, log_file: Path) -> None:
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s'))
    logger.addHandler(handler)


class BaseModule(AppModule):
    def __init__(self,
                 *data_sources: DataSource):
        self._salt_file: Path | None = None
        self._data_file: Path | None = None
        self._init_with_test_data: bool = False
        self._data_sources = data_sources

    def apply_args(self, args: Namespace):
        _setup_logger(args.log_level, args.log_file)
        self._salt_file = args.salt_file
        self._data_file = args.data_file
        self._init_with_test_data = args.init_with_test_data

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
