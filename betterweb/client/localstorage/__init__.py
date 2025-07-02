from ...server.predefined.ws import WebsocketHandler
import msgspec as ms
import typing as t


class LocalStorageReceive(t.TypedDict):
    type: t.Literal["ls-receive"]
    data: dict[str, str]

class LocalStorage:
  ws: WebsocketHandler

  storage = {}

  @classmethod
  async def get(cls, key: str) -> t.Optional[t.Any]:
    await cls.ws.send({"type": "ls", "data": {"type": "get"}})
    
    msg = await cls.ws.receive()

    if msg["bytes"]:
      data: LocalStorageReceive = ms.json.decode(msg["bytes"])
    elif msg["text"]:
      data = ms.json.decode(msg["text"])
    else:
      raise RuntimeError("Websocket did not send data")
    
    cls.storage = data["data"]

    return data.get(key, None)
  
  @classmethod
  async def set(cls, key: str, value: t.Any):
    cls.storage[key] = value
    await cls.ws.send({"type": "ls", "data": {"type": "set", "data": {key: value}}})
