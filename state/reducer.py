import logging
from uuid import UUID

from lib.redux.reducer import combine_reducers, INIT, ReducerMapping
from lib.redux.store import Action
from state.models import State, Assets, Asset, AssetsFile, Snapshot, DataSource
from state.test_data import CURRENT

LOGGER = logging.getLogger(__name__)

UPDATE_ASSET = 'UPDATE_ASSET'
ADD_ASSET = 'ADD_ASSET'
DELETE_ASSET = 'DELETE_ASSET'
MOVE_ASSET_DOWN = 'MOVE_ASSET_DOWN'
MOVE_ASSET_UP = 'MOVE_ASSET_UP'
APPLY_DATA_SOURCE = 'APPLY_DATA_SOURCES'


def _assets_file_reducer(state: AssetsFile, action: Action) -> AssetsFile:
    if action.type == INIT:
        return AssetsFile(
            path=None,
            passphrase=None,
        )
    return state


def _data_sources_reducer(state: tuple[DataSource, ...], action: Action) -> tuple[DataSource, ...]:
    if action.type == INIT:
        return tuple()
    if action.type == APPLY_DATA_SOURCE:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        return tuple()
    return state


def _get_asset_index(assets: tuple[Asset, ...], uuid: UUID) -> int | None:
    for index, asset in enumerate(assets):
        if asset.uuid == uuid:
            return index
    return None


def _current_assets_reducer(state: tuple[Asset, ...], action: Action) -> tuple[Asset, ...]:
    if action.type == INIT:
        return CURRENT
    if action.type == ADD_ASSET:
        asset = action.payload
        assert isinstance(asset, Asset)
        return state + (asset,)
    if action.type == UPDATE_ASSET:
        asset = action.payload
        assert isinstance(asset, Asset)
        index = _get_asset_index(state, asset.uuid)
        if index is None:
            return state
        return state[:index] + (asset,) + state[index + 1:]
    if action.type == DELETE_ASSET:
        asset = action.payload
        assert isinstance(asset, Asset)
        index = _get_asset_index(state, asset.uuid)
        if index is None:
            return state
        return state[:index] + state[index + 1:]
    if action.type == MOVE_ASSET_UP:
        asset = action.payload
        assert isinstance(asset, Asset)
        index = _get_asset_index(state, asset.uuid)
        if index is None:
            return state
        if index > 0:
            return state[:index - 1] + (asset, state[index - 1]) + state[index + 1:]
        return state
    if action.type == MOVE_ASSET_DOWN:
        asset = action.payload
        assert isinstance(asset, Asset)
        index = _get_asset_index(state, asset.uuid)
        if index is None:
            return state
        if index < len(state) - 1:
            return state[:index] + (state[index + 1], asset) + state[index + 2:]
        return state
    return state


def _snapshots_reducer(state: tuple[Snapshot, ...], action: Action) -> tuple[Snapshot, ...]:
    if action.type == INIT:
        return tuple()
    return state


_assets_reducer = combine_reducers(Assets, (
    ReducerMapping('current', _current_assets_reducer),
    ReducerMapping('snapshots', _snapshots_reducer),
))

reducer = combine_reducers(State, (
    ReducerMapping('assets_file', _assets_file_reducer),
    ReducerMapping('data_sources', _data_sources_reducer),
    ReducerMapping('assets', _assets_reducer),
))
