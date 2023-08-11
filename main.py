from app import App
from base_module import BaseModule
from commands.export.export_module import ExportModule
from commands.import_.import_module import ImportModule
from commands.ui.ui_module import UIModule
from data_sources.crypto_compare.crypto_compare import CryptoCompare
from data_sources.tiingo.tiingo import Tiingo

if __name__ == '__main__':
    App(
        BaseModule(
            CryptoCompare(),
            Tiingo(),
        ),
        UIModule(),
        ExportModule(),
        ImportModule(),
    )
