import logging

from data_sources.crypto_compare.config_names import FSYM, TSYM
from data_sources.crypto_compare.crypto_compare_endpoint import CryptoCompareEndpoint
from data_sources.crypto_compare.crypto_compare_endpoint_aggregate import CryptoCompareEndpointAggregate
from lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField

_LOGGER = logging.getLogger(__name__)

CRYPTO_COMPARE_ASSET = 'asset'


class AssetCryptoCompareEndpoint(CryptoCompareEndpoint):
    def get_name(self) -> str:
        return CRYPTO_COMPARE_ASSET

    def get_display_name(self) -> str:
        return u'Asset'

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=FSYM,
                display_name=u'fsym',
                default='',
            ),
            StringDataSourceConfigField(
                name=TSYM,
                display_name=u'tsym',
                default='',
            ),
        )

    def create_aggregate(self, base_url: str, api_key: str) -> CryptoCompareEndpointAggregate:
        return CryptoCompareEndpointAggregate(base_url,
                                              api_key,
                                              'data/pricemulti')
