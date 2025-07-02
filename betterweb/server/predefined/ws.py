import typing as t
from ..api import Websocket
import msgspec as ms
from ..dom import DOM
import asyncio as io

if t.TYPE_CHECKING:
    from ..app import App

JSONTYPES = t.Union[
    str, int, float, bool, None, dict["JSONTYPES", "JSONTYPES"], list["JSONTYPES"]
]

T = t.TypeVar("T", bound=str)
D = t.TypeVar("D", bound=JSONTYPES)


class Process(t.TypedDict, t.Generic[T, D]):
    type: T
    data: D


class ConsoleSchema(t.TypedDict):
    type: t.Union[
        t.Literal["log"], t.Literal["error"], t.Literal["warn"], t.Literal["info"]
    ]
    message: str


class Console(t.TypedDict):
    type: t.Literal["console"]
    data: ConsoleSchema


class ConsoleClear(t.TypedDict):
    type: t.Literal["console-clear"]
    data: None


class HTML(t.TypedDict):
    type: t.Literal["html"]
    data: str


class LocalStorageType(t.TypedDict, t.Generic[T]):
    type: T

class LocalStorageSet(LocalStorageType[t.Literal["set"]]):
    data: dict[str, str]

class LocalStorage(t.TypedDict):
    type: t.Literal["ls"]
    data: t.Union[LocalStorageType[t.Literal["get"]], LocalStorageSet]

PROCESSES = t.Union[Console, ConsoleClear, HTML, LocalStorage]

class WebsocketHandler:
    websocket: Websocket = None

    loc: str
    query: dict[str, str]
    hash: str

    app: "App"
    dirty: bool = True

    @classmethod
    def app_init(cls, app: "App"):
        cls.app = app

    @classmethod
    async def init(cls, websocket: Websocket):
        cls.websocket = websocket

        await websocket.accept()
        msg = await websocket.receive()
        if msg["bytes"]:
            data = ms.json.decode(msg["bytes"])
            cls.loc = data["url"]
            cls.query = dict(data["query"])
            cls.hash = data["hash"]
        elif msg["text"]:
            data = ms.json.decode(msg["text"])
            cls.loc = data["data"]["url"]
            cls.query = dict(data["data"]["query"])
            cls.hash = data["data"]["hash"]
        else:
            raise RuntimeError("Websocket not initialized")

        route = cls.app.routes[cls.loc]
        while True:
            if cls.dirty:
                client = await route()
                await cls.send(
                    {
                        "type": "html",
                        "data": client,
                    }
                )
                cls.dirty = False

            msg = await cls.websocket.receive()
            data = ms.json.decode(msg["text"])

            handler = DOM.events[data["data"]["id"]][data["data"]["event"]]
            if io.iscoroutinefunction(handler):
                await handler()
            else:
                handler()

    @classmethod
    def schedule_render(cls):
        cls.dirty = True

    @classmethod
    async def send(cls, data: PROCESSES):
        await cls.websocket.sendBytes(ms.json.encode(data))

    @classmethod
    async def receive(cls):
        return await cls.websocket.receive()
