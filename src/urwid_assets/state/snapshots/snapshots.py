import logging
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from urwid_assets.lib.redux.list_reducer import ListItem, create_list_reducer, move_item_up, replace_item, \
    move_item_down
from urwid_assets.lib.redux.reducer import ActionTypeFactory, Action
from urwid_assets.lib.serialization.serialization import serializable

LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

ADD_SNAPSHOT = ACTION_TYPE_FACTORY.create('ADD_SNAPSHOT')
UPDATE_SNAPSHOT = ACTION_TYPE_FACTORY.create('UPDATE_SNAPSHOT')
DELETE_SNAPSHOT = ACTION_TYPE_FACTORY.create('DELETE_SNAPSHOT')
MOVE_SNAPSHOT_DOWN = ACTION_TYPE_FACTORY.create('MOVE_SNAPSHOT_DOWN')
MOVE_SNAPSHOT_UP = ACTION_TYPE_FACTORY.create('MOVE_SNAPSHOT_UP')
MOVE_ASSET_SNAPSHOT_DOWN = ACTION_TYPE_FACTORY.create('MOVE_ASSET_SNAPSHOT_DOWN')
MOVE_ASSET_SNAPSHOT_UP = ACTION_TYPE_FACTORY.create('MOVE_ASSET_SNAPSHOT_UP')
UPDATE_ASSET_SNAPSHOT = ACTION_TYPE_FACTORY.create('UPDATE_ASSET_SNAPSHOT')


@serializable()
@dataclass(frozen=True)
class AssetSnapshot(ListItem):
    name: str
    amount: Decimal
    price: Decimal | None = None
    error: str | None = None


@serializable()
@dataclass(frozen=True)
class Snapshot(ListItem):
    name: str
    assets: tuple[AssetSnapshot, ...]
    timestamp: datetime


class UnknownSnapshot(Exception):
    def __init__(self, uuid: UUID):
        super().__init__(u'Unknown snapshot: %s' % uuid)
        self.uuid = uuid


class UnknownAssetSnapshot(Exception):
    def __init__(self, uuid: UUID):
        super().__init__(u'Unknown asset snapshot: %s' % uuid)
        self.uuid = uuid


def get_asset_snapshot(uuid: UUID, asset_snapshots: tuple[AssetSnapshot, ...]):
    for asset_snapshot in asset_snapshots:
        if asset_snapshot.uuid == uuid:
            return asset_snapshot
    raise UnknownAssetSnapshot(uuid)


def get_snapshot(uuid: UUID, snapshots: tuple[Snapshot, ...]):
    for snapshot in snapshots:
        if snapshot.uuid == uuid:
            return snapshot
    raise UnknownSnapshot(uuid)


_reducer = create_list_reducer(Snapshot,
                               add=ADD_SNAPSHOT,
                               update=UPDATE_SNAPSHOT,
                               delete=DELETE_SNAPSHOT,
                               move_up=MOVE_SNAPSHOT_UP,
                               move_down=MOVE_SNAPSHOT_DOWN)


def reducer(snapshots: tuple[Snapshot, ...], action: Action) -> tuple[Snapshot, ...]:
    if action.type == MOVE_ASSET_SNAPSHOT_UP:
        (uuid, asset_snapshot) = action.payload
        assert isinstance(uuid, UUID)
        assert isinstance(asset_snapshot, AssetSnapshot)
        try:
            snapshot = get_snapshot(uuid, snapshots)
            return replace_item(replace(snapshot, assets=move_item_up(asset_snapshot, snapshot.assets)), snapshots)
        except UnknownSnapshot:
            return snapshots
    if action.type == MOVE_ASSET_SNAPSHOT_DOWN:
        (uuid, asset_snapshot) = action.payload
        assert isinstance(uuid, UUID)
        assert isinstance(asset_snapshot, AssetSnapshot)
        try:
            snapshot = get_snapshot(uuid, snapshots)
            return replace_item(replace(snapshot, assets=move_item_down(asset_snapshot, snapshot.assets)), snapshots)
        except UnknownSnapshot:
            return snapshots
    if action.type == UPDATE_ASSET_SNAPSHOT:
        (uuid, asset_snapshot) = action.payload
        assert isinstance(uuid, UUID)
        assert isinstance(asset_snapshot, AssetSnapshot)
        try:
            snapshot = get_snapshot(uuid, snapshots)
            return replace_item(replace(snapshot, assets=replace_item(asset_snapshot, snapshot.assets)), snapshots)
        except UnknownSnapshot:
            return snapshots
    return _reducer(snapshots, action)
