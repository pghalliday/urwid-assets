import logging

from urwid import Filler, BigText, Thin6x6Font, Padding

from urwid_assets.ui.widgets.views.view import View

_LOGGER = logging.getLogger(__name__)


class SplashView(View):
    def __init__(self):
        super().__init__(Filler(Padding(BigText(u'urwid-assets', Thin6x6Font()), 'center', 'clip'), 'top'))
