from decimal import Decimal
from random import randrange
from uuid import uuid1, UUID

from state.models import Asset, Assets, State, AssetsFile


def asset(uuid: UUID, index: int) -> Asset:
    return Asset(
        uuid=uuid,
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        price_source=u'test'
    )


ASSETS_FILE: AssetsFile = AssetsFile(
    path='path',
    passphrase='passphrase',
)
IDS = tuple((uuid1(), index) for index in range(5))
CURRENT = tuple(asset(uuid, index) for uuid, index in IDS)
SNAPSHOTS = tuple()
ASSETS: Assets = Assets(
    current=CURRENT,
    snapshots=SNAPSHOTS,
)
STATE: State = State(
    assets_file=ASSETS_FILE,
    assets=ASSETS,
)
