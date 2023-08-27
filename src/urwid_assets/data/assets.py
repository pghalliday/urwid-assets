from _decimal import Decimal
from random import randrange
from uuid import uuid1, UUID

from urwid_assets.data.symbols import SYMBOLS
from urwid_assets.state.saved.assets.assets import Asset


def _asset(uuid: UUID, index: int) -> Asset:
    modulo = index % len(SYMBOLS)
    return Asset(
        uuid=uuid,
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        symbol=SYMBOLS[modulo].uuid,
    )


_ASSET_IDS = tuple((uuid1(), index) for index in range(20))

ASSETS = tuple(_asset(uuid, index) for uuid, index in _ASSET_IDS)
