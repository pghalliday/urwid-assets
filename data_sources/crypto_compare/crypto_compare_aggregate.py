from asyncio import TaskGroup

from data_sources.crypto_compare.config_names import FSYM, TSYM
from data_sources.crypto_compare.crypto_compare_endpoint import CryptoCompareEndpoint
from data_sources.crypto_compare.crypto_compare_endpoint_aggregate import CryptoCompareEndpointAggregate
from lib.data_sources.data_source_aggregate import DataSourceAggregate
from lib.data_sources.models import get_string_from_config, Query, QueryResult


class CryptoCompareAggregate(DataSourceAggregate):
    _aggregates: dict[str, CryptoCompareEndpointAggregate]

    def __init__(self,
                 base_url: str,
                 api_key: str,
                 endpoints: tuple[CryptoCompareEndpoint, ...]) -> None:
        # create aggregates for each endpoint
        self._aggregates = {endpoint.get_name(): endpoint.create_aggregate(base_url, api_key)
                            for endpoint in endpoints}

    async def select(self, query: Query) -> QueryResult:
        fsym = get_string_from_config(FSYM, query.config)
        tsym = get_string_from_config(TSYM, query.config)
        return await self._aggregates[query.endpoint].select((fsym, tsym))

    async def run(self) -> None:
        async with TaskGroup() as tg:
            for aggregate in self._aggregates.values():
                tg.create_task(aggregate.run())
