from getpass import getpass

from injector import inject

from commands.export.export_types import OutputFile
from encryption.encryption import Encryption
from lib.redux.store import Store
from lib.serialization.serialization import serialize
from state.state import State


class Export:
    @inject
    def __init__(self,
                 store: Store[State],
                 encryption: Encryption,
                 output_file: OutputFile):
        passphrase = getpass(u'Passphrase: ')
        encryption.init_passphrase(passphrase)
        output_file.write_text(serialize(store.get_state()))
