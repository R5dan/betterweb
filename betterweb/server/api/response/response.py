import typing as t
import msgspec as ms
from ..types import ConstructorOptions, OPTIONS

class Response:
    """
    DO NOT INITIALIZE THIS CLASS DIRECTLY

    USE `ResponseConstructor`
    """

    def __init__(
        self,
        body: t.Optional[bytes],
        options: OPTIONS,
        constructor: ConstructorOptions,
    ):
        self._body = body
        self._options = options
        self._url = constructor["url"]
        self._redirect = constructor["redirect"]
        self._type = constructor["type"]

        options = options

        self._status = options["status"]
        self._statusText = options["statusText"]
        self._headers = options["headers"]
        self._cookies = constructor["cookies"]

    @property
    def body(self):
        return self._body

    @property
    def bodyUsed(self):
        pass

    @property
    def headers(self):
        return self._headers

    @property
    def ok(self):
        return self._status >= 200 and self._status < 300

    @property
    def redirected(self):
        return self._redirect

    @property
    def status(self):
        return self._status

    @property
    def statusText(self):
        return self._statusText

    @property
    def type(self):
        return self._type

    @property
    def url(self):
        return self._url

    @property
    def cookies(self):
        self._cookies

    def json(self):
        return ms.json.decode(self._body)

    def arrayBuffer(self):
        pass

    def blob(self):
        pass

    def clone(self):
        pass

    def formData(self):
        pass

    def text(self):
        pass
