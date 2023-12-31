from getpass import getpass
from json import loads

from injector import inject

from urwid_assets.cli.import_ import InputFile
from urwid_assets.encryption.encryption import Encryption
from urwid_assets.lib.redux.reducer import Action
from urwid_assets.lib.redux.store import Store
from urwid_assets.lib.serialization.serialization import deserialize
from urwid_assets.state.saved.saved import Saved, SET_SAVED
from urwid_assets.state.state import State


class Import:
    @inject
    def __init__(self,
                 store: Store[State],
                 encryption: Encryption,
                 input_file: InputFile):
        passphrase = getpass(u'Passphrase: ')
        encryption.init_passphrase(passphrase)
        store.dispatch(Action(SET_SAVED, deserialize(Saved, loads(input_file.read_text()))))
