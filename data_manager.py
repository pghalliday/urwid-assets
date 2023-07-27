from dataclasses import dataclass

from data import Asset, Assets


@dataclass
class DataManager:
    assets: Assets

    def get_current(self) -> list[Asset]:
        return self.assets.current
