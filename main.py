from random import randrange
from uuid import uuid1

import ui
import data


def asset(index: int) -> data.Asset:
    return data.Asset(
        id=uuid1(),
        name=u'Asset %s' % index,
        amount=randrange(1, 1000000),
        price_source=u'test'
    )


CURRENT: list[data.Asset] = [asset(index) for index in range(50)]
SNAPSHOTS: list[data.Snapshot] = []
ASSETS: data.Assets = data.Assets(
    current=CURRENT,
    snapshots=SNAPSHOTS,
)

if __name__ == '__main__':
    ui.UI(ASSETS).start()
