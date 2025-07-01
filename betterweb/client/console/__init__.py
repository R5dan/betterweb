from ...server.predefined.ws import WebsocketHandler

class Console:
  ws = WebsocketHandler()

  @classmethod
  def log(cls, data: str):
    return cls.ws.send({"type": "console", "data": {"type": "log", "message": data}})

  @classmethod
  def clear(cls):
    return cls.ws.send({"type": "console-clear"})
