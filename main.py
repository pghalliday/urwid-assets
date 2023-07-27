from uimanager import UIManager
from random import randrange
from uuid import uuid1
from decimal import Decimal
from widgets import Layout

import urwid
import data


def asset(index: int) -> data.Asset:
    return data.Asset(
        id=uuid1(),
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        price_source=u'test'
    )


CURRENT: list[data.Asset] = [asset(index) for index in range(50)]
SNAPSHOTS: list[data.Snapshot] = []
ASSETS: data.Assets = data.Assets(
    current=CURRENT,
    snapshots=SNAPSHOTS,
)


def global_keys(key: str) -> None:
    if key in ('q', 'Q'):
        stop()


def stop() -> None:
    raise urwid.ExitMainLoop()


def start() -> None:
    ui = UIManager()
    ui.register_view('current', Layout(ASSETS))
    ui.switch_to_view('current')
    urwid.MainLoop(ui,
                   palette=[
                       ('reversed', 'standout', ''),
                       ('popup-bg', 'white', 'dark blue'),
                   ],
                   unhandled_input=global_keys,
                   pop_ups=True).run()


if __name__ == '__main__':
    start()
