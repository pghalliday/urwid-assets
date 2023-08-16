from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from urwid_assets.lib.serialization.serialization import serializable


class UnknownConfigField(Exception):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__('Unknown config field: %s' % name)
        self.name = name


@serializable()
@dataclass(frozen=True)
class DataSourceConfig:
    name: str


@serializable('string')
@dataclass(frozen=True)
class StringDataSourceConfig(DataSourceConfig):
    value: str


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


@dataclass(frozen=True)
class Query:
    uuid: UUID
    endpoint: str
    config: tuple[DataSourceConfig, ...]


@dataclass(frozen=True)
class QueryResult:
    price: Decimal | None = None
    error: str | None = None


def get_string_from_config(name: str, config: tuple[DataSourceConfig, ...]):
    for field in config:
        if field.name == name:
            assert isinstance(field, StringDataSourceConfig)
            return field.value
    raise UnknownConfigField(name)
