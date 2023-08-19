from urwid_assets.data.assets import ASSETS
from urwid_assets.data.data_sources import DATA_SOURCES
from urwid_assets.data.rates import RATES
from urwid_assets.data.snapshots import SNAPSHOTS
from urwid_assets.data.symbols import SYMBOLS
from urwid_assets.state.saved.saved import Saved
from urwid_assets.state.state import State
from urwid_assets.state.ui.ui import UI

INITIAL_SAVED = Saved(
    symbols=SYMBOLS,
    rates=RATES,
    assets=ASSETS,
    data_sources=DATA_SOURCES,
    snapshots=SNAPSHOTS,
)

INITIAL_STATE = State(
    saved=INITIAL_SAVED,
    ui=UI(),
)
