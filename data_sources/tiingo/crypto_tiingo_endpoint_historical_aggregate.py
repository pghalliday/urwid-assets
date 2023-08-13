from _decimal import Decimal
from datetime import datetime
from typing import Callable
from urllib.parse import urljoin

from aiohttp import ClientSession

from lib.asyncio.base_aggregate import BaseAggregate
from lib.data_sources.models import QueryResult

JsonSelector = Callable[[dict], str]


def _select_callback(ticker: str, response: dict) -> QueryResult:
    try:
        matching_entries = tuple(filter(lambda entry: entry['ticker'] == ticker, response))
        entry = matching_entries[0]
        return QueryResult(price=Decimal(entry['priceData'][0]['open']))
    except (IndexError, KeyError, TypeError):
        return QueryResult(error='Something went wrong')


class CryptoTiingoEndpointHistoricalAggregate(BaseAggregate[str, QueryResult, dict]):
    def __init__(self,
                 timestamp: datetime,
                 base_url: str,
                 api_key: str):
        self._timestamp = timestamp
        self._base_url = base_url
        self._api_key = api_key
        self._tickers: tuple[str, ...] = tuple()
        super().__init__(_select_callback, self._aggregate_callback)

    async def _aggregate_callback(self) -> dict:
        url = urljoin(self._base_url, '/tiingo/crypto/prices')
        async with ClientSession() as session:
            async with session.get(url, params={
                'tickers': ','.join(self._tickers),
                'startDate': self._timestamp.date().isoformat(),
                'endDate': self._timestamp.date().isoformat(),
                'resampleFreq': '24hour',
                'token': self._api_key,
            }, headers={
                'Content-Type': 'application/json',
            }) as response:
                return await response.json()

    async def select(self, ticker: str) -> QueryResult:
        self._tickers += (ticker,)
        return await super().select(ticker)
