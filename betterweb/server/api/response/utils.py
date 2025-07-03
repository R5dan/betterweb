import typing as t
from datetime import datetime
from ....client.router import Router
from ..types import HTTPScope, WebSocketScope


class Cookie:
    def __init__(
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
        self.name = name
        self.value = value
        self.domain = domain
        self.path = path
        self.maxage = maxage
        self.expires = expires
        self.https_only = https_only
        self.secure = secure

    def __str__(self):
        options = []

        if self.domain:
            options.append(f"Domain={self.domain}")

        if self.path:
            options.append(f"Path={self.path}")

        if self.maxage:
            options.append(f"Max-Age={self.maxage}")

        if self.expires:
            options.append(
                f"Expires={self.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            )

        if self.https_only:
            options.append("HttpOnly")

        if self.secure:
            options.append("Secure")

        return f"{self.name}={self.value}; {"; ".join(options)}"

    @staticmethod
    def to_dict(cookies: "list[Cookie]"):
        return {cookie.name: cookie.value for cookie in cookies}


class Headers:
    def __init__(
        self,
        headers: "t.Iterable[tuple[bytes | str, bytes | str]]" = [],
        **kwargs: "str | bytes",
    ):
        heads: "list[tuple[bytes, bytes]]" = []

        for k, v in headers:
            if isinstance(k, str):
                k = k.encode()
            if isinstance(v, str):
                v = v.encode()
            heads.append((k, v))

        for k, v in kwargs.items():
            if isinstance(k, str):
                k = k.encode()
            if isinstance(v, str):
                v = v.encode()
            heads.append((k, v))

        self.headers = heads

    @t.overload
    def get(self, key: str | bytes, bytes: t.Literal[False] = False) -> list[str]: ...

    @t.overload
    def get(self, key: str | bytes, bytes: t.Literal[True] = True) -> list[bytes]: ...

    def get(self, key: str | bytes, bytes: bool = False):  # type: ignore[override]
        if isinstance(key, str):
            key = key.encode()
        return [v.decode() if bytes else v for k, v in self.headers if k == key]

    def __getitem__(self, key: str | bytes):
        return self.get(key)

    @t.overload
    def items(self, bytes: t.Literal[False] = False) -> list[tuple[str, str]]: ...

    @t.overload
    def items(self, bytes: t.Literal[True]) -> list[tuple[bytes, bytes]]: ...

    def items(self, bytes: bool = False):
        if bytes:
            return self.headers
        return [(k.decode(), v.decode()) for k, v in self.headers]

    def __iter__(self):
        return iter(self.headers)

    def __len__(self):
        return len(self.headers)

    def __eq__(self, other: t.Any) -> bool:
        if not isinstance(other, Headers):
            return False
        return self.headers == other.headers

    def __contains__(self, key: str | bytes):
        if isinstance(key, str):
            key = key.encode()
        return any(k == key for k, v in self.headers)

    def __bool__(self):
        return bool(self.headers)


import re


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
