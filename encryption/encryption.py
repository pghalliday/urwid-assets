import base64
import logging
import secrets

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from injector import singleton, inject

from base_types import SaltFile, DataFile
from lib.redux.reducer import Action
from lib.redux.store import Store
from lib.serialization.serialization import serialize, deserialize
from state.state import State, SET_STATE

_LOGGER = logging.getLogger(__name__)

_SALT_SIZE = 16
_SCRYPT_LENGTH = 32
_SCRYPT_N = 2 ** 14
_SCRYPT_R = 8
_SCRYPT_P = 1


class DecryptionFailure(Exception):
    def __init__(self, invalid_token: InvalidToken):
        super().__init__(u'Decryption failure')
        self.invalid_token = invalid_token


@singleton
class Encryption:

    @inject
    def __init__(self, store: Store[State], salt_file: SaltFile, data_file: DataFile):
        self._passphrase: str | None = None
        self._fernet: Fernet | None = None
        self._store = store
        self._data_file = data_file
        self._salt_file = salt_file
        _LOGGER.info('data: %s', self._data_file)
        _LOGGER.info('salt: %s', self._salt_file)
        self._load_salt()

    def init_passphrase(self, passphrase: str):
        self._set_passphrase(passphrase)
        self._decrypt()
        self._store.subscribe(self._update)

    def change_passphrase(self, passphrase: str):
        self._set_passphrase(passphrase)
        self._encrypt()

    def regenerate_salt(self):
        self._create_salt()
        self._create_fernet()
        self._encrypt()

    def _set_passphrase(self, passphrase: str):
        self._passphrase = passphrase
        self._create_fernet()

    def _load_salt(self) -> None:
        try:
            self._salt = self._salt_file.read_bytes()
        except FileNotFoundError:
            self._create_salt()

    def _create_salt(self) -> None:
        salt = secrets.token_bytes(_SALT_SIZE)
        self._salt_file.absolute().parent.mkdir(parents=True, exist_ok=True)
        self._salt_file.write_bytes(salt)
        self._salt = salt

    def _create_fernet(self):
        kdf = Scrypt(salt=self._salt, length=_SCRYPT_LENGTH, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
        derived_key = kdf.derive(self._passphrase.encode())
        self._fernet = Fernet(base64.urlsafe_b64encode(derived_key))

    def _encrypt(self):
        _LOGGER.info('encrypt')
        state = self._store.get_state()
        serialized = serialize(state)
        self._data_file.absolute().parent.mkdir(parents=True, exist_ok=True)
        self._data_file.write_bytes(self._fernet.encrypt(serialized.encode()))

    def _decrypt(self):
        _LOGGER.info('export')
        try:
            encrypted = self._data_file.read_bytes()
            try:
                serialized = self._fernet.decrypt(encrypted)
                state = deserialize(State, serialized.decode())
                self._store.dispatch(Action(SET_STATE, state))
            except InvalidToken as invalid_token:
                raise DecryptionFailure(invalid_token)

        except FileNotFoundError:
            _LOGGER.info('export: File not found')
            self._encrypt()

    def _update(self) -> None:
        self._encrypt()
