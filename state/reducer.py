import logging
from types import MappingProxyType
from uuid import UUID

from lib.redux.reducer import combine_reducers, INIT
from lib.redux.store import Action
from state.models import State, Assets, Asset, AssetsFile, Snapshot
from state.test_data import STATE

LOGGER = logging.getLogger(__name__)

UPDATE_ASSET = 'UPDATE_ASSET'
ADD_ASSET = 'ADD_ASSET'
DELETE_ASSET = 'DELETE_ASSET'
MOVE_ASSET_DOWN = 'MOVE_ASSET_DOWN'
MOVE_ASSET_UP = 'MOVE_ASSET_UP'


def _assets_file_reducer(state: AssetsFile, action: Action) -> AssetsFile:
    if action.type == INIT:
        return STATE.assets_file
    return state


def _get_asset_index(assets: tuple[Asset, ...], uuid: UUID) -> int | None:
    for index, asset in enumerate(assets):
        if asset.uuid == uuid:
            return index
    return None


def _current_assets_reducer(state: tuple[Asset, ...], action: Action) -> tuple[Asset, ...]:
    if action.type == INIT:
        return STATE.assets.current
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
        return STATE.assets.snapshots
    return state


_assets_reducer = combine_reducers(Assets, MappingProxyType({
    'current': _current_assets_reducer,
    'snapshots': _snapshots_reducer,

}))

reducer = combine_reducers(State, MappingProxyType({
    'assets_file': _assets_file_reducer,
    'assets': _assets_reducer,
}))
