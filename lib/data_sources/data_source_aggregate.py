from lib.asyncio.aggregate import Aggregate
from lib.data_sources.models import Query, QueryResult


class DataSourceAggregate(Aggregate[Query, QueryResult, None]):
    pass
