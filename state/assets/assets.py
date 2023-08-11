from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from decimal import Decimal
from uuid import UUID

from lib.data_sources.models import DataSourceConfig, QueryResult
from lib.redux.reducer import INIT, ActionTypeFactory
from lib.redux.store import Action
from lib.serialization.serialization import serializable

_LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

UPDATE_ASSET = ACTION_TYPE_FACTORY.create('UPDATE_ASSET')
ADD_ASSET = ACTION_TYPE_FACTORY.create('ADD_ASSET')
DELETE_ASSET = ACTION_TYPE_FACTORY.create('DELETE_ASSET')
MOVE_ASSET_DOWN = ACTION_TYPE_FACTORY.create('MOVE_ASSET_DOWN')
MOVE_ASSET_UP = ACTION_TYPE_FACTORY.create('MOVE_ASSET_UP')
SET_ASSET_PRICE = ACTION_TYPE_FACTORY.create('SET_ASSET_PRICE')


@serializable()
@dataclass(frozen=True)
class AssetDataSource:
    uuid: UUID
    endpoint: str
    config: tuple[DataSourceConfig, ...]


@serializable()
@dataclass(frozen=True)
class Asset:
    uuid: UUID
    name: str
    amount: Decimal
    data_source: AssetDataSource
    price: Decimal | None = None
    error: str | None = None


def _get_asset_index(assets: tuple[Asset, ...], uuid: UUID) -> int | None:
    for index, asset in enumerate(assets):
        if asset.uuid == uuid:
            return index
    return None


def reducer(state: tuple[Asset, ...], action: Action) -> tuple[Asset, ...]:
    if action.type == INIT:
        return tuple()
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
    if action.type == SET_ASSET_PRICE:
        (asset, result) = action.payload
        assert isinstance(asset, Asset)
        assert isinstance(result, QueryResult)
        index = _get_asset_index(state, asset.uuid)
        if index is None:
            return state
        if result.error is None:
            new_asset = replace(asset, price=result.price, error=None)
        else:
            new_asset = replace(asset, price=None, error=result.error)
        return state[:index] + (new_asset,) + state[index + 1:]
    return state
