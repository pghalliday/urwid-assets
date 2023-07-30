from dataclasses import dataclass
from decimal import Decimal

from injector import singleton, inject

from models.models import Asset, Assets


@singleton
@inject
@dataclass
class DataController:
    assets: Assets

    def get_current(self) -> list[Asset]:
        return self.assets.current

    def update_current_asset(self,
                             asset: Asset,
                             name: str,
                             amount: Decimal,
                             price_source: str):
        pass
