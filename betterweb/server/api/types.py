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
from starlette.requests import Request


class OPTIONS(t.TypedDict):
    status: int
    statusText: str
    headers: dict[bytes, bytes]


class ConstructorOptions(t.TypedDict):
    url: str
    redirect: bool
    type: str
    cookies: dict[str, str]


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
