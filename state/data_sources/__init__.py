from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import UUID, uuid1

from lib.redux.reducer import INIT, ActionTypeFactory
from lib.redux.store import Action
from lib.serialization import serializable

LOGGER = logging.getLogger(__name__)
ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

ADD_DATA_SOURCE = ACTION_TYPE_FACTORY.create('ADD_DATA_SOURCE')
UPDATE_DATA_SOURCE = ACTION_TYPE_FACTORY.create('UPDATE_DATA_SOURCE')
DELETE_DATA_SOURCE = ACTION_TYPE_FACTORY.create('DELETE_DATA_SOURCE')
MOVE_DATA_SOURCE_DOWN = ACTION_TYPE_FACTORY.create('MOVE_DATA_SOURCE_DOWN')
MOVE_DATA_SOURCE_UP = ACTION_TYPE_FACTORY.create('MOVE_DATA_SOURCE_UP')


@serializable()
@dataclass(frozen=True)
class DataSourceConfigField:
    name: str


@serializable('string')
@dataclass(frozen=True)
class StringDataSourceConfigField(DataSourceConfigField):
    value: str


@serializable()
@dataclass(frozen=True)
class DataSource:
    uuid: UUID
    name: str
    type: str
    config: tuple[DataSourceConfigField, ...]


DATA_SOURCE_UUID = uuid1()
DATA_SOURCES = (DataSource(
    uuid=DATA_SOURCE_UUID,
    name=u'My Tiingo',
    type='tiingo',
    config=(
        StringDataSourceConfigField(
            name='base_url',
            value='https://api.tiingo.com/',
        ),
        StringDataSourceConfigField(
            name='api_key',
            value='asdfghjkl',
        ),
    ),
),)


def _get_data_source_index(data_sources: tuple[DataSource, ...], uuid: UUID) -> int | None:
    for index, data_source in enumerate(data_sources):
        if data_source.uuid == uuid:
            return index
    return None


def reducer(state: tuple[DataSource, ...], action: Action) -> tuple[DataSource, ...]:
    if action.type == INIT:
        return DATA_SOURCES
    if action.type == ADD_DATA_SOURCE:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        return state + (data_source,)
    if action.type == UPDATE_DATA_SOURCE:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        index = _get_data_source_index(state, data_source.uuid)
        if index is None:
            return state
        return state[:index] + (data_source,) + state[index + 1:]
    if action.type == DELETE_DATA_SOURCE:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        index = _get_data_source_index(state, data_source.uuid)
        if index is None:
            return state
        return state[:index] + state[index + 1:]
    if action.type == MOVE_DATA_SOURCE_UP:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        index = _get_data_source_index(state, data_source.uuid)
        if index is None:
            return state
        if index > 0:
            return state[:index - 1] + (data_source, state[index - 1]) + state[index + 1:]
        return state
    if action.type == MOVE_DATA_SOURCE_DOWN:
        data_source = action.payload
        assert isinstance(data_source, DataSource)
        index = _get_data_source_index(state, data_source.uuid)
        if index is None:
            return state
        if index < len(state) - 1:
            return state[:index] + (state[index + 1], data_source) + state[index + 2:]
        return state
    return state
