import logging
from dataclasses import dataclass
from uuid import UUID

from urwid_assets.lib.data_sources.models import DataSourceConfig
from urwid_assets.lib.redux.list_reducer import ListItem, create_list_reducer
from urwid_assets.lib.redux.reducer import ActionTypeFactory
from urwid_assets.lib.serialization.serialization import serializable

_LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

UPDATE_RATE = ACTION_TYPE_FACTORY.create('UPDATE_RATE')
ADD_RATE = ACTION_TYPE_FACTORY.create('ADD_RATE')
DELETE_RATE = ACTION_TYPE_FACTORY.create('DELETE_RATE')
MOVE_RATE_DOWN = ACTION_TYPE_FACTORY.create('MOVE_RATE_DOWN')
MOVE_RATE_UP = ACTION_TYPE_FACTORY.create('MOVE_RATE_UP')


@serializable()
@dataclass(frozen=True)
class Rate(ListItem):
    name: str
    cost: int
    from_symbol: UUID
    to_symbol: UUID
    data_source: UUID
    endpoint: str
    config: tuple[DataSourceConfig, ...]


reducer = create_list_reducer(Rate,
                              add=ADD_RATE,
                              update=UPDATE_RATE,
                              delete=DELETE_RATE,
                              move_up=MOVE_RATE_UP,
                              move_down=MOVE_RATE_DOWN)
