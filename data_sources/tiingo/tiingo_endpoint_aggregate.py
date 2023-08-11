from _decimal import Decimal
from typing import Callable
from urllib.parse import urljoin

from aiohttp import ClientSession

from lib.asyncio.base_aggregate import BaseAggregate
from lib.data_sources.models import QueryResult

JsonSelector = Callable[[dict], str]


class TiingoEndpointAggregate(BaseAggregate[str, QueryResult, dict]):
    _base_url: str
    _api_key: str
    _url_path: str
    _json_selector: JsonSelector
    _tickers: tuple[str, ...] = tuple()

    def __init__(self,
                 base_url: str,
                 api_key: str,
                 url_path: str,
                 json_selector: JsonSelector):
        self._base_url = base_url
        self._api_key = api_key
        self._url_path = url_path
        self._json_selector = json_selector
        super().__init__(self._select_callback, self._aggregate_callback)

    async def _aggregate_callback(self) -> dict:
        url = urljoin(self._base_url, self._url_path)
        async with ClientSession() as session:
            async with session.get(url, params={
                'tickers': ','.join(self._tickers),
                'token': self._api_key,
            }, headers={
                'Content-Type': 'application/json',
            }) as response:
                return await response.json()

    def _select_callback(self, ticker: str, response: dict) -> QueryResult:
        matching_entries = tuple(filter(lambda entry: entry['ticker'] == ticker, response))
        try:
            entry = matching_entries[0]
            return QueryResult(price=Decimal(self._json_selector(entry)))
        except IndexError:
            return QueryResult(error='Ticker not found')

    async def select(self, ticker: str) -> QueryResult:
        self._tickers += (ticker,)
        return await super().select(ticker)
