from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeVar, Any, Callable

STATE = TypeVar('STATE')


@dataclass(frozen=True)
class Action:
    type: str
    payload: Any


Reducer = Callable[[STATE, Action], STATE]

INIT = '__INIT__'
INIT_ACTION = Action(
    INIT,
    None
)


def combine_reducers(
        state_class: Callable[[Any, ...], STATE],
        reducer_map: MappingProxyType[str, Reducer]
) -> Reducer:
    def combined_reducer(state: STATE, action: Action) -> STATE:
        kwargs = {arg: reducer(None if state is None else getattr(state, arg), action)
                  for arg, reducer in reducer_map.items()}
        return state_class(**kwargs)

    return combined_reducer
