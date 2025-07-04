import typing as t

T = t.TypeVar("T")
I = t.TypeVar("I")


class State(t.Generic[T, I]):
    states: "dict[str, State]" = {}

    def __init__(self, initial: I):
        self.data = initial
        self.new = initial
        # Use lazy import to avoid circular dependency
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            from ..predefined.ws import WebsocketHandler

            self._ws = WebsocketHandler
        return self._ws

    @classmethod
    def create(cls, name: str, initial: I):
        if name in cls.states:
            return cls.states[name].rerender()
        else:
            state = State(initial)
            cls.states[name] = state
            return state

    def rerender(self):
        self.data = self.new
        return self

    @property
    def value(self) -> T | I:
        return self.data

    def dispatch(self, data: T):
        self.new = data
        self.ws.schedule_render()


class Memo:
    states: "dict[str, Memo]" = {}

    def __init__(
        self, func: t.Callable[[], None | t.Callable[[], None]], deps: list[t.Any]
    ):
        self.func = func
        self.deps = deps
        self.cleanup = None
        self.run()

    def run(self):
        if self.cleanup is not None:
            self.cleanup()

        self.cleanup = self.func()

    @classmethod
    def create(
        cls, func: t.Callable[[], None | t.Callable[[], None]], deps: list[t.Any]
    ):
        if func.__name__ in cls.states:
            effect = cls.states[func.__name__]
            if effect.deps != deps:
                effect.deps = deps
                effect.run()

            return effect
        else:
            effect = cls(func, deps)
            cls.states[func.__name__] = effect
            return effect


def use_state[
    T
](name, initial: T | t.Callable[[], T] = None) -> tuple[T | T, t.Callable[[T], None]]:
    """
    Creates a stateful value.

    - `name`: The name of the state. Has no  effect on the state, but is used to identify it.
    - `initial`: The initial value of the state.

    Returns:

    - tuple[T | I, Callable[[T], None]]
        - The stateful value
        - A function to dispatch a new value to the state, causing a rerender
    """
    if callable(initial):
        i = initial()
    else:
        i = initial
    state: State[T, T] = State.create(name, i)

    return state.data, state.dispatch


def use_memo(
    func: t.Callable[[], None | t.Callable[[], None]],
    deps: t.Optional[list[t.Any]] = None,
):
    """
    Creates a memoized value.
    Is run when the dependencies change.

    - `func`: The function to memoize. The name must be unique.
    - `deps`: The dependencies of the memoized value. Optional: defaults to an empty list.

    Returns:

    - None
    - Cleanup function - Called immediately before the next render
    """

    if deps is None:
        deps = []

    e = Memo.create(func, deps)

    if e.deps != deps:
        e.deps = deps
