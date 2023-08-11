from datetime import datetime

from data_sources.tiingo.config_names import API_KEY, BASE_URL
from data_sources.tiingo.crypto_tiingo_endpoint import CryptoTiingoEndpoint
from data_sources.tiingo.forex_tiingo_endpoint import ForexTiingoEndpoint
from data_sources.tiingo.iex_tiingo_endpoint import IEXTiingoEndpoint
from data_sources.tiingo.tiingo_aggregate import TiingoAggregate
from data_sources.tiingo.tiingo_endpoint import TiingoEndpoint
from data_sources.tiingo.tiingo_historical_aggregate import TiingoHistoricalAggregate
from lib.data_sources.data_source import DataSource
from lib.data_sources.data_source_aggregate import DataSourceAggregate
from lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField, DataSourceEndpoint, \
    DataSourceConfig, get_string_from_config

TIINGO = 'tiingo'


class Tiingo(DataSource):
    def __init__(self):
        self._endpoints: tuple[TiingoEndpoint, ...] = (
            IEXTiingoEndpoint(),
            ForexTiingoEndpoint(),
            CryptoTiingoEndpoint(),
        )

    def get_name(self) -> str:
        return TIINGO

    def get_display_name(self) -> str:
        return u'Tiingo'

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=BASE_URL,
                display_name=u'Base URL',
                default='https://api.tiingo.com/',
            ),
            StringDataSourceConfigField(
                name=API_KEY,
                display_name=u'API Key',
                default='',
                secret=True,
            ),
        )

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        return tuple(DataSourceEndpoint(
            name=endpoint.get_name(),
            display_name=endpoint.get_display_name(),
            config_fields=endpoint.get_config_fields(),
        ) for endpoint in self._endpoints)

    def create_aggregate(self,
                         config: tuple[DataSourceConfig, ...]) -> DataSourceAggregate:
        base_url = get_string_from_config(BASE_URL, config)
        api_key = get_string_from_config(API_KEY, config)
        return TiingoAggregate(base_url, api_key, self._endpoints)

    def create_historical_aggregate(self,
                                    timestamp: datetime,
                                    config: tuple[DataSourceConfig, ...]) -> DataSourceAggregate:
        base_url = get_string_from_config(BASE_URL, config)
        api_key = get_string_from_config(API_KEY, config)
        return TiingoHistoricalAggregate(timestamp, base_url, api_key, self._endpoints)
