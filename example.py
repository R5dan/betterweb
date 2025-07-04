from betterweb import (
    App,
    APIRoute,
    WSRoute,
    ResponseConstructor,
    Websocket,
    Route,
    Console,
    DOM,
    StaticRoute,
    RouteError,
    Request,
    use_state,
    use_memo,
    Headers,
    Router
)
import time
import asyncio


async def get(request: Request, response: ResponseConstructor):
    await response.json({"method": "GET"})


async def post(request: Request, response: ResponseConstructor):
    await response.json({"method": "POST"})


async def stream(request: Request, response: ResponseConstructor):
    stream = await response.stream()
    print("Sending")
    for i in range(10):
        await stream.send(f"Hello World {i}\n".encode())
        await asyncio.sleep(1)
    print("Closing")
    await stream.close()

async def on_click():
    print("CLICK")
    await Router.push("/get")


async def page():
    async def client():
        await Console.log("Hello World")

        def complex_func():
            print("COMPLEX")
            #time.sleep(10)

        count, setCount = use_state("counter", 0)
        use_memo(complex_func, [count])
        return DOM.create(
            "div",
            {},
            [
                DOM.create(
                    "Error",
                    {
                        "onclick": on_click
                    },
                    ["Click Me"],
                ),
            ],
        )

    return client


async def ws(ws: Websocket):
    await ws.accept()
    while True:
        msg = await ws.receive()
        if msg["text"]:
            print(msg["text"])
            await ws.sendText(msg["text"])


app = App(
    api_routes={
        "/get": APIRoute(["GET"], get),
        "/post": APIRoute(["POST"], post),
        "/stream": APIRoute(["GET"], stream),
    },
    websocket_routes={"/ws": WSRoute(ws)},
    routes={"/": Route("/", page)},
    static_routes={
        #        "/static": StaticRoute.from_file("static/index.html", "text/html")
        #        "/client/client.js": StaticRoute.from_file("path/to/file.js", "application/javascript")
    },
)

app.run()
