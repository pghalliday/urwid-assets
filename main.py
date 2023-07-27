from random import randrange
from uuid import uuid1
from decimal import Decimal

import ui
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

if __name__ == '__main__':
    ui.UI(ASSETS).start()
