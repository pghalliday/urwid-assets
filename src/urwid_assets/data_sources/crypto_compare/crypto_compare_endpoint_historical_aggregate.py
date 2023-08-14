from datetime import datetime
from urllib.parse import urljoin

from aiohttp import ClientSession

from urwid_assets.lib.asyncio.aggregate import Aggregate
from urwid_assets.lib.data_sources.models import QueryResult
from urwid_assets.lib.json.decimal_decoder import loads_with_decimal


class CryptoCompareEndpointHistoricalAggregate(Aggregate[tuple[str, str], QueryResult, None]):
    def __init__(self,
                 timestamp: datetime,
                 base_url: str,
                 api_key: str,
                 url_path: str):
        self._timestamp = timestamp
        self._base_url = base_url
        self._api_key = api_key
        self._url_path = url_path

    async def select(self, pair: (str, str)) -> QueryResult:
        url = urljoin(self._base_url, self._url_path)
        (fsym, tsym) = pair
        async with ClientSession() as session:
            async with session.get(url, params={
                'fsym': fsym,
                'tsyms': tsym,
                'ts': self._timestamp.timestamp(),
                'api_key': self._api_key,
            }, headers={
                'Content-Type': 'application/json',
            }) as response:
                json = await response.json(loads=loads_with_decimal)
                try:
                    return QueryResult(price=json[fsym][tsym])
                except (KeyError, IndexError, TypeError):
                    return QueryResult(error='Something went wrong')
