from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from lib.redux.store import Store
from state import State
from state.assets import Asset


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
    _store: Store[State]

    def __init__(self, store: Store[State]):
        self._store = store
        self._store.subscribe(self._update)

    def get_name(self) -> str:
        pass

    def get_display_name(self) -> str:
        pass

    def get_global_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        pass

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        pass

    def before_query(self, timestamp: str | None = None) -> None:
        pass

    def query(self, asset: Asset, timestamp: str | None = None) -> Decimal:
        pass

    def _update(self) -> None:
        pass
