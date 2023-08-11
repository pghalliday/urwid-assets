from state.state import State
from test_data.assets import ASSETS
from test_data.data_sources import DATA_SOURCES
from test_data.snapshots import SNAPSHOTS

INITIAL_STATE = State(
    assets=ASSETS,
    data_sources=DATA_SOURCES,
    snapshots=SNAPSHOTS,
)
