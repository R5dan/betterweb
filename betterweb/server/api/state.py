from ..predefined.ws import WebsocketHandler
import typing as t

T = t.TypeVar("T")
I = t.TypeVar("I")

class State(t.Generic[T, I]):
    states: 'dict[str, State]' = {}

    def __init__(self, initial: I):
        self.data = initial
        self.new = initial
        self.ws = WebsocketHandler

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
    states: 'dict[str, Memo]' = {}
    def __init__(self, func: t.Callable[[], None | t.Callable[[], None]], deps: list[t.Any]):
        self.func = func
        self.deps = deps
        self.cleanup = None
        self.run()
    
    def run(self):
        if self.cleanup is not None:
            self.cleanup()
        
        self.cleanup = self.func()

    @classmethod
    def create(cls, func: t.Callable[[], None], deps: list[t.Any]):
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

def use_state[T, I](name, initial: I | t.Callable[[], I]=None) -> t.Tuple[T|I, t.Callable[[T], None]]:
    if callable(initial):
        i = initial()
    else:
        i = initial
    state: State[T, I] = State.create(name, i)

    return state.data, state.dispatch

def use_memo(func: t.Callable[[], None], deps: list[t.Any] = None):
    if deps is None:
        deps = []

    e = Memo.create(func, deps)

    if e.deps != deps:
        e.deps = deps
