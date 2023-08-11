from asyncio import TaskGroup
from datetime import datetime

from data_sources.tiingo.config_names import TICKER
from data_sources.tiingo.tiingo_endpoint import TiingoEndpoint
from lib.data_sources.data_source_aggregate import DataSourceAggregate
from lib.data_sources.models import get_string_from_config, Query, QueryResult


class TiingoHistoricalAggregate(DataSourceAggregate):

    def __init__(self,
                 timestamp: datetime,
                 base_url: str,
                 api_key: str,
                 endpoints: tuple[TiingoEndpoint, ...]) -> None:
        # create aggregates for each endpoint
        self._aggregates = {endpoint.get_name(): endpoint.create_historical_aggregate(timestamp, base_url, api_key)
                            for endpoint in endpoints}

    async def select(self, query: Query) -> QueryResult:
        return await self._aggregates[query.endpoint].select(get_string_from_config(TICKER, query.config))

    async def run(self) -> None:
        async with TaskGroup() as tg:
            for aggregate in self._aggregates.values():
                tg.create_task(aggregate.run())
