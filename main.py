from application import Application
from data_manager import DataManager
from test_data import ASSETS
from ui_manager import UIManager

data_manager = DataManager(ASSETS)
ui_manager = UIManager()
application = Application(data_manager, ui_manager)

if __name__ == '__main__':
    application.start()
