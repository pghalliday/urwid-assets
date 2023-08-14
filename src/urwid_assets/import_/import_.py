from getpass import getpass

from injector import inject

from urwid_assets.cli.import_ import InputFile
from urwid_assets.encryption.encryption import Encryption
from urwid_assets.lib.redux.reducer import Action
from urwid_assets.lib.redux.store import Store
from urwid_assets.lib.serialization.serialization import deserialize
from urwid_assets.state.state import State, SET_STATE


class Import:
    @inject
    def __init__(self,
                 store: Store[State],
                 encryption: Encryption,
                 input_file: InputFile):
        passphrase = getpass(u'Passphrase: ')
        encryption.init_passphrase(passphrase)
        store.dispatch(Action(SET_STATE, deserialize(State, input_file.read_text())))
