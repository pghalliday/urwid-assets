from dataclasses import dataclass

from urwid_assets.lib.redux.reducer import combine_reducers, ReducerMapping
from urwid_assets.state.saved.saved import Saved, reducer as saved_reducer
from urwid_assets.state.ui.ui import UI, reducer as ui_reducer


@dataclass(frozen=True)
class State:
    saved: Saved
    ui: UI


reducer = combine_reducers(State, (
    ReducerMapping('saved', saved_reducer),
    ReducerMapping('ui', ui_reducer),
))
