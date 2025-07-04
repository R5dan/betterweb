from .utils import Headers

class RouteError(Exception):
    def __init__(self, status: int, statusText: str, headers: Headers):
        self.status = status
        self.statusText = statusText
        self.headers = headers

    def throw(self):
        raise self