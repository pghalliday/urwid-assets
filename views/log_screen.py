import logging

from injector import singleton
from urwid import LineBox

from lib.widgets.text_list import TextList
from lib.widgets.view import View


class _LoggingHandler(logging.Handler):
    _text_list: TextList

    def __init__(self, text_list: TextList) -> None:
        self._text_list = text_list
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(levelname)s: %(name)s: %(message)s'))

    def emit(self, record: logging.LogRecord) -> None:
        self._text_list.append(self.format(record))


@singleton
class LogScreen(View):
    def __init__(self):
        text_list = TextList()
        super().__init__(LineBox(text_list))
        logging.getLogger().addHandler(_LoggingHandler(text_list))
