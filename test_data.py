from decimal import Decimal
from random import randrange
from uuid import uuid1

from data import Asset, Snapshot, Assets


def asset(index: int) -> Asset:
    return Asset(
        id=uuid1(),
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        price_source=u'test'
    )


CURRENT: list[Asset] = [asset(index) for index in range(50)]
SNAPSHOTS: list[Snapshot] = []
ASSETS: Assets = Assets(
    current=CURRENT,
    snapshots=SNAPSHOTS,
)
