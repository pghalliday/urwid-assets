from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Asset:
    id: UUID
    name: str
    amount: Decimal
    price_source: str


@dataclass(frozen=True)
class AssetSnapshot:
    id: UUID
    name: str
    amount: Decimal
    price: Decimal


@dataclass(frozen=True)
class Snapshot:
    id: UUID
    assets: tuple[AssetSnapshot]
    timestamp: int


@dataclass(frozen=True)
class Assets:
    current: tuple[Asset]
    snapshots: tuple[Snapshot]
