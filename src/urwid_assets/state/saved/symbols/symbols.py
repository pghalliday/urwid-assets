import logging
from dataclasses import dataclass
from uuid import UUID

from urwid_assets.lib.redux.list_reducer import ListItem, create_list_reducer
from urwid_assets.lib.redux.reducer import ActionTypeFactory
from urwid_assets.lib.serialization.serialization import serializable

_LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

UPDATE_SYMBOL = ACTION_TYPE_FACTORY.create('UPDATE_SYMBOL')
ADD_SYMBOL = ACTION_TYPE_FACTORY.create('ADD_SYMBOL')
DELETE_SYMBOL = ACTION_TYPE_FACTORY.create('DELETE_SYMBOL')
MOVE_SYMBOL_DOWN = ACTION_TYPE_FACTORY.create('MOVE_SYMBOL_DOWN')
MOVE_SYMBOL_UP = ACTION_TYPE_FACTORY.create('MOVE_SYMBOL_UP')


@serializable()
@dataclass(frozen=True)
class Symbol(ListItem):
    name: str


class UnknownSymbol(Exception):
    def __init__(self, uuid: UUID):
        super().__init__(u'Unknown symbol: %s' % uuid)
        self.uuid = uuid


def get_symbol_index(uuid: UUID, symbols: tuple[Symbol, ...]) -> int:
    for index, symbol in enumerate(symbols):
        if symbol.uuid == uuid:
            return index
    raise UnknownSymbol(uuid)


def get_symbol(uuid: UUID, symbols: tuple[Symbol, ...]) -> Symbol:
    return symbols[get_symbol_index(uuid, symbols)]


reducer = create_list_reducer(Symbol,
                              add=ADD_SYMBOL,
                              update=UPDATE_SYMBOL,
                              delete=DELETE_SYMBOL,
                              move_up=MOVE_SYMBOL_UP,
                              move_down=MOVE_SYMBOL_DOWN)
