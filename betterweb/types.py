import typing as t

T = t.TypeVar('T')
P = t.ParamSpec('P')
R = t.TypeVar('R')

clsInstMethodType = t.Callable[t.Concatenate[t.Union[type[T], T], P], R]

class clsInstMethod(t.Generic[T, P, R]):
    @property
    def __func__(self) -> clsInstMethodType: ...
    @property
    def __isabstractmethod__(self) -> bool: ...
    def __init__(self, f: clsInstMethodType, /) -> None: ...
    @t.overload
    def __get__(self, instance: T, owner: type[T] | None = None, /) -> t.Callable[P, R]: ...
    @t.overload
    def __get__(self, instance: None, owner: type[_T], /) -> t.Callable[P, R]: ...
 
    __name__: str
    __qualname__: str
    @property
    def __wrapped__(self) -> t.Callable[t.Concatenate[type[T], P], R]: ...
