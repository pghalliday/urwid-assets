from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid1

from lib.data_source.data_source import DataSource, DataSourceConfigField, \
    DataSourceEndpoint, StringDataSourceConfigField, DataSourceConfig

_API_KEY = 'api_key'
_BASE_URL = 'base_url'
_ENVIRONMENT = 'environment'
_SYMBOL = 'symbol'
_TEST_1 = 'test1'
_TEST_2 = 'test2'
_TEST_3 = 'test3'

_ENDPOINT_1 = 'endpoint1'
_ENDPOINT_2 = 'endpoint2'
_ENDPOINT_3 = 'endpoint3'


@dataclass(frozen=True)
class _Query1:
    symbol: str
    test1: str


@dataclass(frozen=True)
class _Query2:
    symbol: str
    test1: str
    test2: str


@dataclass(frozen=True)
class _Query3:
    symbol: str
    test1: str
    test2: str
    test3: str


class Test(DataSource):
    _base_url: str
    _api_key: str
    _environment: str
    _endpoint_1_queries: dict[UUID, _Query1]
    _endpoint_2_queries: dict[UUID, _Query2]
    _endpoint_3_queries: dict[UUID, _Query3]

    def get_name(self) -> str:
        return 'test'

    def get_display_name(self) -> str:
        return u'Test'

    def get_global_config_fields(self) -> tuple[DataSourceConfigField, ...]:
        return (
            StringDataSourceConfigField(
                name=_BASE_URL,
                display_name=u'Base URL',
                default='https://api.test.com/',
            ),
            StringDataSourceConfigField(
                name=_API_KEY,
                display_name=u'API Key',
                default='',
            ),
            StringDataSourceConfigField(
                name=_ENVIRONMENT,
                display_name=u'Environment',
                default='live',
            ),
        )

    def set_global_config(self, config: tuple[DataSourceConfig, ...]) -> None:
        config_dict = {data_source_config.name: data_source_config.value for data_source_config in config}
        self._base_url = config_dict[_BASE_URL]
        self._api_key = config_dict[_API_KEY]
        self._environment = config_dict[_ENVIRONMENT]

    def get_endpoints(self) -> tuple[DataSourceEndpoint, ...]:
        return (
            DataSourceEndpoint(
                name=_ENDPOINT_1,
                display_name=u'Endpoint 1',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_SYMBOL,
                        display_name=u'Symbol',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_1,
                        display_name=u'Test 1',
                        default='',
                    ),
                )
            ),
            DataSourceEndpoint(
                name=_ENDPOINT_2,
                display_name=u'Endpoint 2',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_SYMBOL,
                        display_name=u'Symbol',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_1,
                        display_name=u'Test 1',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_2,
                        display_name=u'Test 2',
                        default='',
                    ),
                )
            ),
            DataSourceEndpoint(
                name=_ENDPOINT_3,
                display_name=u'Endpoint 3',
                config_fields=(
                    StringDataSourceConfigField(
                        name=_SYMBOL,
                        display_name=u'Symbol',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_1,
                        display_name=u'Test 1',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_2,
                        display_name=u'Test 2',
                        default='',
                    ),
                    StringDataSourceConfigField(
                        name=_TEST_3,
                        display_name=u'Test 3',
                        default='',
                    ),
                )
            ),
        )

    def register_query(self, endpoint: str, config: tuple[DataSourceConfig, ...]) -> UUID:
        uuid = uuid1()
        config_dict = {data_source_config.name: data_source_config.value for data_source_config in config}
        if endpoint == _ENDPOINT_1:
            self._endpoint_1_queries[uuid] = _Query1(
                symbol=config_dict[_SYMBOL],
                test1=config_dict[_TEST_1],
            )
        elif endpoint == _ENDPOINT_2:
            self._endpoint_2_queries[uuid] = _Query2(
                symbol=config_dict[_SYMBOL],
                test1=config_dict[_TEST_1],
                test2=config_dict[_TEST_2],
            )
        elif endpoint == _ENDPOINT_3:
            self._endpoint_3_queries[uuid] = _Query3(
                symbol=config_dict[_SYMBOL],
                test1=config_dict[_TEST_1],
                test2=config_dict[_TEST_2],
                test3=config_dict[_TEST_3],
            )
        return uuid

    def before_query(self, timestamp: str | None = None) -> None:
        pass

    def query(self, endpoint: str, uuid: UUID, timestamp: str | None = None) -> Decimal:
        pass
