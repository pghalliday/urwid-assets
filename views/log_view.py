import logging
import subprocess

from injector import singleton
from urwid import LineBox

from lib.widgets.text_list import TextList
from lib.widgets.views.view import View


class _LoggingHandler(logging.Handler):
    _text_list: TextList

    def __init__(self, text_list: TextList) -> None:
        self._text_list = text_list
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(levelname)s: %(name)s: %(message)s'))

    def emit(self, record: logging.LogRecord) -> None:
        self._text_list.append(self.format(record))


@singleton
class LogView(View):
    _text_list: TextList

    def __init__(self):
        self._text_list = TextList()
        super().__init__(LineBox(self._text_list))
        logging.getLogger().addHandler(_LoggingHandler(self._text_list))

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('y', 'Y'):
            subprocess.run("pbcopy", text=True, input=self._text_list.get_selected_text())
            return None
        return key
