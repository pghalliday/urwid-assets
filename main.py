from injector import Injector

from application import Application
from application_module import ApplicationModule

if __name__ == '__main__':
    injector = Injector(ApplicationModule())
    application = injector.get(Application)
    application.start()
