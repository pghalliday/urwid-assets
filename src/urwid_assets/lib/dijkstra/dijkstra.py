from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypeVar, Generic, Iterable

T = TypeVar('T')
K = TypeVar('K')


@dataclass(frozen=True)
class Edge(Generic[K, T]):
    source: K
    target: K
    cost: int
    ref: T


@dataclass(frozen=True)
class _GraphEntry(Generic[T]):
    cost: int
    ref: T
    reversed: bool


class _Graph(dict[K, dict[K, _GraphEntry[T]]]):
    def __init__(self, edges: Iterable[Edge[K, T], ...]):
        super().__init__()
        for edge in edges:
            try:
                # we may have duplicate edges with different costs
                # so only keep the lowest cost edge
                existing = self[edge.source][edge.target]
                if edge.cost < existing.cost:
                    self._add_entries(edge)
            except KeyError:
                self._add_entries(edge)

    def _add_entries(self, edge: Edge[K, T]):
        self._add_entry(edge.source, edge.target, _GraphEntry[T](edge.cost, edge.ref, False))
        self._add_entry(edge.target, edge.source, _GraphEntry[T](edge.cost, edge.ref, True))

    def _add_entry(self, source: K, target: K, entry: _GraphEntry[T]):
        try:
            sub_map = self[source]
        except KeyError:
            sub_map: dict[K, _GraphEntry[T]] = {}
            self[source] = sub_map
        sub_map[target] = entry


@dataclass(frozen=True)
class _QueueEntry(Generic[K]):
    cost: int | float
    key: K


class _Queue(Generic[K]):
    def __init__(self) -> None:
        self._queue: list[_QueueEntry[K]] = []

    def add(self, entry: _QueueEntry[K]) -> None:
        self._queue.append(entry)
        self._queue.sort(key=lambda e: e.cost, reverse=True)

    def pop(self) -> _QueueEntry[K]:
        return self._queue.pop()

    def is_not_empty(self) -> bool:
        return len(self._queue) > 0

    def replace(self, entry: _QueueEntry[K]) -> None:
        self._queue = list(filter(lambda e: e.key != entry.key, self._queue))
        self.add(entry)


@dataclass(frozen=True)
class Step(Generic[K, T]):
    source: K
    target: K
    ref: T
    reversed: bool


Resolved = tuple[tuple[K, tuple[Step[K, T], ...]], ...]


def dijkstra(source: K, edges: Iterable[Edge[K, T]]) -> Resolved:
    graph = _Graph(edges)
    prev: dict[K, K | None] = {}
    dist: dict[K, int | float] = {source: 0}
    queue = _Queue()
    for key in graph.keys():
        if not key == source:
            dist[key] = math.inf
            prev[key] = None
        queue.add(_QueueEntry[K](dist[key], key))
    while queue.is_not_empty():
        entry = queue.pop()
        edges = graph[entry.key]
        for key, graph_entry in edges.items():
            alt = dist[entry.key] + edges[key].cost
            if alt < dist[key]:
                dist[key] = alt
                prev[key] = entry.key
                queue.replace(_QueueEntry[K](alt, key))

    # now collapse the prev dictionary to lists of steps from source
    def resolve(target: K) -> tuple[Step[K, T], ...] | None:
        steps: tuple[Step[K, T], ...] = tuple()
        while True:
            if target == source:
                return steps
            last_target = target
            target = prev[target]
            if target is None:
                # there is no path to target
                return None
            steps = (Step[K, T](target,
                                last_target,
                                graph[target][last_target].ref,
                                graph[target][last_target].reversed),) + steps

    return ((source, tuple()),) + tuple(filter(
        lambda item: item[1] is not None,
        [(target, resolve(target)) for target in prev.keys()]
    ))


class UnreachableTarget(Exception):
    def __init__(self, target: K):
        super().__init__(u'Unreachable target: %s' % target)
        self.target = target


def get_steps(target: K, resolved: Resolved) -> tuple[Step[K, T], ...]:
    for item in resolved:
        if item[0] == target:
            return item[1]
    raise UnreachableTarget(target)
