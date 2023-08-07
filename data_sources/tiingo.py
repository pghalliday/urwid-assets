from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from lib.data_source import DataSource, DataSourceConfigField, \
    DataSourceEndpoint, StringDataSourceConfigField
from lib.redux.store import Store
from state import State
from state.assets import Asset

_API_KEY = 'api_key'
_BASE_URL = 'base_url'
_TICKER = 'ticker'

_IEX = 'iex'
_FOREX = 'forex'
_CRYPTO = 'crypto'


@dataclass(frozen=True)
class _Query:
    ticker: str


class Tiingo(DataSource):
    @inject
    def __init__(self, store: Store[State]):
        super().__init__(store)

    def _update(self) -> None:
        pass

    def get_name(self) -> str:
        return 'tiingo'

    def get_display_name(self) -> str:
        return u'Tiingo'

    def get_global_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=_BASE_URL,
                display_name=u'Base URL',
                default='https://api.tiingo.com/',
            ),
            StringDataSourceConfigField(
                name=_API_KEY,
                display_name=u'API Key',
                default='',
                secret=True,
            ),
        )

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        return (
            DataSourceEndpoint(
                name=_IEX,
                display_name=u'IEX',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_TICKER,
                        display_name=u'Ticker',
                        default='',
                    ),
                )
            ),
            DataSourceEndpoint(
                name=_FOREX,
                display_name=u'Forex',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_TICKER,
                        display_name=u'Ticker',
                        default='',
                    ),
                )
            ),
            DataSourceEndpoint(
                name=_CRYPTO,
                display_name=u'Crypto',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_TICKER,
                        display_name=u'Ticker',
                        default='',
                    ),
                )
            ),
        )

    def before_query(self, timestamp: str | None = None) -> None:
        pass

    def query(self, asset: Asset, timestamp: str | None = None) -> Decimal:
        pass
