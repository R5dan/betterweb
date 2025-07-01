import typing as t
from .types import (
    sendType,
    Request,
    websocketSendType,
    websocketReceiveType,
    HTTPScope,
    websocketSendEvents,
)
from .response.constructor import ResponseConstructor
from .response.error import methodNotAllowed
from ..dom import DOMNode, DOM

class APIRoute:
    def __init__(
        self,
        path: str,
        methods: list[str],
        handler: t.Callable[[Request, ResponseConstructor], t.Awaitable[None]],
    ):
        self.path = path
        self.methods = methods
        self.handler = handler

    async def __call__(
        self,
        request: Request,
        send: sendType,
    ) -> None:
        response = ResponseConstructor(
            send,
            {
                "url": request.url.path,
                "redirect": False,
                "type": "basic",
                "cookies": request.cookies,
            },
        )

        if request.method not in self.methods:
            await methodNotAllowed(send, self.methods)(request, response)
            return

        await self.handler(request, response)


class Websocket:
    def __init__(self, send: websocketSendType, receive: websocketReceiveType):
        self._send = send
        self._receive = receive

    async def accept(
        self,
        subprotocol: t.Optional[str] = None,
        headers: t.Optional[list[tuple[bytes, bytes]]] = None,
    ):
        await self._send(
            {
                "type": "websocket.accept",
                "subprotocol": subprotocol,
                "headers": headers or [],
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
        await self._send({"type": "websocket.send", "bytes": bytes, "text": text})

    async def close(self, code: int = 1000, reason: t.Optional[str] = None):
        await self._send({"type": "websocket.close", "code": code, "reason": reason})

    async def receive(self):
        while True:
            msg = await self._receive()
            if msg["type"] == "websocket.receive":
                return {
                    "bytes": msg.get("bytes", None),
                    "text": msg.get("text", None),
                }


class WSRoute:
    def __init__(
        self, path: str, handler: t.Callable[[Websocket], t.Awaitable[None]], close=True
    ):
        self.path = path
        self.handler = handler
        self.close = close

    async def __call__(
        self, send: websocketSendType, receive: websocketReceiveType
    ) -> None:
        has_closed = False

        async def _send(data: websocketSendEvents):
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

    async def __call__(self) -> str:
        client = await self.handler()
        html = DOM.to_html(await client())
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

    async def __call__(self, scope: HTTPScope, receive, send: sendType) -> None:
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
