from .response import Response
import typing as t
from .utils import Headers

if t.TYPE_CHECKING:
    from ..types import sendType, OPTIONS

class StreamResponse(Response):
    def __init__(self, send: 'sendType', options: 't.Optional[OPTIONS]' = None):
        self._send = send
        self.options = options or {
            "status": 200,
            "statusText": "",
            "headers": Headers(),
        }

    @classmethod
    async def init(cls, send: 'sendType', options: 't.Optional[OPTIONS]' = None):
        self = cls(send, options)

        await self._send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": self.options["headers"],
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
