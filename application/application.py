from asyncio import AbstractEventLoop

from injector import inject
from urwid import ExitMainLoop, MainLoop, AsyncioEventLoop

from encryption.encryption import Encryption
from lib.data_sources.data_source import DataSource
from views.application_view import ApplicationView


class Application:
    _application_view: ApplicationView
    _loop: AbstractEventLoop
    _encryption: Encryption
    _data_sources: tuple[DataSource, ...]

    @inject
    def __init__(self,
                 application_view: ApplicationView,
                 loop: AbstractEventLoop,
                 encryption: Encryption,
                 data_sources: tuple[DataSource, ...]) -> None:
        self._application_view = application_view
        self._loop = loop
        self._encryption = encryption
        self._data_sources = data_sources

    def global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise ExitMainLoop()

    def start(self) -> None:
        self._application_view.activate()
        MainLoop(self._application_view,
                 event_loop=AsyncioEventLoop(loop=self._loop),
                 palette=[
                     ('reversed', 'standout', ''),
                 ],
                 unhandled_input=self.global_keys,
                 pop_ups=True).run()
