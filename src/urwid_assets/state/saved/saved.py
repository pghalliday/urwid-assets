import logging
from dataclasses import dataclass

from urwid_assets.lib.redux.reducer import combine_reducers, ReducerMapping, ActionTypeFactory, Action
from urwid_assets.lib.serialization.serialization import serializable
from urwid_assets.state.saved.assets.assets import Asset, reducer as assets_reducer
from urwid_assets.state.saved.data_sources.data_sources import DataSourceInstance, reducer as data_sources_reducer
from urwid_assets.state.saved.rates.rates import Rate, reducer as rates_reducer
from urwid_assets.state.saved.snapshots.snapshots import Snapshot, reducer as snapshots_reducer
from urwid_assets.state.saved.symbols.symbols import Symbol, reducer as symbols_reducer

LOGGER = logging.getLogger(__name__)

_ACTION_TYPE_FACTORY = ActionTypeFactory(__name__)

SET_SAVED = _ACTION_TYPE_FACTORY.create('SET_SAVED')


@serializable()
@dataclass(frozen=True)
class Saved:
    data_sources: tuple[DataSourceInstance, ...]
    symbols: tuple[Symbol, ...]
    rates: tuple[Rate, ...]
    assets: tuple[Asset, ...]
    snapshots: tuple[Snapshot, ...]
    version: int = 1


_reducer = combine_reducers(Saved, (
    ReducerMapping('data_sources', data_sources_reducer),
    ReducerMapping('symbols', symbols_reducer),
    ReducerMapping('rates', rates_reducer),
    ReducerMapping('assets', assets_reducer),
    ReducerMapping('snapshots', snapshots_reducer),
))


def reducer(saved: Saved, action: Action) -> Saved:
    if action.type == SET_SAVED:
        saved = action.payload
        assert isinstance(saved, Saved)
        return saved
    return _reducer(saved, action)
