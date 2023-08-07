from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from random import randrange
from uuid import UUID, uuid1

from lib.redux.reducer import INIT, ActionTypeFactory
from lib.redux.store import Action
from lib.serialization import serializable
from state.data_sources import DATA_SOURCE_UUID

LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

UPDATE_ASSET = ACTION_TYPE_FACTORY.create('UPDATE_ASSET')
ADD_ASSET = ACTION_TYPE_FACTORY.create('ADD_ASSET')
DELETE_ASSET = ACTION_TYPE_FACTORY.create('DELETE_ASSET')
MOVE_ASSET_DOWN = ACTION_TYPE_FACTORY.create('MOVE_ASSET_DOWN')
MOVE_ASSET_UP = ACTION_TYPE_FACTORY.create('MOVE_ASSET_UP')


@serializable()
@dataclass(frozen=True)
class AssetDataSourceConfig:
    name: str


@serializable('string')
@dataclass(frozen=True)
class StringAssetDataSourceConfig(AssetDataSourceConfig):
    value: str


@serializable()
@dataclass(frozen=True)
class AssetDataSource:
    uuid: UUID
    endpoint: str
    config: tuple[AssetDataSourceConfig, ...]


@serializable()
@dataclass(frozen=True)
class Asset:
    uuid: UUID
    name: str
    amount: Decimal
    data_source: AssetDataSource
    price: Decimal


def _asset(uuid: UUID, index: int) -> Asset:
    return Asset(
        uuid=uuid,
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        data_source=AssetDataSource(
            uuid=DATA_SOURCE_UUID,
            endpoint='iex',
            config=(StringAssetDataSourceConfig(
                name='ticker',
                value='AAPL%s' % index,
            ),)
        ),
        price=Decimal(-1)
    )


_IDS = tuple((uuid1(), index) for index in range(5))
_CURRENT = tuple(_asset(uuid, index) for uuid, index in _IDS)


def _get_asset_index(assets: tuple[Asset, ...], uuid: UUID) -> int | None:
    for index, asset in enumerate(assets):
        if asset.uuid == uuid:
            return index
    return None


def reducer(state: tuple[Asset, ...], action: Action) -> tuple[Asset, ...]:
    if action.type == INIT:
        return _CURRENT
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
