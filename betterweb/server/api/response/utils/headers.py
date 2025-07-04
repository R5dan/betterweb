import typing as t

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
