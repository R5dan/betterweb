import re
import typing as t
from .....client import Router

class URL:
    REGEX = re.compile(
        "([a-zA-Z][a-zA-Z0-9+.-]*):\\/\\/(?:([^/#?:@]*)(?::([0-9]*))?@)?(?:([^#:]*)(?::([0-9]+))?)?(?:([^?#]*))(?:\\?([^#]*))?(?:#(.*))?"
    )

    @t.overload
    def __init__(self, url: str, base: str): ...

    @t.overload
    def __init__(self, url: str): ...

    def __init__(self, url: str, base: t.Optional[str] = None):
        self.url = url
        self.base = base
        self.resolved = f"{self.base if self.base else ''}{self.url}"

        r = self.REGEX.match(self.resolved)
        if r:
            self._scheme = r.group(1)
            self._username = r.group(2)
            self._password = r.group(3)
            self._hostname = r.group(4)
            self._port = r.group(5)
            self._path = r.group(6)
            self._query = r.group(7)
            self._hash = r.group(8)

    def __str__(self):
        return self.resolved

    @property
    def hash(self):
        return self._hash

    @property
    def host(self):
        if self._port:
            return f"{self._hostname}:{self._port}"
        return self._hostname

    @property
    def hostname(self):
        return self._hostname

    @property
    def href(self):
        return self.resolved

    @href.setter
    async def href(self, value: str):
        await Router.push(value)

    @property
    def origin(self):
        if self._port:
            return f"{self._scheme}://{self._hostname}:{self._port}"
        return f"{self._scheme}://{self._hostname}"

    @property
    def password(self):
        return self._password

    @property
    def pathname(self):
        return self._path

    @property
    def port(self):
        return self._port

    @property
    def protocol(self):
        return self._scheme

    @property
    def search(self):
        return self._query

    @property
    def username(self):
        return self._username
