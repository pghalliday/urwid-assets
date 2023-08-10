import logging
from asyncio import Task, TaskGroup, create_task
from dataclasses import dataclass
from typing import Callable
from uuid import uuid1

from injector import singleton, inject

from lib.data_sources.data_source import DataSource
from lib.data_sources.models import QueryResult, Query
from lib.redux.reducer import Action
from lib.redux.reselect import create_selector, SelectorOptions
from lib.redux.store import Store
from state.assets.assets import SET_ASSET_PRICE, Asset
from state.data_sources.data_sources import DataSourceInstance
from state.state import State

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Group:
    data_source: DataSource
    data_source_config: DataSourceInstance
    assets: tuple[Asset, ...]


@singleton
class DataSources:
    _store: Store[State]
    _data_sources: dict[str, DataSource]
    _assets_by_data_source_selector: Callable[[State], tuple[Group, ...]]

    @inject
    def __init__(self, store: Store[State], data_sources: tuple[DataSource, ...]):
        self._store = store
        self._data_sources = {data_source.get_name(): data_source for data_source in data_sources}
        self._assets_by_data_source_selector = self._create_assets_by_data_source_selector()

    def _create_assets_by_data_source_selector(self) -> Callable[[State], tuple[Group, ...]]:
        return create_selector((
            lambda state: state.data_sources,
            lambda state: state.assets,
        ), self._group_assets_by_data_source, SelectorOptions(dimensions=(1,)))

    def _group_assets_by_data_source(
            self,
            data_source_config: DataSourceInstance,
            assets: tuple[Asset, ...],
    ) -> Group:
        return Group(
            data_source_config=data_source_config,
            data_source=self._data_sources[data_source_config.type],
            assets=tuple(filter(lambda asset: asset.data_source.uuid == data_source_config.uuid, assets)),
        )

    async def _refresh_asset(self, asset: Asset, task: Task[QueryResult]) -> None:
        result = await task
        self._store.dispatch(Action(SET_ASSET_PRICE, (asset, result)))

    async def refresh_all(self) -> None:
        _LOGGER.info('refresh all')
        groups = self._assets_by_data_source_selector(self._store.get_state())
        async with TaskGroup() as data_source_queries:
            for group in groups:
                aggregate = group.data_source.create_aggregate(group.data_source_config.config)
                for asset in group.assets:
                    create_task(self._refresh_asset(asset, create_task(aggregate.select(Query(
                        uuid=uuid1(),
                        endpoint=asset.data_source.endpoint,
                        config=asset.data_source.config,
                    )))))
                data_source_queries.create_task(aggregate.run())
