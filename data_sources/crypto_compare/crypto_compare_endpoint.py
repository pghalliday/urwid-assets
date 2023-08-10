from data_sources.crypto_compare.crypto_compare_endpoint_aggregate import CryptoCompareEndpointAggregate
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
