from urwid import SolidFill

from lib.widgets.view import View


class SplashScreen(View):
    def __init__(self):
        super().__init__(SolidFill(u'#'))
