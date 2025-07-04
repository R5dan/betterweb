from ...server.predefined.ws import WebsocketHandler
import msgspec as ms
import typing as t

T = t.TypeVar("T")


class Router:
    ws = WebsocketHandler()

    @classmethod
    async def push(cls, url: str):
        await cls.ws.send({"type": "router", "data": {"type": "push", "url": url}})

    @classmethod
    async def replace(cls, url: str):
        await cls.ws.send({"type": "router", "data": {"type": "replace", "url": url}})

    @classmethod
    async def reload(cls):
        await cls.ws.send({"type": "router", "data": {"type": "reload"}})

    @classmethod
    async def back(cls):
        await cls.ws.send({"type": "router", "data": {"type": "back"}})

    @classmethod
    async def forward(cls):
        await cls.ws.send({"type": "router", "data": {"type": "forward"}})
