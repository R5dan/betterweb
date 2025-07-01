from ..types import sendType, OPTIONS
from .response import Response
import typing as t


class StreamResponse(Response):
    def __init__(self, send: sendType, options: t.Optional[OPTIONS] = None):
        self._send = send
        self.options = options or {
            "status": 200,
            "statusText": "",
            "headers": {},
        }

    @classmethod
    async def init(cls, send: sendType, options: t.Optional[OPTIONS] = None):
        self = cls(send, options)

        await self._send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(k, v) for k, v in self.options["headers"].items()],
            }
        )

        return self

    async def send(self, data: bytes):
        await self._send(
            {
                "type": "http.response.body",
                "body": data,
                "more_body": True,
            }
        )

    async def close(self):
        await self._send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            }
        )
