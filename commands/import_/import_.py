from getpass import getpass

from injector import inject

from commands.import_.import_types import InputFile
from encryption.encryption import Encryption
from lib.redux.reducer import Action
from lib.redux.store import Store
from lib.serialization.serialization import deserialize
from state.state import State, SET_STATE


class Import:
    @inject
    def __init__(self,
                 store: Store[State],
                 encryption: Encryption,
                 input_file: InputFile):
        passphrase = getpass(u'Passphrase: ')
        encryption.init_passphrase(passphrase)
        store.dispatch(Action(SET_STATE, deserialize(State, input_file.read_text())))
