import urwid
import widgets


class UI:
    def __init__(self):
        self.top = widgets.Layout()

    def start(self):
        urwid.MainLoop(self.top,
                       palette=[('reversed', 'standout', '')],
                       unhandled_input=self.global_keys).run()

    def global_keys(self, key):
        if key in ('q', 'Q'):
            self.stop()

    def stop(self):
        raise urwid.ExitMainLoop()
