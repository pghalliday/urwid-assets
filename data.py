from dataclasses import dataclass
from uuid import UUID


@dataclass
class Asset:
    id: UUID
    name: str
    amount: int
    price_source: str


@dataclass
class AssetSnapshot:
    id: UUID
    name: str
    amount: int
    price: int


@dataclass
class Snapshot:
    id: UUID
    assets: list[AssetSnapshot]
    timestamp: int


@dataclass
class Assets:
    current: list[Asset]
    snapshots: list[Snapshot]
