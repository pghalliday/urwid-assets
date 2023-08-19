from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from urwid_assets.lib.redux.list_reducer import create_list_reducer, ListItem
from urwid_assets.lib.redux.reducer import ActionTypeFactory
from urwid_assets.lib.serialization.serialization import serializable

_LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

UPDATE_ASSET = ACTION_TYPE_FACTORY.create('UPDATE_ASSET')
ADD_ASSET = ACTION_TYPE_FACTORY.create('ADD_ASSET')
DELETE_ASSET = ACTION_TYPE_FACTORY.create('DELETE_ASSET')
MOVE_ASSET_DOWN = ACTION_TYPE_FACTORY.create('MOVE_ASSET_DOWN')
MOVE_ASSET_UP = ACTION_TYPE_FACTORY.create('MOVE_ASSET_UP')


@serializable()
@dataclass(frozen=True)
class Asset(ListItem):
    name: str
    amount: Decimal
    symbol: UUID


reducer = create_list_reducer(Asset,
                              add=ADD_ASSET,
                              update=UPDATE_ASSET,
                              delete=DELETE_ASSET,
                              move_up=MOVE_ASSET_UP,
                              move_down=MOVE_ASSET_DOWN)
