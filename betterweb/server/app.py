import uvicorn
from uvicorn._types import Scope, ASGIReceiveCallable, ASGISendCallable
import typing as t
from .api import APIRoute, WSRoute, Route, StaticRoute
from starlette.requests import Request
from .predefined.ws import WebsocketHandler

def read(path: str):
    with open(path, "rb") as f:
        return f.read()


class App:
    DEFAULT_PAGE = read("betterweb\\server\\default.html")

    def __init__(
        self,
        api_routes: "dict[str, APIRoute]",
        websocket_routes: "dict[str, WSRoute]",
        routes: "dict[str, Route]",
        static_routes: "dict[str, StaticRoute]",
        on_startup: t.Callable[[], None] | None = None,
        on_shutdown: t.Callable[[], None] | None = None,
    ):
        self.api_routes = api_routes
        self.websockets = websocket_routes
        self.routes = routes
        self.static_routes = static_routes

        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

        self.init()

    def init(self):
        WebsocketHandler.app_init(self)
        DEFAULT_ROUTE_PREFIX = "/__bw"
        DEFAULT_STATIC_ROUTES = {
            "/client.js": StaticRoute.from_file(
                "C:\\Users\\AJD21\\OneDrive\\Desktop\\Programming\\Python\\BetterWeb\\betterweb\\js\\dist\\conection.js",
                "application/javascript",
            ),
        }
        DEFAULT_WEBSOCKET_ROUTES = {
            "/ws": WSRoute("/ws", WebsocketHandler.init, close=False)
        }

        for path, route in DEFAULT_STATIC_ROUTES.items():
            self.static_routes[f"{DEFAULT_ROUTE_PREFIX}{path}"] = route

        for path, route in DEFAULT_WEBSOCKET_ROUTES.items():
            self.websockets[f"{DEFAULT_ROUTE_PREFIX}{path}"] = route

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    if self.on_startup:
                        self.on_startup()
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    if self.on_shutdown:
                        self.on_shutdown()
                    await send({"type": "lifespan.shutdown.complete"})
                    return

        elif scope["type"] == "http":
            if scope["path"] in self.api_routes:
                request = Request(scope, receive, send)
                await self.api_routes[scope["path"]](request, send)
                return
            elif scope["path"] in self.static_routes:
                print(f"Handling static route: {scope['path']}")
                await self.static_routes[scope["path"]](scope, receive, send)
            else:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [
                            (b"content-type", b"text/html; charset=utf-8"),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": self.DEFAULT_PAGE})
                return

        elif scope["path"] in self.websockets and scope["type"] == "websocket":
            await self.websockets[scope["path"]](send, receive)  # type: ignore[arg-type]
            return
        else:
            return

    def run(self, host="127.0.0.1", port=8000):
        uvicorn.run(
            self,
            host=host,
            port=port,
        )
