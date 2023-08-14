from urwid_assets.lib.asyncio.aggregate import Aggregate
from urwid_assets.lib.data_sources.models import Query, QueryResult


class DataSourceAggregate(Aggregate[Query, QueryResult, None]):
    pass
