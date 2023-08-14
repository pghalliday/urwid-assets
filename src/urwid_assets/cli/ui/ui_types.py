from typing import NewType

from urwid_assets.ui.widgets.views.placeholder_view import PlaceholderView

ContentView = NewType('ContentView', PlaceholderView)
ShowLogPanel = NewType('ShowLogPanel', bool)
