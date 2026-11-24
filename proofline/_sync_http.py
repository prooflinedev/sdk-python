"""Bound name resolution, blocking socket reads, writes and TLS to the request deadline.

Operating-system name resolution cannot be interrupted, so it runs on a daemon
thread and the request stops waiting for it at the deadline. An abandoned lookup
finishes on its own thread and its result is discarded.
"""

from __future__ import annotations

import ipaddress
import socket
import ssl
import threading
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from time import monotonic
from typing import Any

import httpcore2
import httpx2

IO_DEADLINE: ContextVar[float | None] = ContextVar("proofline_io_deadline", default=None)
CALLER_DEADLINE: ContextVar[float | None] = ContextVar(
    "proofline_caller_deadline",
    default=None,
)

_CORE_TIMEOUT_MAP: tuple[
    tuple[type[httpcore2.TimeoutException], type[httpx2.TimeoutException]], ...
] = (
    (httpcore2.ConnectTimeout, httpx2.ConnectTimeout),
    (httpcore2.ReadTimeout, httpx2.ReadTimeout),
    (httpcore2.WriteTimeout, httpx2.WriteTimeout),
    (httpcore2.PoolTimeout, httpx2.PoolTimeout),
)


def bounded_timeout(
    timeout: float | None,
    timeout_exc: type[httpcore2.TimeoutException] = httpcore2.ReadTimeout,
) -> float | None:
    deadline = IO_DEADLINE.get()
    if deadline is None:
        return timeout

    remaining = deadline - monotonic()
    if remaining <= 0:
        raise timeout_exc("The request deadline expired.")

    return remaining if timeout is None else min(timeout, remaining)


class Lookup:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._finished = threading.Event()
        self._addresses: list[str] = []

    def run(self) -> None:
        try:
            for family, *_, sockaddr in socket.getaddrinfo(
                self._host, self._port, type=socket.SOCK_STREAM
            ):
                address = str(sockaddr[0])
                if family == socket.AF_INET6 and len(sockaddr) == 4 and sockaddr[3]:
                    address = f"{address}%{sockaddr[3]}"
                if address not in self._addresses:
                    self._addresses.append(address)
        except (OSError, UnicodeError):
            self._addresses = []
        finally:
            self._finished.set()

    def addresses(self, timeout: float | None) -> list[str]:
        if not self._finished.wait(timeout):
            raise httpcore2.ConnectTimeout("The host name lookup did not finish in time.")
        if not self._addresses:
            raise httpcore2.ConnectError("The host name did not resolve.")
        return self._addresses


def resolve(host: str, port: int, timeout: float | None) -> list[str]:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        lookup = Lookup(host, port)
        threading.Thread(
            target=lookup.run,
            name="proofline-dns",
            daemon=True,
        ).start()
        return lookup.addresses(timeout)

    return [host]


class NetworkStream(httpcore2.NetworkStream):
    def __init__(self, inner: httpcore2.NetworkStream) -> None:
        self._inner = inner

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        deadline = IO_DEADLINE.get()
        caller = CALLER_DEADLINE.get()

        remaining = None if deadline is None else deadline - monotonic()

        caller_bounded = (
            caller is not None
            and deadline is not None
            and caller <= deadline
            and remaining is not None
            and (timeout is None or remaining <= timeout)
        )

        try:
            return self._inner.read(
                max_bytes,
                bounded_timeout(timeout, httpcore2.ReadTimeout),
            )
        except httpcore2.ReadTimeout as error:
            setattr(error, "_deadline_bounded", caller_bounded)
            raise

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self._inner.write(
            buffer,
            bounded_timeout(timeout, httpcore2.WriteTimeout),
        )

    def close(self) -> None:
        self._inner.close()

    def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore2.NetworkStream:
        return NetworkStream(
            self._inner.start_tls(
                ssl_context,
                server_hostname,
                bounded_timeout(timeout, httpcore2.ConnectTimeout),
            )
        )

    def get_extra_info(self, info: str) -> Any:
        return self._inner.get_extra_info(info)


class NetworkBackend(httpcore2.SyncBackend):
    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[Any] | None = None,
    ) -> httpcore2.NetworkStream:
        failure: httpcore2.ConnectError | httpcore2.ConnectTimeout | None = None
        connect_timeout = bounded_timeout(timeout, httpcore2.ConnectTimeout)

        for address in resolve(host, port, connect_timeout):
            # Calculate this outside the try block so an expired shared
            # deadline escapes instead of being treated as a retryable
            # connection failure for the next address.
            address_timeout = bounded_timeout(timeout, httpcore2.ConnectTimeout)

            try:
                stream = super().connect_tcp(
                    address,
                    port,
                    address_timeout,
                    local_address,
                    socket_options,
                )
            except (httpcore2.ConnectError, httpcore2.ConnectTimeout) as error:
                failure = error
            else:
                return NetworkStream(stream)

        raise failure or httpcore2.ConnectError("The host name did not resolve.")


@contextmanager
def mapped_errors() -> Iterator[None]:
    try:
        yield
    except httpcore2.TimeoutException as error:
        mapped_cls = next(
            (httpx_cls for core_cls, httpx_cls in _CORE_TIMEOUT_MAP if isinstance(error, core_cls)),
            httpx2.TimeoutException,
        )

        mapped_error = mapped_cls("The request deadline expired.")
        setattr(
            mapped_error,
            "_deadline_bounded",
            getattr(error, "_deadline_bounded", False),
        )
        raise mapped_error from None

    except (httpcore2.NetworkError, httpcore2.ProtocolError):
        raise httpx2.TransportError("The HTTP transport failed.") from None


class ResponseStream(httpx2.SyncByteStream):
    def __init__(self, response: httpcore2.Response) -> None:
        self._response = response

    def __iter__(self) -> Iterator[bytes]:
        with mapped_errors():
            yield from self._response.iter_stream()

    def close(self) -> None:
        with mapped_errors():
            self._response.close()


class Transport(httpx2.BaseTransport):
    def __init__(self) -> None:
        self._pool = httpcore2.ConnectionPool(
            ssl_context=httpcore2.default_ssl_context(),
            network_backend=NetworkBackend(),
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=5,
        )

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        if not isinstance(request.stream, httpx2.SyncByteStream):
            raise httpx2.TransportError("The synchronous request has an invalid stream.")

        core_request = httpcore2.Request(
            method=request.method,
            url=httpcore2.URL(
                scheme=request.url.raw_scheme,
                host=request.url.raw_host,
                port=request.url.port,
                target=request.url.raw_path,
            ),
            headers=request.headers.raw,
            content=request.stream,
            extensions=request.extensions,
        )

        with mapped_errors():
            response = self._pool.handle_request(core_request)

        return httpx2.Response(
            response.status,
            headers=response.headers,
            stream=ResponseStream(response),
            extensions=response.extensions,
        )

    def close(self) -> None:
        self._pool.close()
