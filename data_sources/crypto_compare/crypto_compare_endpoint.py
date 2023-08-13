from datetime import datetime

from data_sources.crypto_compare.crypto_compare_endpoint_aggregate import CryptoCompareEndpointAggregate
from data_sources.crypto_compare.crypto_compare_endpoint_historical_aggregate import \
    CryptoCompareEndpointHistoricalAggregate
from lib.data_sources.models import DataSourceConfigField


class CryptoCompareEndpoint:
    def get_name(self) -> str:
        pass

    def get_display_name(self) -> str:
        pass

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        pass

    def create_aggregate(self, base_url: str, api_key: str) -> CryptoCompareEndpointAggregate:
        pass

    def create_historical_aggregate(self,
                                    timestamp: datetime,
                                    base_url: str,
                                    api_key: str) -> CryptoCompareEndpointHistoricalAggregate:
        pass
