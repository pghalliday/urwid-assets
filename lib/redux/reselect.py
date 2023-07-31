from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable


@dataclass(frozen=True)
class SelectorCacheOptions:
    max_age: int = 0


@dataclass(frozen=True)
class SelectorOptions:
    cache: SelectorCacheOptions = SelectorCacheOptions()
    dimensions: tuple[int, ...] = tuple()


def _matches(args1: tuple[Any, ...], args2: tuple[Any, ...]) -> bool:
    if len(args1) == len(args2):
        zipped = zip(args1, args2)
        if reduce(lambda acc, args: args[0] is args[1], zipped, True):
            return True
    return False


# _CacheHit is used to wrap results so that we
# can distinguish between a None result and
# a cache miss
@dataclass(frozen=True)
class _CacheHit:
    result: Any


class _Level2Cache:
    _results: dict[tuple[Any, ...], Any] = {}

    def push(self, args: tuple[Any, ...], result: Any) -> None:
        self._results[args] = result

    def get(self, args: tuple[Any, ...]) -> _CacheHit | None:
        try:
            return _CacheHit(self._results[args])
        except KeyError:
            return None

    def pop(self, args: tuple[Any, ...]) -> _CacheHit | None:
        try:
            return _CacheHit(self._results.pop(args))
        except KeyError:
            return None


class _Level2CacheHistory:
    _options: SelectorCacheOptions
    _next_cache: _Level2Cache | None = None
    _caches: tuple[_Level2Cache, ...] = tuple()

    def __init__(self, options: SelectorCacheOptions):
        self._options = options

    def start_next(self):
        self._next_cache = _Level2Cache()

    def commit(self):
        self._caches = (self._next_cache,) + self._caches[:self._options.max_age]
        self._next_cache = None

    def find(self, args: tuple[Any, ...]) -> _CacheHit | None:
        cache_hit = self._next_cache.get(args)
        if cache_hit is not None:
            return cache_hit
        for cache in self._caches:
            cache_hit = cache.pop(args)
            if cache_hit is not None:
                self._next_cache.push(args, cache_hit.result)
                return cache_hit
        return None

    def add(self, args: tuple[Any, ...], result: Any) -> None:
        self._next_cache.push(args, result)


class _Level1Cache:
    _options: SelectorCacheOptions
    _results: dict[tuple[Any, ...], Any] = {}

    def __init__(self, options: SelectorCacheOptions):
        self._options = options

    def find(self, args: tuple[Any, ...]) -> _CacheHit | None:
        try:
            return _CacheHit(self._results[args])
        except KeyError:
            return None

    def add(self, args: tuple[Any, ...], result: Any) -> None:
        self._results = {
            **{args: result},
            **dict(itertools.islice(self._results.items(), None, self._options.max_age))
        }


@dataclass(frozen=True)
class _ArgumentsTree:
    sub_trees: tuple[_ArgumentsTree, ...] = None
    args: tuple[Any, ...] = None


def create_selector(selectors: tuple[Callable, ...], next_selector: Callable, options=SelectorOptions()) -> Callable:
    level_1_cache = _Level1Cache(options.cache)
    level_2_cache_history = _Level2CacheHistory(options.cache)

    def prepend_args(left_args: tuple[Any, ...], right_args: _ArgumentsTree) -> _ArgumentsTree:
        if right_args.sub_trees is None:
            # right_args is an end leaf, we can just append the args
            return _ArgumentsTree(
                args=left_args + right_args.args
            )
        # recurse for the right_args sub_trees
        return _ArgumentsTree(
            sub_trees=tuple(prepend_args(left_args, sub_tree) for sub_tree in right_args.sub_trees)
        )

    def multiply_args(left_args: _ArgumentsTree, right_args: _ArgumentsTree) -> _ArgumentsTree:
        if left_args.sub_trees is None:
            # left_args is an end leaf so merge it with the right_args
            return prepend_args(left_args.args, right_args)
        # recurse for the left_args sub_trees
        return _ArgumentsTree(
            sub_trees=tuple(multiply_args(sub_tree, right_args) for sub_tree in left_args.sub_trees)
        )

    def expand_dimensions(dimensions: int, arg: Any) -> _ArgumentsTree:
        if dimensions == 0:
            # no dimensions just a single argument
            return _ArgumentsTree(args=(arg,))
        # recurse to expand the next dimension
        assert isinstance(arg, tuple)
        return _ArgumentsTree(
            sub_trees=tuple(expand_dimensions(dimensions - 1, sub_arg) for sub_arg in arg)
        )

    def expand_args(
            dimensioned_args: tuple[tuple[int, Any], ...]
    ) -> _ArgumentsTree:
        head = dimensioned_args[0]
        tail = dimensioned_args[1:]
        (dimensions, arg) = head
        if len(tail) > 0:
            expanded_head = expand_dimensions(dimensions, arg)
            expanded_tail = expand_args(tail)
            return multiply_args(expanded_head, expanded_tail)
        return expand_dimensions(dimensions, arg)

    def expand_results(arguments_tree: _ArgumentsTree) -> Any:
        nonlocal level_2_cache_history
        if arguments_tree.sub_trees is None:
            # this is a simple, single function call :)
            args = arguments_tree.args
            cache_hit = level_2_cache_history.find(args)
            if cache_hit is None:
                result = next_selector(*args)
                level_2_cache_history.add(args, result)
                return result
            return cache_hit.result
        # need to recurse and construct a (possibly multidimensional) tuple
        return tuple(expand_results(sub_tree) for sub_tree in arguments_tree.sub_trees)

    def memoized_selector(*args: tuple[Any]) -> Any:
        nonlocal level_2_cache_history
        resolved_args = tuple(selector(*args) for selector in selectors)
        cache_hit = level_1_cache.find(resolved_args)
        if cache_hit is None:
            level_2_cache_history.start_next()
            resolved_args_length = len(resolved_args)
            options_dimensions = options.dimensions
            options_dimensions_length = len(options_dimensions)
            dimensions = tuple(options_dimensions[index] if index < options_dimensions_length else 0
                               for index in range(resolved_args_length))
            dimensioned_args = tuple(zip(dimensions, resolved_args))
            expanded_args = expand_args(dimensioned_args)
            result = expand_results(expanded_args)
            level_2_cache_history.commit()
            level_1_cache.add(resolved_args, result)
            return result
        return cache_hit.result

    return memoized_selector
