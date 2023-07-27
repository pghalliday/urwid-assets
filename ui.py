import urwid
import widgets
import data


class UI:
    def __init__(self, assets: data.Assets) -> None:
        self.top = widgets.Layout(assets)

    def start(self) -> None:
        urwid.MainLoop(self.top,
                       palette=[('reversed', 'standout', '')],
                       unhandled_input=self.global_keys).run()

    def global_keys(self, key: str) -> None:
        if key in ('q', 'Q'):
            self.stop()

    def stop(self) -> None:
        raise urwid.ExitMainLoop()
