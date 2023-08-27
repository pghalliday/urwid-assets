import logging
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from urwid_assets.lib.redux.reducer import Action, ActionTypeFactory, INIT

_LOGGER = logging.getLogger(__name__)

_ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

SET_TARGET_SYMBOL = _ACTION_TYPE_FACTORY.create('SET_TARGET_SYMBOL')
SET_TIMESTAMP = _ACTION_TYPE_FACTORY.create('SET_TIMESTAMP')
SET_LAST_UPDATE_TIME = _ACTION_TYPE_FACTORY.create('SET_LAST_UPDATE_TIME')
START_LOADING_RATES = _ACTION_TYPE_FACTORY.create('START_LOADING_RATES')
SET_LOADED_RATE = _ACTION_TYPE_FACTORY.create('SET_LOADED_RATE')


class UnknownLoadedRate(Exception):
    def __init__(self, uuid: UUID):
        super().__init__(u'Unknown loaded rate: %s' % uuid)
        self.uuid = uuid


@dataclass(frozen=True)
class LoadedRate:
    uuid: UUID
    rate: Decimal | None
    error: str | None


def get_loaded_rate(uuid: UUID, loaded_rates: tuple[LoadedRate, ...]) -> LoadedRate | None:
    for loaded_rate in loaded_rates:
        if loaded_rate.uuid == uuid:
            return loaded_rate
    raise UnknownLoadedRate(uuid)


def _get_index_of_loaded_rate(uuid: UUID, loaded_rates: tuple[LoadedRate, ...]) -> int:
    for index, loaded_rate in enumerate(loaded_rates):
        if loaded_rate.uuid == uuid:
            return index
    raise UnknownLoadedRate(uuid)


def _set_loaded_rate(loaded_rate: LoadedRate, loaded_rates: tuple[LoadedRate, ...]) -> tuple[LoadedRate, ...]:
    try:
        index = _get_index_of_loaded_rate(loaded_rate.uuid, loaded_rates)
    except UnknownLoadedRate:
        return loaded_rates + (loaded_rate,)
    return loaded_rate[:index] + (loaded_rate,) + loaded_rate[index + 1:]


@dataclass(frozen=True)
class UI:
    target_symbol: UUID | None = None
    timestamp: datetime | None = None
    last_update_time: datetime | None = None
    loaded_rates: tuple[LoadedRate, ...] = tuple()


def reducer(ui: UI, action: Action) -> UI:
    if action.type == INIT:
        return UI()
    if action.type == SET_TARGET_SYMBOL:
        target_symbol = action.payload
        assert isinstance(target_symbol, UUID)
        return replace(ui, target_symbol=target_symbol)
    if action.type == SET_TIMESTAMP:
        timestamp = action.payload
        assert isinstance(timestamp, datetime | None)
        return replace(ui, timestamp=timestamp, loaded_rates=tuple())
    if action.type == SET_LAST_UPDATE_TIME:
        last_update_time = action.payload
        assert isinstance(last_update_time, datetime | None)
        return replace(ui, last_update_time=last_update_time)
    if action.type == START_LOADING_RATES:
        return replace(ui, loaded_rates=tuple())
    if action.type == SET_LOADED_RATE:
        loaded_rate = action.payload
        assert isinstance(loaded_rate, LoadedRate)
        return replace(ui, loaded_rates=_set_loaded_rate(loaded_rate, ui.loaded_rates))
    return ui
