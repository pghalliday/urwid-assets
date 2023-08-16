from __future__ import annotations

import logging
from dataclasses import dataclass

from urwid_assets.lib.data_sources.models import DataSourceConfig
from urwid_assets.lib.redux.list_reducer import create_list_reducer, ListItem
from urwid_assets.lib.redux.reducer import ActionTypeFactory
from urwid_assets.lib.serialization.serialization import serializable

LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

ADD_DATA_SOURCE = ACTION_TYPE_FACTORY.create('ADD_DATA_SOURCE')
UPDATE_DATA_SOURCE = ACTION_TYPE_FACTORY.create('UPDATE_DATA_SOURCE')
DELETE_DATA_SOURCE = ACTION_TYPE_FACTORY.create('DELETE_DATA_SOURCE')
MOVE_DATA_SOURCE_DOWN = ACTION_TYPE_FACTORY.create('MOVE_DATA_SOURCE_DOWN')
MOVE_DATA_SOURCE_UP = ACTION_TYPE_FACTORY.create('MOVE_DATA_SOURCE_UP')


@serializable()
@dataclass(frozen=True)
class DataSourceInstance(ListItem):
    name: str
    type: str
    config: tuple[DataSourceConfig, ...]


reducer = create_list_reducer(DataSourceInstance,
                              add=ADD_DATA_SOURCE,
                              update=UPDATE_DATA_SOURCE,
                              delete=DELETE_DATA_SOURCE,
                              move_up=MOVE_DATA_SOURCE_UP,
                              move_down=MOVE_DATA_SOURCE_DOWN)
