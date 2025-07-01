import typing as t
import msgspec as ms
from ..types import sendType, ConstructorOptions, OPTIONS
from .stream import StreamResponse
from .response import Response

class ResponseConstructor:
    def __init__(
        self,
        send: sendType,
        options: ConstructorOptions,
    ):
        self.send = send
        self.options = options

    async def __call__(
        self, body: t.Optional[bytes] = None, options: t.Optional[OPTIONS] = None
    ):
        options = options or {
            "status": 200,
            "statusText": "",
            "headers": {},
        }
        await self.send(
            {
                "type": "http.response.start",
                "status": options["status"],
                "headers": [(k, v) for k, v in options["headers"].items()],
            }
        )
        await self.send(
            {
                "type": "http.response.body",
                "body": b"",
            }
        )
        return Response(body, options, self.options)

    def error(self):
        pass

    def redirect(self):
        pass

    async def json(self, data: dict, options: t.Optional[OPTIONS] = None):
        json = ms.json.encode(data)
        options = options or {
            "status": 200,
            "statusText": "",
            "headers": {},
        }
        await self.send(
            {
                "type": "http.response.start",
                "status": options["status"],
                "headers": [(k, v) for k, v in options["headers"].items()],
            }
        )

        await self.send(
            {
                "type": "http.response.body",
                "body": json,
            }
        )

        return Response(json, options, self.options)

    async def stream(self, options: t.Optional[OPTIONS] = None):
        return await StreamResponse.init(self.send, options)
