from typing import Generic, TypeVar

SELECT = TypeVar('SELECT')
RESULT = TypeVar('RESULT')
AGGREGATE = TypeVar('AGGREGATE')


class Aggregate(Generic[SELECT, RESULT, AGGREGATE]):
    async def select(self, select_param: SELECT) -> RESULT:
        pass

    async def run(self) -> AGGREGATE:
        pass
