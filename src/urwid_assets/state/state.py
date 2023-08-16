import logging
from dataclasses import dataclass

from urwid_assets.lib.redux.reducer import combine_reducers, ReducerMapping, ActionTypeFactory, Action
from urwid_assets.lib.serialization.serialization import serializable
from urwid_assets.state.assets.assets import Asset, reducer as assets_reducer
from urwid_assets.state.data_sources.data_sources import DataSourceInstance, reducer as data_sources_reducer
from urwid_assets.state.snapshots.snapshots import Snapshot, reducer as snapshots_reducer

LOGGER = logging.getLogger(__name__)

_ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

SET_STATE = _ACTION_TYPE_FACTORY.create('SET_STATE')


@serializable()
@dataclass(frozen=True)
class State:
    data_sources: tuple[DataSourceInstance, ...]
    assets: tuple[Asset, ...]
    snapshots: tuple[Snapshot, ...]


_reducer = combine_reducers(State, (
    ReducerMapping('data_sources', data_sources_reducer),
    ReducerMapping('assets', assets_reducer),
    ReducerMapping('snapshots', snapshots_reducer),
))


def reducer(state: State, action: Action) -> State:
    if action.type == SET_STATE:
        state = action.payload
        assert isinstance(state, State)
        return state
    return _reducer(state, action)
