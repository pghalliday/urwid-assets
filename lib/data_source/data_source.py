from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class DataSourceConfig:
    name: str
    value: Any


@dataclass(frozen=True)
class DataSourceConfigField:
    name: str
    display_name: str


@dataclass(frozen=True)
class StringDataSourceConfigField(DataSourceConfigField):
    default: str
    secret: bool = False


@dataclass(frozen=True)
class DataSourceEndpoint:
    name: str
    display_name: str
    config_fields: tuple[DataSourceConfigField, ...]


class DataSource:
    def get_name(self) -> str:
        pass

    def get_display_name(self) -> str:
        pass

    def get_global_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        pass

    def set_global_config(self, config: tuple[DataSourceConfig, ...]) -> None:
        pass

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        pass

    def register_query(self, endpoint: str, config: tuple[DataSourceConfig, ...]) -> UUID:
        pass

    def before_query(self, timestamp: str | None = None) -> None:
        pass

    def query(self, endpoint: str, uuid: UUID, timestamp: str | None = None) -> Decimal:
        pass
