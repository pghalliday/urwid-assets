from dataclasses import dataclass

from injector import singleton, inject

from models.models import Asset, Assets


@singleton
@inject
@dataclass
class DataController:
    assets: Assets

    def get_current(self) -> list[Asset]:
        return self.assets.current
