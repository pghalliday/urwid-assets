from dataclasses import dataclass
from typing import TypeVar, Type
from uuid import UUID

from lib.redux.reducer import ActionType, Reducer, Action, INIT


@dataclass(frozen=True)
class ListItem:
    uuid: UUID


LIST_ITEM = TypeVar('LIST_ITEM', bound=ListItem)
LIST = tuple[LIST_ITEM, ...]


def get_list_index(state: LIST, uuid: UUID) -> int | None:
    for index, list_item in enumerate(state):
        if list_item.uuid == uuid:
            return index
    return None


def append_item(item: LIST_ITEM, state: LIST) -> LIST:
    return state + (item,)


def remove_item(item: LIST_ITEM, state: LIST) -> LIST:
    index = get_list_index(state, item.uuid)
    if index is None:
        return state
    return state[:index] + state[index + 1:]


def replace_item(item: LIST_ITEM, state: LIST) -> LIST:
    index = get_list_index(state, item.uuid)
    if index is None:
        return state
    return state[:index] + (item,) + state[index + 1:]


def move_item_up(item: LIST_ITEM, state: LIST) -> LIST:
    index = get_list_index(state, item.uuid)
    if index is None:
        return state
    if index > 0:
        return state[:index - 1] + (item, state[index - 1]) + state[index + 1:]
    return state


def move_item_down(item: LIST_ITEM, state: LIST) -> LIST:
    index = get_list_index(state, item.uuid)
    if index is None:
        return state
    if index < len(state) - 1:
        return state[:index] + (state[index + 1], item) + state[index + 2:]
    return state


def create_list_reducer(
        list_type: Type[LIST_ITEM],
        add: ActionType | None = None,
        update: ActionType | None = None,
        delete: ActionType | None = None,
        move_up: ActionType | None = None,
        move_down: ActionType | None = None,
) -> Reducer[LIST]:
    def reducer(state: LIST, action: Action) -> LIST:
        if action.type == INIT:
            return tuple()
        if add and action.type == add:
            item = action.payload
            assert isinstance(item, list_type)
            return append_item(item, state)
        if update and action.type == update:
            item = action.payload
            assert isinstance(item, list_type)
            return replace_item(item, state)
        if delete and action.type == delete:
            item = action.payload
            assert isinstance(item, list_type)
            return remove_item(item, state)
        if move_up and action.type == move_up:
            item = action.payload
            assert isinstance(item, list_type)
            return move_item_up(item, state)
        if move_down and action.type == move_down:
            item = action.payload
            assert isinstance(item, list_type)
            return move_item_down(item, state)
        return state

    return reducer
