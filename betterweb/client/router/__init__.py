from ...server.predefined.ws import WebsocketHandler
import msgspec as ms
import typing as t

T = t.TypeVar("T")


class Router:
    ws = WebsocketHandler()

    @classmethod
    async def push(cls, url: str, client: 't.Optional[bool]' = None):
        if client == None and url in cls.ws.app.routes:
            client = True

        await cls.ws.send({"type": "router", "data": {"type": "push", "url": url, "client": client}})

    @classmethod
    async def replace(cls, url: str, client: 't.Optional[bool]' = None):
        if client == None and url in cls.ws.app.routes:
            client = True

        await cls.ws.send({"type": "router", "data": {"type": "replace", "url": url}})

    @classmethod
    async def reload(cls, client: bool = True):
        await cls.ws.send({"type": "router", "data": {"type": "reload", "client": client}})

    @classmethod
    async def back(cls):
        await cls.ws.send({"type": "router", "data": {"type": "back"}})

    @classmethod
    async def forward(cls):
        await cls.ws.send({"type": "router", "data": {"type": "forward"}})
