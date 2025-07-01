from .constructor import ResponseConstructor
from ..types import Request, sendType

class APIError:
  def __init__(self, send: sendType, status: int, statusText: str, data: str, headers: dict[bytes, bytes]):
    self.send = send
    self.status = status
    self.statusText = statusText
    self.data = data
    self.headers = headers

  async def __call__(self, request: Request, response: ResponseConstructor):
    await response(None, {
      "status": self.status,
      "statusText": self.statusText,
      "headers": self.headers,
    })

def methodNotAllowed(send: sendType, allowed: list[str]):
  return APIError(send, 405, "Method Not Allowed", "Method Not Allowed", {
    b"Allow": ", ".join(allowed).encode(),
  })