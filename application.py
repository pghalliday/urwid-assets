from dataclasses import dataclass

from urwid import ExitMainLoop, MainLoop

from data_manager import DataManager
from ui_manager import UIManager
from widgets import Layout


@dataclass
class Application:
    data_manager: DataManager
    ui_manager: UIManager

    def global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise ExitMainLoop()

    def start(self) -> None:
        self.ui_manager.register_view('current', lambda current: Layout(current, self.ui_manager))
        self.ui_manager.switch_to_view('current', self.data_manager.get_current())
        MainLoop(self.ui_manager,
                 palette=[
                     ('reversed', 'standout', ''),
                     ('popup-bg', 'white', 'dark blue'),
                 ],
                 unhandled_input=self.global_keys,
                 pop_ups=True).run()
