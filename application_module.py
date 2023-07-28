from injector import Module, singleton, provider

from models.models import Assets
from test_data import ASSETS


class ApplicationModule(Module):
    @singleton
    @provider
    def provide_assets(self) -> Assets:
        return ASSETS
