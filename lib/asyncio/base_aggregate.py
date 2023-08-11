from __future__ import annotations

from asyncio import Event
from typing import Callable, Awaitable

from lib.asyncio.aggregate import SELECT, RESULT, AGGREGATE, Aggregate

SelectCallback = Callable[[SELECT, AGGREGATE], RESULT]
AggregateCallback = Callable[[], Awaitable[AGGREGATE]]


class BaseAggregate(Aggregate[SELECT, RESULT, AGGREGATE]):
    def __init__(self,
                 select_callback: SelectCallback,
                 aggregate_callback: AggregateCallback) -> None:
        self._aggregate: AGGREGATE | None = None
        self._select_callback = select_callback
        self._aggregate_callback = aggregate_callback
        self._event = Event()

    async def select(self, select_param: SELECT) -> RESULT:
        await self._event.wait()
        return self._select_callback(select_param, self._aggregate)

    async def run(self) -> AGGREGATE:
        self._aggregate = await self._aggregate_callback()
        self._event.set()
        return self._aggregate
