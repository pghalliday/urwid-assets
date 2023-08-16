from asyncio import AbstractEventLoop

from injector import inject
from urwid import ExitMainLoop, MainLoop, AsyncioEventLoop

from urwid_assets.ui.views.ui_view import UIView


class UI:
    @inject
    def __init__(self,
                 ui_view: UIView,
                 loop: AbstractEventLoop) -> None:
        ui_view.activate()
        MainLoop(ui_view,
                 event_loop=AsyncioEventLoop(loop=loop),
                 palette=[
                     ('reversed', 'standout', ''),
                 ],
                 unhandled_input=self._global_keys,
                 pop_ups=True).run()

    def _global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise ExitMainLoop()
