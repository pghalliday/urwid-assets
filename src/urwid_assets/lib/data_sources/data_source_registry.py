import logging
from asyncio import Task, TaskGroup, create_task
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid1

from injector import singleton, inject

from urwid_assets.lib.data_sources.data_source import DataSource
from urwid_assets.lib.data_sources.models import QueryResult, Query
from urwid_assets.lib.redux.reducer import Action
from urwid_assets.lib.redux.store import Store
from urwid_assets.selectors.selectors import select_timestamp, \
    select_rates_by_data_source
from urwid_assets.state.saved.data_sources.data_sources import DataSourceInstance
from urwid_assets.state.saved.rates.rates import Rate
from urwid_assets.state.state import State
from urwid_assets.state.ui.ui import SET_LOADED_RATE, LoadedRate, START_LOADING_RATES, SET_LAST_UPDATE_TIME

_LOGGER = logging.getLogger(__name__)


class UnknownDataSource(Exception):
    name: str

    def __init__(self, name: str):
        super().__init__(u'Unknown data source: %s' % name)
        self.name = name


@dataclass(frozen=True)
class Group:
    data_source: DataSource
    data_source_config: DataSourceInstance
    rates: tuple[Rate, ...]


@singleton
class DataSourceRegistry:

    @inject
    def __init__(self, store: Store[State]):
        self._data_sources: dict[str, DataSource] = {}
        self._store = store

    def register(self, data_source: DataSource) -> None:
        self._data_sources[data_source.get_name()] = data_source

    def get_data_sources(self) -> tuple[DataSource, ...]:
        return tuple(self._data_sources.values())

    def get_data_source(self, name: str):
        try:
            return self._data_sources[name]
        except KeyError:
            raise UnknownDataSource(name)

    async def _set_loaded_rate(self, rate: Rate, task: Task[QueryResult]) -> None:
        result = await task
        if result.error is None:
            new_loaded_rate = LoadedRate(uuid=rate.uuid, rate=result.price, error=None)
        else:
            new_loaded_rate = LoadedRate(uuid=rate.uuid, rate=None, error=result.error)
        self._store.dispatch(Action(SET_LOADED_RATE, new_loaded_rate))

    async def refresh_rates(self) -> None:
        _LOGGER.info('refresh rates')
        self._store.dispatch(Action(START_LOADING_RATES), Action(SET_LAST_UPDATE_TIME, datetime.now()))
        groups = select_rates_by_data_source(self._store.get_state())
        timestamp = select_timestamp(self._store.get_state())
        async with TaskGroup() as data_source_queries:
            for group in groups:
                data_source_instance, rates = group
                data_source = self._data_sources[data_source_instance.type]
                aggregate = data_source.create_aggregate(
                    data_source_instance.config
                ) if timestamp is None else data_source.create_historical_aggregate(
                    timestamp,
                    data_source_instance.config
                )
                for rate in rates:
                    create_task(self._set_loaded_rate(rate, create_task(aggregate.select(Query(
                        uuid=uuid1(),
                        endpoint=rate.endpoint,
                        config=rate.config,
                    )))))
                data_source_queries.create_task(aggregate.run())
