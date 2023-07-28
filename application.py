from dataclasses import dataclass

from injector import inject
from urwid import ExitMainLoop, MainLoop

from controllers.ui_controller import UIController
from views.current_view import CurrentView


@inject
@dataclass
class Application:
    ui_manager: UIController
    current_view: CurrentView

    def global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise ExitMainLoop()

    def start(self) -> None:
        self.ui_manager.set_view(self.current_view)
        MainLoop(self.ui_manager,
                 palette=[
                     ('reversed', 'standout', ''),
                     ('popup-bg', 'white', 'dark blue'),
                 ],
                 unhandled_input=self.global_keys,
                 pop_ups=True).run()
