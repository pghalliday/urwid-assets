import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from lib.redux.reducer import INIT
from lib.redux.store import Action
from lib.serialization.serialization import serializable

LOGGER = logging.getLogger(__name__)


@serializable()
@dataclass(frozen=True)
class AssetSnapshot:
    uuid: UUID
    name: str
    amount: Decimal
    price: Decimal


@serializable()
@dataclass(frozen=True)
class Snapshot:
    uuid: UUID
    assets: tuple[AssetSnapshot, ...]
    timestamp: int


def reducer(state: tuple[Snapshot, ...], action: Action) -> tuple[Snapshot, ...]:
    if action.type == INIT:
        return tuple()
    return state
