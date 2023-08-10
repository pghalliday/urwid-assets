from decimal import Decimal
from random import randrange
from uuid import UUID, uuid1

from data_sources.crypto_compare.asset_crypto_compare_endpoint import CRYPTO_COMPARE_ASSET
from data_sources.crypto_compare.config_names import TSYM, FSYM
from data_sources.crypto_compare.crypto_compare import CRYPTO_COMPARE
from data_sources.tiingo.config_names import TICKER, BASE_URL, API_KEY
from data_sources.tiingo.crypto_tiingo_endpoint import TIINGO_CRYPTO
from data_sources.tiingo.forex_tiingo_endpoint import TIINGO_FOREX
from data_sources.tiingo.iex_tiingo_endpoint import TIINGO_IEX
from data_sources.tiingo.tiingo import TIINGO
from lib.data_sources.models import StringDataSourceConfig
from state.assets.assets import Asset, AssetDataSource
from state.data_sources.data_sources import DataSourceInstance
from state.state import State
from test_secrets import TIINGO_API_KEY, CRYPTO_COMPARE_API_KEY

_CRYPTO_COMPARE_DATA_SOURCE_UUID = uuid1()
_TIINGO_DATA_SOURCE_UUID = uuid1()
_DATA_SOURCES = (
    DataSourceInstance(
        uuid=_CRYPTO_COMPARE_DATA_SOURCE_UUID,
        name=u'My CryptoCompare',
        type=CRYPTO_COMPARE,
        config=(
            StringDataSourceConfig(
                name=BASE_URL,
                value='https://min-api.cryptocompare.com/',
            ),
            StringDataSourceConfig(
                name=API_KEY,
                value=CRYPTO_COMPARE_API_KEY,
            ),
        ),
    ),
    DataSourceInstance(
        uuid=_TIINGO_DATA_SOURCE_UUID,
        name=u'My Tiingo',
        type=TIINGO,
        config=(
            StringDataSourceConfig(
                name=BASE_URL,
                value='https://api.tiingo.com/',
            ),
            StringDataSourceConfig(
                name=API_KEY,
                value=TIINGO_API_KEY,
            ),
        ),
    ),
)

_CRYPTO_COMPARE_ASSET_PAIRS = tuple((CRYPTO_COMPARE_ASSET, pair) for pair in (
    ('BTC', 'EUR'),
    ('ETH', 'USD'),
    ('LTC', 'GBP'),
    ('GBP', 'EUR'),
    ('USD', 'EUR'),
    ('CAD', 'EUR'),
))
_CRYPTO_COMPARE_PAIRS = _CRYPTO_COMPARE_ASSET_PAIRS


def _crypto_compare_asset(uuid: UUID, index: int) -> Asset:
    modulo = index % len(_CRYPTO_COMPARE_PAIRS)
    (endpoint, (fsym, tsym)) = _CRYPTO_COMPARE_PAIRS[modulo]
    return Asset(
        uuid=uuid,
        name=u'CryptoCompare %s - %s' % (index, _CRYPTO_COMPARE_PAIRS[modulo]),
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        data_source=AssetDataSource(
            uuid=_CRYPTO_COMPARE_DATA_SOURCE_UUID,
            endpoint=endpoint,
            config=(
                StringDataSourceConfig(
                    name=FSYM,
                    value=fsym,
                ),
                StringDataSourceConfig(
                    name=TSYM,
                    value=tsym,
                ),
            ),
        ),
    )


_TIINGO_STOCK_TICKERS = tuple((TIINGO_IEX, ticker) for ticker in ('AAPL', 'TSLA', 'SPY', 'IVV'))
_TIINGO_FOREX_TICKERS = tuple((TIINGO_FOREX, ticker) for ticker in ('eurusd', 'eurcad', 'eurgbp'))
_TIINGO_CRYPTO_TICKERS = tuple((TIINGO_CRYPTO, ticker) for ticker in ('btcusd', 'ethusd', 'ltcusd'))
_TIINGO_TICKERS = _TIINGO_STOCK_TICKERS + _TIINGO_FOREX_TICKERS + _TIINGO_CRYPTO_TICKERS


def _tingo_asset(uuid: UUID, index: int) -> Asset:
    modulo = index % len(_TIINGO_TICKERS)
    (endpoint, ticker) = _TIINGO_TICKERS[modulo]
    return Asset(
        uuid=uuid,
        name=u'Tiingo %s - %s' % (index, _TIINGO_TICKERS[modulo]),
        amount=Decimal(randrange(1, 10000000000)) / 10000,
        data_source=AssetDataSource(
            uuid=_TIINGO_DATA_SOURCE_UUID,
            endpoint=endpoint,
            config=(StringDataSourceConfig(
                name=TICKER,
                value=ticker,
            ),),
        ),
    )


_CRYPTO_COMPARE_IDS = tuple((uuid1(), index) for index in range(10))
_CRYPTO_COMPARE_ASSETS = tuple(_crypto_compare_asset(uuid, index) for uuid, index in _CRYPTO_COMPARE_IDS)

_TIINGO_IDS = tuple((uuid1(), index) for index in range(10))
_TIINGO_ASSETS = tuple(_tingo_asset(uuid, index) for uuid, index in _TIINGO_IDS)

_ASSETS = _CRYPTO_COMPARE_ASSETS + _TIINGO_ASSETS

_SNAPSHOTS = tuple()

INITIAL_STATE = State(
    assets=_ASSETS,
    data_sources=_DATA_SOURCES,
    snapshots=_SNAPSHOTS,
)
