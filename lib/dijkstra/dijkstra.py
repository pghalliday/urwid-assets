from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')


class Edge(Generic[T]):
    a: str
    b: str
    cost: int
    ref: T


@dataclass(frozen=True)
class GraphEntry(Generic[T]):
    cost: int
    ref: T


class Graph(dict[str, dict[str, GraphEntry[T]]]):
    def __init__(self, edges: tuple[Edge[T], ...]):
        super().__init__()
        for edge in edges:
            try:
                # we may have duplicate edges with different costs
                # so only keep the lowest cost edge
                (cost, _) = self[edge.a][edge.b]
                if edge.cost < cost:
                    self._add_edge(edge)
            except KeyError:
                self._add_edge(edge)

    def _add_edge(self, edge):
        graph_data = GraphEntry(edge.cost, edge.ref)
        self[edge.a][edge.b] = graph_data
        self[edge.b][edge.a] = graph_data


@dataclass(frozen=True)
class QueueEntry:
    cost: int | float
    key: str


class Queue:
    def __init__(self) -> None:
        self._queue: list[QueueEntry] = []

    def add(self, entry: QueueEntry) -> None:
        self._queue.append(entry)
        self._queue.sort(key=lambda e: e.cost, reverse=True)

    def pop(self) -> QueueEntry:
        return self._queue.pop()

    def is_not_empty(self) -> bool:
        return len(self._queue) > 0

    def replace(self, entry: QueueEntry) -> None:
        self._queue = filter(lambda e: e.key != entry.key, self._queue)
        self.add(entry)


@dataclass(frozen=True)
class Step(Generic[T]):
    source: str
    target: str
    ref: T


class Dijkstra(Generic[T]):
    def __init__(self, source: str, graph: Graph[T]):
        self._source = source
        self._graph = graph
        self._prev: dict[str, str | None] = {}
        dist: dict[str, int | float] = {source: 0}
        queue: Queue = Queue()
        for key in graph.keys():
            if not key == source:
                dist[key] = math.inf
            self._prev[key] = None
            queue.add(QueueEntry(dist[key], key))
        while queue.is_not_empty():
            entry = queue.pop()
            edges = graph[entry.key]
            for key, graph_entry in edges.items():
                alt = dist[entry.key] + edges[key].cost
                if alt < dist[key]:
                    dist[key] = alt
                    self._prev[key] = entry.key
                    queue.replace(QueueEntry(alt, key))

    def resolve(self, target: str) -> tuple[Step[T], ...] | None:
        steps: tuple[Step, ...] = tuple()
        while True:
            if target == self._source:
                return steps
            last_target = target
            target = self._prev[target]
            if target is None:
                # there is no path to target
                return None
            steps = (Step(target, last_target, self._graph[target][last_target].ref),) + steps
