from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid1

from lib.data_source.data_source import DataSource, DataSourceConfigField, \
    DataSourceEndpoint, StringDataSourceConfigField, DataSourceConfig

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
    _base_url: str
    _api_key: str
    _queries: dict[str, dict[UUID, _Query]]

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
            ),
        )

    def set_global_config(self, config: tuple[DataSourceConfig, ...]) -> None:
        config_dict = {data_source_config.name: data_source_config.value for data_source_config in config}
        self._base_url = config_dict[_BASE_URL]
        self._api_key = config_dict[_API_KEY]

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

    def register_query(self, endpoint: str, config: tuple[DataSourceConfig, ...]) -> UUID:
        uuid = uuid1()
        config_dict = {data_source_config.name: data_source_config.value for data_source_config in config}
        self._queries[endpoint][uuid] = _Query(ticker=config_dict[_TICKER])
        return uuid

    def before_query(self, timestamp: str | None = None) -> None:
        pass

    def query(self, endpoint: str, uuid: UUID, timestamp: str | None = None) -> Decimal:
        pass
