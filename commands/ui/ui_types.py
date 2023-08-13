from typing import NewType

from commands.ui.widgets.views.placeholder_view import PlaceholderView

ContentView = NewType('ContentView', PlaceholderView)
ShowLogPanel = NewType('ShowLogPanel', bool)
