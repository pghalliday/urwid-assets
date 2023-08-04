from injector import inject
from urwid import ExitMainLoop, MainLoop

from views.application_root import ApplicationRoot


class Application:
    _application_root: ApplicationRoot

    @inject
    def __init__(self, application_root: ApplicationRoot):
        self._application_root = application_root

    def global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise ExitMainLoop()

    def start(self) -> None:
        self._application_root.activate()
        MainLoop(self._application_root,
                 palette=[
                     ('reversed', 'standout', ''),
                 ],
                 unhandled_input=self.global_keys).run()
