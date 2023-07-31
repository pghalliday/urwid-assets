from typing import Callable, Generic, TypeVar

from lib.redux.reducer import Reducer, INIT_ACTION, Action

STATE = TypeVar('STATE')

Subscription = Callable[[], None]
Unsubscribe = Callable[[], None]


class Store(Generic[STATE]):
    _subscriptions: tuple[Subscription, ...] = tuple()
    _state: STATE = None
    _reducer: Reducer

    def __init__(self, reducer: Reducer):
        self._reducer = reducer
        self._state = reducer(None, INIT_ACTION)

    def subscribe(self, subscription: Subscription) -> Unsubscribe:
        self._subscriptions += (subscription,)

        def unsubscribe() -> None:
            self._subscriptions = tuple(x for x in self._subscriptions if x is not subscription)

        return unsubscribe

    def dispatch(self, action: Action):
        self._state = self._reducer(self._state, action)
        for subscription in self._subscriptions:
            subscription()

    def get_state(self):
        return self._state
