from uuid import uuid1, UUID

from urwid_assets.data.data_sources import _CRYPTO_COMPARE_DATA_SOURCE_UUID, _TIINGO_DATA_SOURCE_UUID
from urwid_assets.data.symbols import BTC, EUR, ETH, USD, LTC, GBP, CAD, AAPL, TSLA, SPY, IVV
from urwid_assets.data_sources.crypto_compare.asset_crypto_compare_endpoint import CRYPTO_COMPARE_ASSET
from urwid_assets.data_sources.crypto_compare.config_names import FSYM, TSYM
from urwid_assets.data_sources.tiingo.config_names import TICKER
from urwid_assets.data_sources.tiingo.crypto_tiingo_endpoint import TIINGO_CRYPTO
from urwid_assets.data_sources.tiingo.forex_tiingo_endpoint import TIINGO_FOREX
from urwid_assets.data_sources.tiingo.iex_tiingo_endpoint import TIINGO_IEX
from urwid_assets.lib.data_sources.models import StringDataSourceConfig
from urwid_assets.state.saved.rates.rates import Rate

_CRYPTO_COMPARE_ASSET_PAIRS = tuple((CRYPTO_COMPARE_ASSET, pair) for pair in (
    (('BTC', BTC), ('EUR', EUR)),
    (('ETH', ETH), ('USD', USD)),
    (('LTC', LTC), ('GBP', GBP)),
    (('GBP', GBP), ('EUR', EUR)),
    (('USD', USD), ('EUR', EUR)),
    (('CAD', CAD), ('EUR', EUR)),
))
_CRYPTO_COMPARE_PAIRS = _CRYPTO_COMPARE_ASSET_PAIRS


def _crypto_compare_rate(uuid: UUID, index: int) -> Rate:
    modulo = index % len(_CRYPTO_COMPARE_PAIRS)
    (endpoint, ((fsym, from_symbol), (tsym, to_symbol))) = _CRYPTO_COMPARE_PAIRS[modulo]
    return Rate(
        uuid=uuid,
        name=u'CryptoCompare %s' % index,
        cost=10,
        from_symbol=from_symbol.uuid,
        to_symbol=to_symbol.uuid,
        data_source=_CRYPTO_COMPARE_DATA_SOURCE_UUID,
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
    )


_CRYPTO_COMPARE_IDS = tuple((uuid1(), index) for index in range(10))
_CRYPTO_COMPARE_RATES = tuple(_crypto_compare_rate(uuid, index) for uuid, index in _CRYPTO_COMPARE_IDS)

_TIINGO_STOCK_TICKERS = tuple(
    (TIINGO_IEX, ticker) for ticker in (('AAPL', AAPL, USD), ('TSLA', TSLA, USD), ('SPY', SPY, USD), ('IVV', IVV, USD)))
_TIINGO_FOREX_TICKERS = tuple(
    (TIINGO_FOREX, ticker) for ticker in (('eurusd', EUR, USD), ('eurcad', EUR, CAD), ('eurgbp', EUR, GBP)))
_TIINGO_CRYPTO_TICKERS = tuple(
    (TIINGO_CRYPTO, ticker) for ticker in (('btcusd', BTC, USD), ('ethusd', ETH, USD), ('ltcusd', LTC, USD)))
_TIINGO_TICKERS = _TIINGO_STOCK_TICKERS + _TIINGO_FOREX_TICKERS + _TIINGO_CRYPTO_TICKERS


def _tingo_rate(uuid: UUID, index: int) -> Rate:
    modulo = index % len(_TIINGO_TICKERS)
    (endpoint, (ticker, from_symbol, to_symbol)) = _TIINGO_TICKERS[modulo]
    return Rate(
        uuid=uuid,
        name=u'Tiingo %s' % index,
        cost=20,
        from_symbol=from_symbol.uuid,
        to_symbol=to_symbol.uuid,
        data_source=_TIINGO_DATA_SOURCE_UUID,
        endpoint=endpoint,
        config=(StringDataSourceConfig(
            name=TICKER,
            value=ticker,
        ),),
    )


_TIINGO_IDS = tuple((uuid1(), index) for index in range(10))
_TIINGO_RATES = tuple(_tingo_rate(uuid, index) for uuid, index in _TIINGO_IDS)

RATES = _CRYPTO_COMPARE_RATES + _TIINGO_RATES
