from typing import Callable, Generic, TypeVar

from lib.redux.reducer import Reducer, INIT_ACTION, Action

STATE = TypeVar('STATE')

Subscription = Callable[[], None]
Unsubscribe = Callable[[], None]


class Store(Generic[STATE]):
    def __init__(self, reducer: Reducer, initial_state: STATE | None = None):
        self._subscriptions: tuple[Subscription, ...] = tuple()
        self._state: STATE = None
        self._dispatching: bool = False
        self._reducer = reducer
        self._state = reducer(None, INIT_ACTION) if initial_state is None else initial_state

    def subscribe(self, subscription: Subscription) -> Unsubscribe:
        self._subscriptions += (subscription,)

        def unsubscribe() -> None:
            self._subscriptions = tuple(x for x in self._subscriptions if x is not subscription)

        return unsubscribe

    def dispatch(self, actions: Action | tuple[Action, ...]):
        assert not self._dispatching
        self._dispatching = True
        if isinstance(actions, Action):
            actions = (actions,)
        for action in actions:
            self._state = self._reducer(self._state, action)
        for subscription in self._subscriptions:
            subscription()
        self._dispatching = False

    def get_state(self):
        return self._state
