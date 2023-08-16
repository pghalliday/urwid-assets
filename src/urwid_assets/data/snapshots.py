from datetime import datetime
from decimal import Decimal
from random import randrange
from uuid import uuid1

from dateutil.relativedelta import relativedelta

from urwid_assets.state.snapshots.snapshots import Snapshot, AssetSnapshot


def _create_asset_snapshot(snapshot_index: int, index: int) -> AssetSnapshot:
    return AssetSnapshot(
        uuid=uuid1(),
        name=u'Asset %s - %s' % (snapshot_index, index),
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        price=Decimal(randrange(1, 1000000)) / 10000,
    )


def _create_snapshot(index: int) -> Snapshot:
    return Snapshot(
        uuid=uuid1(),
        name=u'Snapshot %s' % index,
        timestamp=datetime.now() - relativedelta(years=index),
        assets=tuple(_create_asset_snapshot(index, asset_index) for asset_index in range(10)),
    )


SNAPSHOTS = tuple(_create_snapshot(index) for index in range(10))
