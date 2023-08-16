from datetime import datetime

from urwid_assets.data_sources.crypto_compare.asset_crypto_compare_endpoint import AssetCryptoCompareEndpoint
from urwid_assets.data_sources.crypto_compare.config_names import BASE_URL, API_KEY
from urwid_assets.data_sources.crypto_compare.crypto_compare_aggregate import CryptoCompareAggregate
from urwid_assets.data_sources.crypto_compare.crypto_compare_endpoint import CryptoCompareEndpoint
from urwid_assets.data_sources.crypto_compare.crypto_compare_historical_aggregate import \
    CryptoCompareHistoricalAggregate
from urwid_assets.lib.data_sources.data_source import DataSource
from urwid_assets.lib.data_sources.data_source_aggregate import DataSourceAggregate
from urwid_assets.lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField, DataSourceEndpoint, \
    DataSourceConfig, get_string_from_config

CRYPTO_COMPARE = 'crypto-compare'


class CryptoCompare(DataSource):
    def __init__(self):
        self._endpoints: tuple[CryptoCompareEndpoint, ...] = (
            AssetCryptoCompareEndpoint(),
        )

    def get_name(self) -> str:
        return CRYPTO_COMPARE

    def get_display_name(self) -> str:
        return u'CryptoCompare'

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=BASE_URL,
                display_name=u'Base URL',
                default='https://min-api.cryptocompare.com/',
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
        return CryptoCompareAggregate(base_url, api_key, self._endpoints)

    def create_historical_aggregate(self,
                                    timestamp: datetime,
                                    config: tuple[DataSourceConfig, ...]) -> DataSourceAggregate:
        base_url = get_string_from_config(BASE_URL, config)
        api_key = get_string_from_config(API_KEY, config)
        return CryptoCompareHistoricalAggregate(timestamp, base_url, api_key, self._endpoints)
