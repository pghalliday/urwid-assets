from _decimal import Decimal
from datetime import datetime
from typing import Callable
from urllib.parse import urljoin

from aiohttp import ClientSession

from lib.asyncio.aggregate import Aggregate
from lib.data_sources.models import QueryResult

JsonSelector = Callable[[dict], str]


class TiingoEndpointHistoricalAggregate(Aggregate[str, QueryResult, None]):
    def __init__(self,
                 timestamp: datetime,
                 base_url: str,
                 api_key: str,
                 url_path: str,
                 json_selector: JsonSelector):
        self._timestamp = timestamp
        self._base_url = base_url
        self._api_key = api_key
        self._url_path = url_path
        self._json_selector = json_selector

    async def select(self, ticker: str) -> QueryResult:
        url = urljoin(self._base_url, '%s/%s/prices' % (self._url_path, ticker))
        async with ClientSession() as session:
            async with session.get(url, params={
                'startDate': self._timestamp.date().isoformat(),
                'endDate': self._timestamp.date().isoformat(),
                'resampleFreq': '24hour',
                'token': self._api_key,
            }, headers={
                'Content-Type': 'application/json',
            }) as response:
                json = await response.json()
                try:
                    return QueryResult(price=Decimal(self._json_selector(json)))
                except (IndexError, KeyError, TypeError):
                    return QueryResult(error='Something went wrong')
