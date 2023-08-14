from urllib.parse import urljoin

from aiohttp import ClientSession

from urwid_assets.lib.asyncio.base_aggregate import BaseAggregate
from urwid_assets.lib.data_sources.models import QueryResult
from urwid_assets.lib.json.decimal_decoder import loads_with_decimal


def _select_callback(pair: (str, str), response: dict) -> QueryResult:
    (fsym, tsym) = pair
    try:
        return QueryResult(price=response[fsym][tsym])
    except (KeyError, TypeError, IndexError):
        return QueryResult(error='Something went wrong')


class CryptoCompareEndpointAggregate(BaseAggregate[tuple[str, str], QueryResult, dict]):
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 url_path: str):
        self._pairs: tuple[(str, str), ...] = tuple()
        self._base_url = base_url
        self._api_key = api_key
        self._url_path = url_path
        super().__init__(_select_callback, self._aggregate_callback)

    async def _aggregate_callback(self) -> dict:
        url = urljoin(self._base_url, self._url_path)
        (fsyms, tsyms) = tuple(zip(*self._pairs))
        fsyms = set(fsyms)
        tsyms = set(tsyms)
        async with ClientSession() as session:
            async with session.get(url, params={
                'fsyms': ','.join(fsyms),
                'tsyms': ','.join(tsyms),
                'api_key': self._api_key,
            }, headers={
                'Content-Type': 'application/json',
            }) as response:
                return await response.json(loads=loads_with_decimal)

    async def select(self, pair: (str, str)) -> QueryResult:
        self._pairs += (pair,)
        return await super().select(pair)
