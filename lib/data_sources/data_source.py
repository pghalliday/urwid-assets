from __future__ import annotations

from lib.data_sources.data_source_aggregate import DataSourceAggregate
from lib.data_sources.models import DataSourceConfigField, DataSourceEndpoint, DataSourceConfig


class DataSource:
    def get_name(self) -> str:
        pass

    def get_display_name(self) -> str:
        pass

    def get_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        pass

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        pass

    def create_aggregate(self, config: tuple[DataSourceConfig, ...]) -> DataSourceAggregate:
        pass
