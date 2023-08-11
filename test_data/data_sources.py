from uuid import uuid1

from data_sources.crypto_compare.crypto_compare import CRYPTO_COMPARE
from data_sources.tiingo.config_names import BASE_URL, API_KEY
from data_sources.tiingo.tiingo import TIINGO
from lib.data_sources.models import StringDataSourceConfig
from state.data_sources.data_sources import DataSourceInstance
from test_secrets import CRYPTO_COMPARE_API_KEY, TIINGO_API_KEY

_CRYPTO_COMPARE_DATA_SOURCE_UUID = uuid1()
_TIINGO_DATA_SOURCE_UUID = uuid1()
DATA_SOURCES = (
    DataSourceInstance(
        uuid=_CRYPTO_COMPARE_DATA_SOURCE_UUID,
        name=u'My CryptoCompare',
        type=CRYPTO_COMPARE,
        config=(
            StringDataSourceConfig(
                name=BASE_URL,
                value='https://min-api.cryptocompare.com/',
            ),
            StringDataSourceConfig(
                name=API_KEY,
                value=CRYPTO_COMPARE_API_KEY,
            ),
        ),
    ),
    DataSourceInstance(
        uuid=_TIINGO_DATA_SOURCE_UUID,
        name=u'My Tiingo',
        type=TIINGO,
        config=(
            StringDataSourceConfig(
                name=BASE_URL,
                value='https://api.tiingo.com/',
            ),
            StringDataSourceConfig(
                name=API_KEY,
                value=TIINGO_API_KEY,
            ),
        ),
    ),
)
