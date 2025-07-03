from uvicorn._types import (
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    HTTPResponseTrailersEvent,
    HTTPServerPushEvent,
    HTTPDisconnectEvent,
    WebSocketAcceptEvent,
    WebSocketSendEvent,
    WebSocketResponseStartEvent,
    WebSocketResponseBodyEvent,
    WebSocketCloseEvent,
    WebSocketConnectEvent,
    WebSocketReceiveEvent,
    WebSocketDisconnectEvent,
    HTTPScope,
    WebSocketScope,
    LifespanScope,
)
import typing as t
from .request import Request
from .response.utils import Headers, Cookie, URL

class OPTIONS(t.TypedDict):
    status: int
    statusText: str
    headers: Headers


class ConstructorOptions(t.TypedDict):
    url: URL
    redirect: bool
    type: str
    cookies: list[Cookie]


sendType = t.Callable[
    [
        HTTPResponseStartEvent
        | HTTPResponseBodyEvent
        | HTTPResponseTrailersEvent
        | HTTPServerPushEvent
        | HTTPDisconnectEvent
    ],
    t.Awaitable[None],
]

websocketSendEvents = (
    WebSocketAcceptEvent
    | WebSocketSendEvent
    | WebSocketResponseStartEvent
    | WebSocketResponseBodyEvent
    | WebSocketCloseEvent
)

websocketSendType = t.Callable[
    [websocketSendEvents],
    t.Awaitable[None],
]

websocketReceiveType = t.Callable[
    [],
    t.Awaitable[
        WebSocketConnectEvent | WebSocketReceiveEvent | WebSocketDisconnectEvent
    ],
]
