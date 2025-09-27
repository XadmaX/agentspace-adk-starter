"""A tiny subset of the httpx API used for Starlette's TestClient.

This module is **not** a drop-in replacement for the real `httpx` package.
It only implements the minimal surface area that the Starlette test client
relies on so that our unit tests can run in environments where the actual
dependency is unavailable (for example, offline execution sandboxes).
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urljoin, urlsplit

from . import _client, _types

CookieTypes = _types.CookieTypes
URLTypes = _types.URLTypes
RequestContent = _types.RequestContent
RequestFiles = _types.RequestFiles
QueryParamTypes = _types.QueryParamTypes
HeaderTypes = _types.HeaderTypes
AuthTypes = _types.AuthTypes
TimeoutTypes = _types.TimeoutTypes
UseClientDefault = _client.UseClientDefault
USE_CLIENT_DEFAULT = _client.USE_CLIENT_DEFAULT


class Headers:
    """A very small case-insensitive headers container."""

    def __init__(self, initial: Iterable[tuple[str, str]] | None = None) -> None:
        self._items: list[tuple[str, str]] = []
        if initial:
            for key, value in initial:
                self.add(key, value)

    def add(self, key: str, value: str) -> None:
        self._items.append((key, value))

    def get(self, key: str, default: str | None = None) -> str | None:
        key_lower = key.lower()
        for candidate, value in reversed(self._items):
            if candidate.lower() == key_lower:
                return value
        return default

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        key_lower = key.lower()
        return any(candidate.lower() == key_lower for candidate, _ in self._items)

    def multi_items(self) -> list[tuple[str, str]]:
        return list(self._items)

    def copy(self) -> Headers:
        return Headers(self._items)

    def extend(self, other: Iterable[tuple[str, str]]) -> None:
        for key, value in other:
            self.add(key, value)


class ByteStream:
    """A trivial byte stream wrapper."""

    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


@dataclass
class URL:
    """Small helper mirroring the bits of httpx.URL that Starlette needs."""

    raw: str

    def __post_init__(self) -> None:
        parsed = urlsplit(self.raw)
        scheme = parsed.scheme or "http"
        netloc = parsed.netloc or ""
        path = parsed.path or "/"
        query = parsed.query or ""

        self.scheme: str = scheme
        self.netloc: bytes = netloc.encode("ascii")
        self.path: str = path
        self.query: bytes = query.encode("ascii")
        raw_path = path
        if query:
            raw_path = f"{raw_path}?{query}"
        self.raw_path: bytes = raw_path.encode("ascii", "ignore")

    def join(self, relative: str) -> URL:
        return URL(urljoin(self.raw, relative))

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return self.raw


class Request:
    def __init__(
        self,
        method: str,
        url: URL,
        *,
        headers: Headers | None = None,
        content: bytes | None = None,
    ) -> None:
        self.method = method.upper()
        self.url = url
        self.headers = headers or Headers()
        self._body = content or b""

    def read(self) -> bytes:
        return self._body


class Response:
    def __init__(
        self,
        status_code: int,
        headers: Iterable[tuple[str, str]] | None = None,
        stream: ByteStream | None = None,
        request: Request | None = None,
    ) -> None:
        self.status_code = status_code
        self._headers = Headers(headers or [])
        self._stream = stream or ByteStream(b"")
        self.request = request

    @property
    def headers(self) -> dict[str, str]:
        return {key: value for key, value in self._headers.multi_items()}

    @property
    def content(self) -> bytes:
        return self._stream.read()

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.text)


class BaseTransport:
    """Interface mirrored from httpx.BaseTransport."""

    def handle_request(self, request: Request) -> Response:  # pragma: no cover - interface only
        raise NotImplementedError


class Client:
    def __init__(
        self,
        *,
        app: Any,
        base_url: str,
        headers: Mapping[str, str] | None = None,
        transport: BaseTransport,
        follow_redirects: bool = True,
        cookies: CookieTypes | None = None,
    ) -> None:
        self.app = app
        self.base_url = URL(base_url)
        self._transport = transport
        self._default_headers = Headers((headers or {}).items())
        self._follow_redirects = follow_redirects
        self.cookies = cookies

    # Context manager helpers -------------------------------------------------
    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        pass

    # Request helpers ---------------------------------------------------------
    def _merge_url(self, url: URLTypes) -> URL:
        if isinstance(url, URL):
            return url
        if isinstance(url, bytes):
            url = url.decode()
        if not isinstance(url, str):
            url = str(url)
        if url.startswith("http://") or url.startswith("https://"):
            return URL(url)
        return self.base_url.join(url)

    def _build_headers(self, headers: HeaderTypes | None) -> Headers:
        merged = self._default_headers.copy()
        if headers is None:
            return merged
        if isinstance(headers, Mapping):
            items = headers.items()
        else:
            items = headers  # type: ignore[assignment]
        merged.extend((str(key), str(value)) for key, value in items)
        return merged

    def _encode_params(self, url: URL, params: QueryParamTypes | None) -> URL:
        if not params:
            return url
        if isinstance(params, Mapping):
            query = urlencode(list(params.items()), doseq=True)
        elif isinstance(params, list | tuple):
            query = urlencode(params, doseq=True)
        else:  # pragma: no cover - defensive
            query = urlencode(params)  # type: ignore[arg-type]
        base = url.raw.split("?")[0]
        return URL(f"{base}?{query}")

    def _encode_body(
        self,
        content: RequestContent | None,
        data: Any = None,
        json_data: Any = None,
    ) -> bytes:
        if content is not None:
            if isinstance(content, bytes):
                return content
            if isinstance(content, str):
                return content.encode("utf-8")
            if hasattr(content, "read"):
                return content.read()
            return bytes(content)
        if json_data is not None:
            return json.dumps(json_data).encode("utf-8")
        if data is None:
            return b""
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")
        if isinstance(data, Mapping):
            return urlencode(list(data.items()), doseq=True).encode("utf-8")
        return bytes(data)

    def request(
        self,
        method: str,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: Any = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | None = None,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: dict[str, Any] | None = None,
    ) -> Response:
        del files, cookies, auth, follow_redirects, timeout, extensions  # Unused
        prepared_url = self._merge_url(url)
        prepared_url = self._encode_params(prepared_url, params)
        body = self._encode_body(content, data, json)
        request_headers = self._build_headers(headers)
        request = Request(method, prepared_url, headers=request_headers, content=body)
        response = self._transport.handle_request(request)
        return response

    # Convenience HTTP verbs --------------------------------------------------
    def get(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("GET", url, **kwargs)

    def options(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("OPTIONS", url, **kwargs)

    def head(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("HEAD", url, **kwargs)

    def post(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: URLTypes, **kwargs: Any) -> Response:
        return self.request("DELETE", url, **kwargs)


__all__ = [
    "AuthTypes",
    "BaseTransport",
    "ByteStream",
    "Client",
    "CookieTypes",
    "Headers",
    "QueryParamTypes",
    "Request",
    "RequestContent",
    "RequestFiles",
    "Response",
    "TimeoutTypes",
    "URL",
    "URLTypes",
    "USE_CLIENT_DEFAULT",
]
