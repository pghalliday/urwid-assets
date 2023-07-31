from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Asset:
    uuid: UUID
    name: str
    amount: Decimal
    price_source: str


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
    path: str
    passphrase: str


@dataclass(frozen=True)
class State:
    assets_file: AssetsFile
    assets: Assets
