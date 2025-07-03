# BetterWeb

A simple web framework for Python.

## Installation

```bash
pip install betterweb
uv add betterweb
```

## Diagram

![Better Web Excalidraw](https://github.com/user-attachments/assets/818f0696-3152-4a63-82a4-84be16a61d35)

## Limitations

- Only SSR, no logic is executed on the client
- Only can edit the children of the `<body>` tag in a normal route. No changing the `<head>` or `<html>` tag
- For non-static routes, the server must always be running
- 99% async
- Currently no dev mode / hot reload

## Example

> [!NOTE]
> See the [example](https://github.com/r5dan/BetterWeb/blob/main/example.py) for a more complete example.
![Uploading Better Web Excalidraw.svg…]()

## Documentation

### App

The `App` class is the main class of the `betterweb` package. It is used to create an instance of the app and run it.

#### `App(api_routes: dict[str, APIRoute], websocket_routes: dict[str, WSRoute], routes: dict[str, Route], static_routes: dict[str, StaticRoute], on_startup: Callable[[], None] = None, on_shutdown: Callable[[], None] = None)`

Creates a new instance of the `App` class.

-   `api_routes`: A dictionary of API routes. The key is the route path, and the value is an `APIRoute` object.
-   `websocket_routes`: A dictionary of websocket routes. The key is the route path, and the value is a `WSRoute` object.
-   `routes`: A dictionary of routes. The key is the route path, and the value is a `Route` object.
-   `static_routes`: A dictionary of static routes. The key is the route path, and the value is a `StaticRoute` object.
-   `on_startup`: A function to be called when the app starts.
-   `on_shutdown`: A function to be called when the app stops.

#### `run(host: str = "127.0.0.1", port: int = 8000)`

Runs the app.

-   `host`: The host to run the app on.
-   `port`: The port to run the app on.

### APIRoute

The `APIRoute` class is used to define an API route.

#### `APIRoute(path: str, methods: list[str], handler: Callable[[Request, ResponseConstructor], Awaitable[None]])`

Creates a new instance of the `APIRoute` class.

-   `path`: The path of the route.
-   `methods`: A list of HTTP methods that the route supports.
-   `handler`: The handler function for the route. Should return `None` but accept a `Request` and `ResponseConstructor` object.

### ResponseConstructor

The `ResponseConstructor` class is used to construct a response.

#### `ResponseConstructor.__call__(body: Optional[bytes] = None, options: Optional[OPTIONS] = None)`

Creates a new instance of the `ResponseConstructor` class.

-   `body`: The body of the response.
-   `options`: The options of the response.

#### `ResponseConstructor.error()`

#### `ResponseConstructor.redirect()`

#### `ResponseConstructor.json(data: dict, options: Optional[OPTIONS] = None)`

#### `ResponseConstructor.stream(options: Optional[OPTIONS] = None)`

Returns a `StreamResponse` object.

##### `StreamResponse.send(data: bytes)`

Sends data to the stream.

##### `StreamResponse.close()`

Closes the stream.

### WSRoute

The `WSRoute` class is used to define a websocket route.

#### `WSRoute(path: str, handler: Callable[[Websocket], Awaitable[None]], close: bool = True)`

Creates a new instance of the `WSRoute` class.

-   `path`: The path of the route.
-   `handler`: The handler function for the route.
-   `close`: Whether to close the websocket connection after the handler function is called.

### Route

The `Route` class is used to define a route.

#### `Route(path: str, handler: Callable[[], Awaitable[Callable[[], Awaitable[DOMNode]]]])`

Creates a new instance of the `Route` class.

-   `path`: The path of the route.
-   `handler`: The handler function for the route.

The handler function should return an async function
The returned function is called the client function
The handler function is called the server function

The client function should return a DOM node
It will be called whenever the state changes
Client APIs like `Console` can only be called from the client function

The server function should return the client function
It will be called exactly once before any response is sent
Client APIs like `Console` can not be called from the server function as the response has not been sent yet

### DOM

The `DOM` class is used to create DOM nodes.

#### `DOM.create(tag: str, properies: dict, children: list[DOMNode | str])`

Creates a new DOM node.

-   `tag`: The tag of the DOM node.
-   `properies`: The properties of the DOM node.
-   `children`: The children of the DOM node.

### StaticRoute

The `StaticRoute` class is used to define a static route.

#### `StaticRoute(path: str, data: bytes, mime: str)`

Creates a new instance of the `StaticRoute` class.

-   `path`: The path of the route.
-   `data`: The data of the route.
-   `mime`: The MIME type of the route.

#### `StaticRoute.from_file(path: str, mime: str)`

Creates a new instance of the `StaticRoute` class from a file.

-   `path`: The path of the file.
-   `mime`: The MIME type of the file.

### State

#### `use_state(name: str, initial: T | Callable[[], T] = None) -> Tuple[T, Callable[[T], None]]`

Creates a stateful value.

-   `name`: The name of the state. Has no  effect on the state, but is used to identify it.
-   `initial`: The initial value of the state.

#### `use_memo(func: Callable[[], None | Callable[[], None]], deps: list[Any] = None)`

Creates a memoized value.
Is run when the dependencies change.

-   `func`: The function to memoize. The name must be unique.
-   `deps`: The dependencies of the memoized value. Optional: defaults to an empty list.

Returns:

- None
- Cleanup function - Called immediately before the next render
