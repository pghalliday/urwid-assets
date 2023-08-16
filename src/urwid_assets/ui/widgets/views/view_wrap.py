from urwid_assets.ui.widgets.views.view import View


class ViewWrap(View):
    def __init__(self, view: View):
        self._view = view
        super().__init__(view)

    def activate(self) -> None:
        self._view.activate()

    def deactivate(self) -> None:
        self.view.deactivate()
