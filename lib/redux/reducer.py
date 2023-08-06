from dataclasses import dataclass
from typing import TypeVar, Any, Callable

STATE = TypeVar('STATE')


@dataclass(frozen=True)
class Action:
    type: str
    payload: Any


Reducer = Callable[[STATE, Action], STATE]


@dataclass(frozen=True)
class ReducerMapping:
    field: str
    reducer: Reducer


INIT = '__INIT__'
INIT_ACTION = Action(
    INIT,
    None
)


def combine_reducers(
        state_class: Callable[[Any, ...], STATE],
        reducer_map: tuple[ReducerMapping, ...]
) -> Reducer:
    def combined_reducer(state: STATE, action: Action) -> STATE:
        kwargs = {reducer_mapping.field: reducer_mapping.reducer(
            None if state is None else getattr(state, reducer_mapping.field), action
        ) for reducer_mapping in reducer_map}
        return state_class(**kwargs)

    return combined_reducer
