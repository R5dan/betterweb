import typing as t
import msgspec as ms

if t.TYPE_CHECKING:
    from ..types import sendType, ConstructorOptions, OPTIONS
from .stream import StreamResponse
from .response import Response
from datetime import datetime
from .utils import Headers, Cookie


class ResponseConstructor:
    def __init__(
        self,
        send: "sendType",
        options: "ConstructorOptions",
    ):
        self.send = send
        self.options = options
        self.cookies = []

    async def __call__(
        self, body: t.Optional[bytes] = None, options: t.Optional["OPTIONS"] = None
    ):
        options = options or {
            "status": 200,
            "statusText": "",
            "headers": Headers(),
        }
        await self.send(
            {
                "type": "http.response.start",
                "status": options["status"],
                "headers": options["headers"],
            }
        )
        await self.send(
            {
                "type": "http.response.body",
                "body": b"",
            }
        )
        return Response(body, options, self.options)

    def cookie(
        self,
        name: str,
        value: str,
        domain: t.Optional[str] = None,
        path: t.Optional[str] = None,
        maxage: t.Optional[int] = None,
        expires: t.Optional[datetime] = None,
        https_only: bool = False,
        secure: bool = False,
    ):
        """
        Sets a cookie to be sent with the response.

        Only one of `maxage` or `expires` should be provided.
        If neither is provided, the cookie will be a session cookie.

        Parameters:
            name (str): The name of the cookie.
            value (str): The value of the cookie.

            domain (str, optional): The domain of the cookie. Defaults to None: host-only cookie - no subdomains.
            path (str, optional): The path of the cookie. Defaults to None: All paths included.
            max_age (int, optional): The max age of the cookie in seconds. Defaults to None: No max age.
            expires (datetime, optional): The expiration date of the cookie. Defaults to None: No expiration date.
            https_only (bool, optional): Whether the cookie should only be sent over HTTPS. Defaults to False.
            secure (bool, optional): Whether the cookie should only be sent over HTTPS. Defaults to False.
        """

        self.cookies.append(
            Cookie(name, value, domain, path, maxage, expires, https_only, secure)
        )

        return self

    def error(self):
        pass

    def redirect(self):
        pass

    async def start(self, status: int, headers: Headers):
        await self.send(
            {"type": "http.response.start", "status": status, "headers": headers}
        )

    async def json(self, data: dict, options: t.Optional["OPTIONS"] = None):
        json = ms.json.encode(data)

        options = options or {"status": 200, "headers": Headers(), "statusText": ""}

        await self.start(
            options["status"],
            options["headers"],
        )

        await self.send(
            {
                "type": "http.response.body",
                "body": json,
            }
        )

        return Response(json, options, self.options)

    async def stream(self, options: t.Optional["OPTIONS"] = None):
        return await StreamResponse.init(self.send, options)
