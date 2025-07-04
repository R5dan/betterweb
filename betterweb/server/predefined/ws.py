import typing as t
import msgspec as ms
import asyncio as io
from .errors import ErrorHandler

if t.TYPE_CHECKING:
    from ..api import Websocket
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
    data: t.NotRequired[None]


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


class PushBody(t.TypedDict):
    type: t.Literal["push"]
    url: str
    client: bool

class ReplaceBody(t.TypedDict):
    type: t.Literal["replace"]
    url: str
    client: bool

class ReloadBody(t.TypedDict):
    type: t.Literal["reload"]
    client: bool

class BackBody(t.TypedDict):
    type: t.Literal["back"]


class ForwardBody(t.TypedDict):
    type: t.Literal["forward"]


class Router(t.TypedDict):
    type: t.Literal["router"]
    data: t.Union[PushBody, ReplaceBody, ReloadBody, BackBody, ForwardBody]


PROCESSES = t.Union[Console, ConsoleClear, HTML, LocalStorage, Router]


class WebsocketHandler:
    websocket: "Websocket" = None  # type: ignore[assignment]

    loc: str
    query: dict[str, str]
    hash: str

    app: "App"
    dirty: bool

    @classmethod
    def app_init(cls, app: "App"):
        cls.app = app

    @classmethod
    async def init(cls, websocket: "Websocket"):
        cls.websocket = websocket

        await websocket.accept()

        msg = await websocket.receive()
        if msg["bytes"]:
            data = ms.json.decode(msg["bytes"])
        elif msg["text"]:
            data = ms.json.decode(msg["text"])
        else:
            raise RuntimeError("Invalid request")
        
        assert isinstance(data, dict)
        assert data["type"] == "request"
        data = data["data"]

        while True:
            print(data)
            cls.loc = data["url"]
            cls.query = dict(data["query"])
            cls.hash = data["hash"]
            cls.dirty = True
            route = cls.app.routes[cls.loc]
            loading = await route.loading()
            if loading is not None:
                await cls.send(
                    {
                        "type": "html",
                        "data": loading,
                    }
                )
            from ..dom import DOM
            try:
                client = await route.handler()

                while True:
                    if cls.dirty:
                        try:
                            # Import DOM here to avoid circular import
                                html = DOM.to_html(await client())
                                await cls.send(
                                    {
                                        "type": "html",
                                        "data": html,
                                    }
                                )
                                cls.dirty = False

                        except Exception as exc:
                            # Import RouteError here to avoid circular import
                            from ..api.response.error import RouteError

                            if isinstance(exc, RouteError):
                                err = await route.error(exc.status)
                                if err is not None:

                                    await cls.send({
                                        "type": "html",
                                        "data": err,
                                    })
                                else:
                                    await cls.send(
                                    {
                                        "type": "html",
                                        "data": DOM.to_html(ErrorHandler(exc.status).h())
                                    }
                                )
                            else:
                                await cls.send(
                                {
                                    "type": "html",
                                    "data": DOM.to_html(ErrorHandler(500).h())
                                }
                                )

                    msg = await cls.websocket.receive()
                    data = ms.json.decode(msg["text"])  # type: ignore[assignment]
    
                    if data["type"] == "request":
                        break

                    elif data["type"] == "event":
                        # Import DOM here to avoid circular import

                        print(DOM.events)

                        handler = DOM.events[data["data"]["id"]][data["data"]["event"]]
                        if io.iscoroutinefunction(handler):
                            await handler()
                        else:
                            handler()

                    else:
                        raise RuntimeError("Invalid request")

            except Exception as exc:
                # Import RouteError here to avoid circular import
                from ..api.response.error import RouteError
                print("Error", exc)
                if isinstance(exc, RouteError):
                    err = await route.error(exc.status)
                    print("Response", err)
                    if err is not None:
                        print("Sending Error")
                        await cls.send(
                            {
                                "type": "html",
                                "data": err,
                            }
                        )
                    else:
                        await cls.send(
                            {
                                "type": "html",
                                "data": DOM.to_html(ErrorHandler(exc.status).h())
                            }
                        )
                else: 
                    await cls.send(
                        {
                            "type": "html",
                            "data": DOM.to_html(ErrorHandler(500).h())
                        }
                    )
                break

    @classmethod
    def schedule_render(cls):
        cls.dirty = True

    @classmethod
    async def send(cls, data: PROCESSES):
        await cls.websocket.sendBytes(ms.json.encode(data))

    @classmethod
    async def receive(cls):
        return await cls.websocket.receive()
