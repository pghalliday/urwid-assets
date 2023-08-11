from datetime import datetime

from data_sources.crypto_compare.config_names import FSYM, TSYM
from data_sources.crypto_compare.crypto_compare_endpoint import CryptoCompareEndpoint
from lib.data_sources.data_source_aggregate import DataSourceAggregate
from lib.data_sources.models import get_string_from_config, Query, QueryResult


class CryptoCompareHistoricalAggregate(DataSourceAggregate):
    def __init__(self,
                 timestamp: datetime,
                 base_url: str,
                 api_key: str,
                 endpoints: tuple[CryptoCompareEndpoint, ...]) -> None:
        # create aggregates for each endpoint
        self._aggregates = {endpoint.get_name(): endpoint.create_historical_aggregate(timestamp, base_url, api_key)
                            for endpoint in endpoints}

    async def select(self, query: Query) -> QueryResult:
        fsym = get_string_from_config(FSYM, query.config)
        tsym = get_string_from_config(TSYM, query.config)
        return await self._aggregates[query.endpoint].select((fsym, tsym))