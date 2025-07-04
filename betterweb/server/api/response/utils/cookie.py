import typing as t
from datetime import datetime

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
