from datetime import datetime

from data_sources.tiingo.tiingo_endpoint_aggregate import TiingoEndpointAggregate
from data_sources.tiingo.tiingo_endpoint_historical_aggregate import TiingoEndpointHistoricalAggregate
from lib.data_sources.models import DataSourceConfigField


class TiingoEndpoint:
    def get_name(self) -> str:
        pass

    def get_display_name(self) -> str:
        pass

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        pass

    def create_aggregate(self, base_url: str, api_key: str) -> TiingoEndpointAggregate:
        pass

    def create_historical_aggregate(self,
                                    timestamp: datetime,
                                    base_url: str,
                                    api_key: str) -> TiingoEndpointHistoricalAggregate:
        pass
