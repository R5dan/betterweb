from uvicorn._types import (
    HTTPScope,
    LifespanScope,
    HTTPRequestEvent,
    HTTPDisconnectEvent
)
import typing as t
import msgspec as ms
from http import cookies
from .response.utils import Cookie, URL

ASGIReceiveEvent = t.Union[
    HTTPRequestEvent,
    HTTPDisconnectEvent,
]

ASGIReceiveCallable = t.Callable[[], t.Awaitable[ASGIReceiveEvent]]

def cookie_parser(cookie_string: str) -> dict[str, str]:
    ret = {}
    for cookie in cookie_string.split(";"):
        if "=" in cookie:
            if "=" in cookie:
                key, value = cookie.split("=", 1)
            else:
                key, value = cookie, ""

            ret[key.strip()] = cookies._unquote(value.strip())
    return ret


class Request:
    def __init__(self, scope: HTTPScope, receive: ASGIReceiveCallable):
        self._scope = scope
        self._receive = receive
        self._body_consumed = False

    @property
    def scope(self) -> HTTPScope:
        return self._scope

    @property
    def receive(self) -> ASGIReceiveCallable:
        return self._receive

    @property
    def http_version(self) -> str:
        return self.scope["http_version"]
    
    @property
    def cookies(self):
        return [Cookie(k, v) for k, v in cookie_parser(self.headers.get(b"cookie", b"").decode()).items()]

    @property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def url(self) -> URL:
        return URL(self.scope["raw_path"].decode())

    @property
    def scheme(self) -> str:
        return self.scope["scheme"]

    @property
    def path(self) -> str:
        return self.scope["path"]

    @property
    def raw_path(self) -> bytes:
        return self.scope["raw_path"]

    @property
    def query_string(self) -> bytes:
        return self.scope["query_string"]

    @property
    def root_path(self) -> str:
        return self.scope["root_path"]

    @property
    def headers(self) -> dict[bytes, bytes]:
        return dict(self.scope["headers"])

    @property
    def client(self) -> tuple[str, int] | None:
        return self.scope["client"]

    @property
    def server(self) -> tuple[str, int | None] | None:
        return self.scope["server"]

    @property
    def state(self) -> LifespanScope | None:
        return self.scope.get("state", None) # type: ignore[return-value]

    @property
    def extensions(self) -> dict[str, dict[object, object]]:
        return self.scope.get("extensions", {})

    def __getitem__(self, key: str):
        return self.scope[key]

    def __iter__(self) -> t.Iterator[str]:
        return iter(self.scope)

    def __len__(self) -> int:
        return len(self.scope)

    async def _fetch_body(self):
        if self._body_consumed:
            return

        body = b""
        iter = []
        more_body = True
        while more_body:
            message = await self._receive()
            assert message["type"] == "http.request"
            body += message.get("body")
            iter.append(message.get("body"))
            more_body = message.get("more_body", False)

        self._body_consumed = True
        self._body_iter = iter
        self._body = body

    async def json(self):
        if not self._body_consumed:
            await self._fetch_body()

        if hasattr(self, "_json"):
            return self._json

        if hasattr(self, "_body"):
            self._json = ms.json.decode(self._body)
            return self._json

    async def stream(self):
        if self._body_consumed:
            for body in self._body_iter:
                yield body
            return

        more_body = True
        self._body = b""
        self._body_iter = []

        while more_body:
            message = await self._receive()
            assert message["type"] == "http.request"
            body = message.get("body")

            self._body_iter.append(message.get("body")) 
            self._body += body
            more_body = message.get("more_body", False)
            yield body

    async def text(self):
        if not self._body_consumed:
            await self._fetch_body()

        return self._body.decode()