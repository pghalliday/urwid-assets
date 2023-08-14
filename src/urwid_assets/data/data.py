from urwid_assets.data.assets import ASSETS
from urwid_assets.data.data_sources import DATA_SOURCES
from urwid_assets.data.snapshots import SNAPSHOTS
from urwid_assets.state.state import State

INITIAL_STATE = State(
    assets=ASSETS,
    data_sources=DATA_SOURCES,
    snapshots=SNAPSHOTS,
)
