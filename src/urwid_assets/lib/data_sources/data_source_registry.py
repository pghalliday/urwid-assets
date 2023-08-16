import logging
from asyncio import Task, TaskGroup, create_task
from dataclasses import dataclass, replace
from typing import Callable
from uuid import uuid1, UUID

from injector import singleton, inject

from urwid_assets.lib.data_sources.data_source import DataSource
from urwid_assets.lib.data_sources.models import QueryResult, Query
from urwid_assets.lib.redux.reducer import Action
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store
from urwid_assets.state.assets.assets import Asset, UPDATE_ASSET
from urwid_assets.state.data_sources.data_sources import DataSourceInstance
from urwid_assets.state.snapshots.snapshots import Snapshot, AssetSnapshot, get_asset_snapshot, UPDATE_ASSET_SNAPSHOT
from urwid_assets.state.state import State

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
    assets: tuple[Asset, ...]


@singleton
class DataSourceRegistry:

    @inject
    def __init__(self, store: Store[State]):
        self._data_sources: dict[str, DataSource] = {}
        self._store = store
        self._select_assets_by_data_source = self._create_assets_by_data_source_selector()

    def register(self, data_source: DataSource) -> None:
        self._data_sources[data_source.get_name()] = data_source

    def get_data_sources(self) -> tuple[DataSource, ...]:
        return tuple(self._data_sources.values())

    def get_data_source(self, name: str):
        try:
            return self._data_sources[name]
        except KeyError:
            raise UnknownDataSource(name)

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
        if result.error is None:
            new_asset = replace(asset, price=result.price, error=None)
        else:
            new_asset = replace(asset, price=None, error=result.error)
        self._store.dispatch(Action(UPDATE_ASSET, new_asset))

    async def _refresh_asset_snapshot(self,
                                      uuid: UUID,
                                      asset_snapshot: AssetSnapshot,
                                      task: Task[QueryResult]) -> None:
        result = await task
        if result.error is None:
            new_asset_snapshot = replace(asset_snapshot, price=result.price, error=None)
        else:
            new_asset_snapshot = replace(asset_snapshot, price=None, error=result.error)
        self._store.dispatch(Action(UPDATE_ASSET_SNAPSHOT, (uuid, new_asset_snapshot)))

    async def refresh_all(self) -> None:
        _LOGGER.info('refresh all')
        groups = self._select_assets_by_data_source(self._store.get_state())
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

    async def refresh_snapshot(self, snapshot: Snapshot) -> None:
        _LOGGER.info('refresh snapshot')
        state = self._store.get_state()
        groups = self._select_assets_by_data_source(state)
        async with TaskGroup() as data_source_queries:
            for group in groups:
                aggregate = group.data_source.create_historical_aggregate(snapshot.timestamp,
                                                                          group.data_source_config.config)
                for asset in group.assets:
                    create_task(self._refresh_asset_snapshot(snapshot.uuid,
                                                             get_asset_snapshot(asset.uuid, snapshot.assets),
                                                             create_task(aggregate.select(Query(
                                                                 uuid=uuid1(),
                                                                 endpoint=asset.data_source.endpoint,
                                                                 config=asset.data_source.config,
                                                             )))))
                data_source_queries.create_task(aggregate.run())
