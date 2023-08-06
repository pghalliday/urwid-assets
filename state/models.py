from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class AssetDataSourceConfig:
    name: str


@dataclass(frozen=True)
class StringAssetDataSourceConfig(AssetDataSourceConfig):
    value: str


@dataclass(frozen=True)
class AssetDataSource:
    name: str
    endpoint: str
    config: tuple[AssetDataSourceConfig, ...]


@dataclass(frozen=True)
class Asset:
    uuid: UUID
    name: str
    amount: Decimal
    data_source: AssetDataSource
    price: Decimal


@dataclass(frozen=True)
class AssetSnapshot:
    uuid: UUID
    name: str
    amount: Decimal
    price: Decimal


@dataclass(frozen=True)
class Snapshot:
    uuid: UUID
    assets: tuple[AssetSnapshot, ...]
    timestamp: int


@dataclass(frozen=True)
class Assets:
    current: tuple[Asset, ...]
    snapshots: tuple[Snapshot, ...]


@dataclass(frozen=True)
class AssetsFile:
    path: str | None
    passphrase: str | None


@dataclass(frozen=True)
class DataSourceConfigField:
    name: str


@dataclass(frozen=True)
class StringDataSourceConfigField(DataSourceConfigField):
    value: str


@dataclass(frozen=True)
class DataSource:
    name: str
    config: tuple[DataSourceConfigField]


@dataclass(frozen=True)
class State:
    assets_file: AssetsFile
    data_sources: tuple[DataSource, ...]
    assets: Assets
