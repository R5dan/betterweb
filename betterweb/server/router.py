from .api import APIRoute, WSRoute, Route, StaticRoute
import typing as t
from .dom import DOMNode

class Router:
    def __init__(
        self,
        api_routes: "t.Optional[dict[str, APIRoute]]" = None,
        websocket_routes: "t.Optional[dict[str, WSRoute]]" = None,
        routes: "t.Optional[dict[str, Route]]" = None,
        static_routes: "t.Optional[dict[str, StaticRoute]]" = None,
    ):
        self.api_routes = api_routes or {}
        self.websockets = websocket_routes or {}
        self.routes = routes or {}
        self.static_routes = static_routes or {}

    def add_router(self, router: "Router", prefix: t.Optional[str] = None):
        self.api_routes.update(
            {f"{prefix}{path}": route for path, route in router.api_routes.items()}
        )
        self.websockets.update(
            {f"{prefix}{path}": route for path, route in router.websockets.items()}
        )
        self.routes.update(
            {f"{prefix}{path}": route for path, route in router.routes.items()}
        )
        self.static_routes.update(
            {f"{prefix}{path}": route for path, route in router.static_routes.items()}
        )

    @property
    def endpoints(self):
        return (
            list(self.api_routes.keys())
            + list(self.websockets.keys())
            + list(self.routes.keys())
            + list(self.static_routes.keys())
        )

    def add_error_handler(self, status: int, handler: t.Callable[[], t.Awaitable[DOMNode]]):
        for route in self.routes.values():
            route.add_error(status, handler)
    
    def add_loading_handler(self, handler: t.Callable[[], t.Awaitable[DOMNode]]):
        for route in self.routes.values():
            route.set_loading(handler)