import typing as t
from .response.error import RouteError
from .response.constructor import ResponseConstructor
from ..dom import DOMNode, DOM
from .response import Headers, Cookie

if t.TYPE_CHECKING:
    from .types import (
        sendType,
        Request,
        websocketSendType,
        websocketReceiveType,
        HTTPScope,
        websocketSendEvents,
    )


class APIRoute:
    def __init__(
        self,
        methods: list[str],
        handler: 't.Callable[["Request", ResponseConstructor], t.Awaitable[None]]',
    ):
        self.methods = methods
        self.handler = handler

    async def __call__(
        self,
        request: "Request",
        send: "sendType",
    ) -> None:
        response = ResponseConstructor(
            send,
            {
                "url": request.url,
                "redirect": False,
                "type": "basic",
                "cookies": request.cookies,
            },
        )

        if request.method not in self.methods:
            raise RouteError(405, "Method Not Allowed", Headers())

        await self.handler(request, response)


T = t.TypeVar("T")


class Receive(t.TypedDict):
    bytes: t.Optional[bytes]
    text: t.Optional[str]


class Websocket:
    def __init__(self, send: "websocketSendType", receive: "websocketReceiveType"):
        self._send = send
        self._receive = receive

    async def accept(
        self,
        subprotocol: t.Optional[str] = None,
        headers: t.Optional[Headers] = None,
        cookies: "t.Optional[list[Cookie]]" = None,
    ):
        await self._send(
            {
                "type": "websocket.accept",
                "subprotocol": subprotocol,
                "headers": Headers(
                    (headers or []), Cookie=str(Cookie.to_dict(cookies or []))
                ),
            }
        )

    async def sendBytes(self, data: bytes):
        await self.send(bytes=data)

    async def sendText(self, data: str):
        await self.send(text=data)

    @t.overload
    async def send(self, /, *, bytes: bytes): ...

    @t.overload
    async def send(self, /, *, text: str): ...

    async def send(
        self, /, *, bytes: t.Optional[bytes] = None, text: t.Optional[str] = None
    ):
        assert (
            bytes is not None or text is not None
        ), "You must provide either 'bytes' or 'text'"
        assert not (
            bytes is not None and text is not None
        ), "You cannot provide both 'bytes' and 'text'"
        await self._send({"type": "websocket.send", "bytes": bytes, "text": text})  # type: ignore[arg-type]

    async def close(self, code: int = 1000, reason: t.Optional[str] = None):
        await self._send({"type": "websocket.close", "code": code, "reason": reason})

    async def receive(self) -> "Receive":
        while True:
            msg = await self._receive()
            if msg["type"] == "websocket.receive":
                return {
                    "bytes": msg.get("bytes", None),
                    "text": msg.get("text", None),
                }


class WSRoute:
    def __init__(self, handler: t.Callable[[Websocket], t.Awaitable[None]], close=True):
        self.handler = handler
        self.close = close

    async def __call__(
        self, send: "websocketSendType", receive: "websocketReceiveType"
    ) -> None:
        has_closed = False

        async def _send(data: "websocketSendEvents"):
            nonlocal has_closed
            if data["type"] == "websocket.close":
                has_closed = True
            return await send(data)

        msg = await receive()
        if msg["type"] == "websocket.connect":
            websocket = Websocket(_send, receive)
            await self.handler(websocket)

        if self.close and not has_closed:
            await send({"type": "websocket.close"})

class Route:
    def __init__(
        self,
        path: str,
        handler: t.Callable[[], t.Awaitable[t.Callable[[], t.Awaitable[DOMNode]]]],
    ):
        self.path = path
        self.handler = handler
        self._errors: "dict[int, t.Callable[[], t.Awaitable[DOMNode]]]" = {}
        self._loading: "t.Optional[t.Callable[[], t.Awaitable[DOMNode]]]" = None

    def add_error(self, status: int, handler: t.Callable[[], t.Awaitable[DOMNode]]):
        self._errors[status] = handler

    def set_loading(self, handler: t.Callable[[], t.Awaitable[DOMNode]]):
        self._loading = handler

    async def loading(self):
        if self._loading is not None:
            html = DOM.to_html(await self._loading())
            return html

    async def error(self, status: int):
        if status in self._errors:
            html = DOM.to_html(await self._errors[status]())
            return html


class StaticRoute:
    def __init__(self, path: str, data: bytes, mime: str):
        self.path = path
        self.data = data
        self.mime = mime

    @classmethod
    def from_file(cls, path: str, mime: str):
        with open(path, "rb") as f:
            content = f.read()
        return cls(path, content, mime)

    async def __call__(self, scope: "HTTPScope", receive, send: "sendType") -> None:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", self.mime.encode("ascii")),
                    (b"content-length", str(len(self.data)).encode("ascii")),
                ],
            }
        )

        await send({"type": "http.response.body", "body": self.data})
