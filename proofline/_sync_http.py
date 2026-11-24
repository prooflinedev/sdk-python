"""Bound name resolution, blocking socket reads, writes and TLS to the request deadline.

Operating-system name resolution cannot be interrupted, so it runs on a daemon
thread and the request stops waiting for it at the deadline. An abandoned lookup
finishes on its own thread and its result is discarded.

A host name with several addresses races its connection attempts (RFC 8305): each starts
250 ms after the previous one, or at once when it fails, and the first connection wins. An
address that silently drops packets then costs one attempt delay instead of the deadline.
"""

from __future__ import annotations

import ipaddress
import socket
import ssl
import threading
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import partial
from time import monotonic
from typing import Any

import httpcore2
import httpx2

IO_DEADLINE: ContextVar[float | None] = ContextVar("proofline_io_deadline", default=None)


def bounded_timeout(timeout: float | None) -> float | None:
    deadline = IO_DEADLINE.get()
    if deadline is None:
        return timeout
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise httpcore2.ReadTimeout("The request deadline expired.")
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
        threading.Thread(target=lookup.run, name="proofline-dns", daemon=True).start()
        return lookup.addresses(timeout)
    return [host]


class NetworkStream(httpcore2.NetworkStream):
    def __init__(self, inner: httpcore2.NetworkStream) -> None:
        self._inner = inner

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        return self._inner.read(max_bytes, bounded_timeout(timeout))

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self._inner.write(buffer, bounded_timeout(timeout))

    def close(self) -> None:
        self._inner.close()

    def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore2.NetworkStream:
        return NetworkStream(
            self._inner.start_tls(ssl_context, server_hostname, bounded_timeout(timeout))
        )

    def get_extra_info(self, info: str) -> Any:
        return self._inner.get_extra_info(info)


# RFC 8305 recommends 250 ms between connection attempts, as anyio uses for the async client.
ATTEMPT_DELAY = 0.25


def interleaved(addresses: list[str]) -> list[str]:
    """Alternate address families, starting with the resolver's first preference (RFC 8305 §4)."""
    families: dict[bool, list[str]] = {True: [], False: []}
    for address in addresses:
        families[":" in address].append(address)
    first = ":" in addresses[0]
    preferred, other = families[first], families[not first]
    ordered: list[str] = []
    for index in range(max(len(preferred), len(other))):
        ordered.extend(family[index] for family in (preferred, other) if index < len(family))
    return ordered


class Race:
    """Concurrent connection attempts. The first stream wins; later streams are closed."""

    def __init__(self) -> None:
        self._changed = threading.Condition()
        self._running = 0
        self._settled = False
        self.winner: httpcore2.NetworkStream | None = None
        self.failure: Exception | None = None
        self.failures = 0

    def start(self, connect: Callable[[], httpcore2.NetworkStream]) -> None:
        with self._changed:
            self._running += 1
        threading.Thread(
            target=self._attempt, args=(connect,), name="proofline-connect", daemon=True
        ).start()

    def _attempt(self, connect: Callable[[], httpcore2.NetworkStream]) -> None:
        try:
            stream = connect()
        except Exception as error:
            with self._changed:
                self._running -= 1
                self.failure = error
                self.failures += 1
                self._changed.notify_all()
            return
        with self._changed:
            self._running -= 1
            if not self._settled and self.winner is None:
                self.winner = stream
                self._changed.notify_all()
                return
        # The request already has a connection or stopped waiting for one.
        stream.close()

    def wait(self, timeout: float | None, *, failures: int | None = None) -> int:
        """Wait for a winner or for every attempt to fail; or for more than `failures` failures.

        Returns the failure count observed under the lock, so the caller acts on exactly the
        failures this wait saw rather than on ones that arrive after it returns.
        """
        with self._changed:
            self._changed.wait_for(
                lambda: (
                    self.winner is not None
                    or self._running == 0
                    or (failures is not None and self.failures > failures)
                ),
                timeout,
            )
            return self.failures

    def settle(self) -> httpcore2.NetworkStream | None:
        """Stop accepting streams; a stream that connects later is closed by its attempt."""
        with self._changed:
            self._settled = True
            return self.winner

    @property
    def running(self) -> int:
        with self._changed:
            return self._running


class NetworkBackend(httpcore2.SyncBackend):
    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[Any] | None = None,
    ) -> httpcore2.NetworkStream:
        addresses = resolve(host, port, bounded_timeout(timeout))
        if len(addresses) == 1:
            stream = super().connect_tcp(
                addresses[0], port, bounded_timeout(timeout), local_address, socket_options
            )
            return NetworkStream(stream)
        # One address that silently drops packets must not spend the whole request deadline
        # while the next address would answer, so attempts overlap ATTEMPT_DELAY apart.
        budget = bounded_timeout(timeout)
        deadline = None if budget is None else monotonic() + budget
        options = list(socket_options or ())
        connect = super().connect_tcp
        race = Race()
        # Failures that have already started an attempt. Each failure starts at most one,
        # so one that arrives while an attempt is being started still starts the next.
        answered = 0
        # Set only here, so a worker that fails after the deadline cannot change the outcome.
        expired = False
        try:
            for index, address in enumerate(interleaved(addresses)):
                if index:
                    # Start the next attempt after the delay, or as soon as any attempt fails.
                    seen = race.wait(
                        ATTEMPT_DELAY
                        if deadline is None
                        else min(ATTEMPT_DELAY, deadline - monotonic()),
                        failures=answered,
                    )
                    if race.winner is not None:
                        break
                    if deadline is not None and monotonic() >= deadline:
                        expired = True
                        break
                    if seen > answered:
                        answered += 1
                remaining = None if deadline is None else max(0.0, deadline - monotonic())
                race.start(partial(connect, address, port, remaining, local_address, options))
            while not expired and race.winner is None and race.running:
                if deadline is None:
                    race.wait(None)
                    continue
                if (left := deadline - monotonic()) > 0:
                    race.wait(left)
                # Judge the deadline before rereading worker state that may change after it.
                expired = monotonic() >= deadline
        finally:
            winner = race.settle()
        if winner is not None:
            return NetworkStream(winner)
        if expired:
            raise httpcore2.ConnectTimeout("No resolved address connected in time.")
        raise race.failure or httpcore2.ConnectError("The host name did not resolve.")


@contextmanager
def mapped_errors() -> Iterator[None]:
    try:
        yield
    except httpcore2.TimeoutException:
        raise httpx2.ReadTimeout("The request deadline expired.") from None
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
