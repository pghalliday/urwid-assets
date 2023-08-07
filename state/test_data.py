from decimal import Decimal
from random import randrange
from uuid import uuid1, UUID

from state.models import Asset, AssetDataSource, StringAssetDataSourceConfig


def asset(uuid: UUID, index: int) -> Asset:
    return Asset(
        uuid=uuid,
        name=u'Asset %s' % index,
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        data_source=AssetDataSource(
            name='tiingo',
            endpoint='iex',
            config=(StringAssetDataSourceConfig(
                name='ticker',
                value='AAPL%s' % index,
            ),)
        ),
        price=Decimal(-1)
    )


IDS = tuple((uuid1(), index) for index in range(5))
CURRENT = tuple(asset(uuid, index) for uuid, index in IDS)
