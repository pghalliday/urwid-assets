from getpass import getpass
from json import dumps

from injector import inject

from urwid_assets.cli.export import OutputFile
from urwid_assets.encryption.encryption import Encryption
from urwid_assets.lib.redux.store import Store
from urwid_assets.lib.serialization.serialization import serialize
from urwid_assets.selectors.selectors import select_saved
from urwid_assets.state.state import State


class Export:
    @inject
    def __init__(self,
                 store: Store[State],
                 encryption: Encryption,
                 output_file: OutputFile):
        passphrase = getpass(u'Passphrase: ')
        encryption.init_passphrase(passphrase)
        output_file.write_text(dumps(serialize(select_saved(store.get_state()))))
