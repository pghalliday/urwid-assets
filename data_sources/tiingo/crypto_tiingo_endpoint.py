import logging

from data_sources.tiingo.config_names import TICKER
from data_sources.tiingo.tiingo_endpoint import TiingoEndpoint
from data_sources.tiingo.tiingo_endpoint_aggregate import TiingoEndpointAggregate
from lib.data_sources.models import DataSourceConfigField, StringDataSourceConfigField

_LOGGER = logging.getLogger(__name__)

TIINGO_CRYPTO = 'crypto'


class CryptoTiingoEndpoint(TiingoEndpoint):
    def get_name(self) -> str:
        return TIINGO_CRYPTO

    def get_display_name(self) -> str:
        return u'Crypto'

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=TICKER,
                display_name=u'Ticker',
                default='',
            ),
        )

    def create_aggregate(self, base_url: str, api_key: str) -> TiingoEndpointAggregate:
        return TiingoEndpointAggregate(base_url,
                                       api_key,
                                       'tiingo/crypto/top',
                                       lambda entry: entry['topOfBookData'][0]['bidPrice'])
