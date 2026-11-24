"""The sync transport races resolved addresses so one silent address cannot spend the deadline."""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpcore2
import httpx2
import pytest

from proofline import ProoflineClient, _sync_http

from .fixtures import FINDING, ORG, REVIEW, TOKEN, finding
from .http_server import Reply, Server

# Documentation addresses (RFC 5737, RFC 3849) stand in for hosts that drop every SYN.
SILENT = "192.0.2.1"
SILENT_V6 = "2001:db8::1"
# These answer every SYN with a reset, as a host with nothing listening does.
REFUSED = "198.51.100.1"
REFUSED_V6 = "2001:db8::2"


@dataclass
class Network:
    hosts: dict[str, list[str]] = field(default_factory=dict)
    # Every address the backend tried, in order, with the time the attempt started.
    attempts: list[tuple[str, float]] = field(default_factory=list)
    silence: threading.Event = field(default_factory=threading.Event)

    @property
    def tried(self) -> list[str]:
        return [address for address, _ in self.attempts]


@pytest.fixture
def network(monkeypatch: pytest.MonkeyPatch) -> Iterator[Network]:
    """Resolve test hosts to chosen addresses. A silent address never answers its SYN.

    Like an unanswered SYN, a silent attempt waits out its whole connect timeout and then
    raises ConnectTimeout; a refused attempt fails at once. Loopback is real TCP.
    """
    state = Network()
    resolve = socket.getaddrinfo
    connect = httpcore2.SyncBackend.connect_tcp

    def getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        if host not in state.hosts:
            return resolve(host, port, *args, **kwargs)
        return [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", (address, port, 0, 0))
            if ":" in address
            else (socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port))
            for address in state.hosts[host]
        ]

    def connect_tcp(self: Any, host: str, port: int, timeout: float | None, *args: Any) -> Any:
        state.attempts.append((host, time.monotonic()))
        if host in (SILENT, SILENT_V6):
            state.silence.wait(timeout)
            raise httpcore2.ConnectTimeout("timed out")
        if host in (REFUSED, REFUSED_V6):
            raise httpcore2.ConnectError("Connection refused")
        return connect(self, host, port, timeout, *args)

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    monkeypatch.setattr(httpcore2.SyncBackend, "connect_tcp", connect_tcp)
    try:
        yield state
    finally:
        # End silent attempts that are still waiting so their threads finish with the test.
        state.silence.set()


def test_a_silent_first_address_falls_back_to_the_next_one(network: Network) -> None:
    network.hosts["dual.proofline.invalid"] = [SILENT_V6, SILENT, "127.0.0.1"]
    with Server(lambda request, index: Reply(body=finding())) as server:
        port = server.url.rsplit(":", 1)[1]
        with httpx2.Client(transport=_sync_http.Transport(), timeout=5) as client:
            started = time.monotonic()
            response = client.get(f"http://dual.proofline.invalid:{port}/finding")
            elapsed = time.monotonic() - started
        assert response.json()["id"] == str(FINDING)
        assert server.requests[0].headers["Host"] == f"dual.proofline.invalid:{port}"
    assert network.tried == [SILENT_V6, SILENT, "127.0.0.1"]
    # Each silent address costs one attempt delay, not the 5 second connect timeout.
    assert elapsed < 2
    starts = [at for _, at in network.attempts]
    assert all(
        later - earlier >= _sync_http.ATTEMPT_DELAY * 0.8
        for earlier, later in zip(starts, starts[1:], strict=False)
    )


def test_the_client_reads_through_a_silent_address(
    network: Network, monkeypatch: pytest.MonkeyPatch
) -> None:
    with Server(lambda request, index: Reply(body=finding())) as server:
        # The origin must be a loopback literal, which resolves to itself; give it a silent
        # address first, as a dual-stack name with broken IPv6 resolves.
        monkeypatch.setattr(_sync_http, "resolve", lambda *_: [SILENT, "127.0.0.1"])
        with ProoflineClient(TOKEN, base_url=server.url, timeout=5) as client:
            started = time.monotonic()
            result = client.get_finding(ORG, FINDING)
            elapsed = time.monotonic() - started
        assert result.id == FINDING
        assert len(server.requests) == 1
    assert network.tried == [SILENT, "127.0.0.1"]
    # Before the race, this read raised urn:proofline:sdk:timeout after 5 seconds.
    assert elapsed < 2


def test_a_refused_address_starts_the_next_attempt_at_once(network: Network) -> None:
    network.hosts["refused.proofline.invalid"] = [REFUSED, "127.0.0.1"]
    with Server(lambda request, index: Reply(body=finding())) as server:
        port = server.url.rsplit(":", 1)[1]
        with httpx2.Client(transport=_sync_http.Transport(), timeout=5) as client:
            started = time.monotonic()
            response = client.get(f"http://refused.proofline.invalid:{port}/finding")
            elapsed = time.monotonic() - started
        assert response.json()["id"] == str(FINDING)
    assert network.tried == [REFUSED, "127.0.0.1"]
    assert elapsed < _sync_http.ATTEMPT_DELAY


def test_every_silent_address_ends_at_the_request_deadline(network: Network) -> None:
    network.hosts["dark.proofline.invalid"] = [SILENT_V6, SILENT]
    with httpx2.Client(transport=_sync_http.Transport(), timeout=0.6) as client:
        started = time.monotonic()
        with pytest.raises(httpx2.TimeoutException):
            client.get("http://dark.proofline.invalid:443/finding")
        elapsed = time.monotonic() - started
    assert 0.5 < elapsed < 1.5
    assert network.tried == [SILENT_V6, SILENT]


def test_the_wait_deadline_still_bounds_the_race(
    network: Network, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_sync_http, "resolve", lambda *_: [SILENT, SILENT_V6])
    with ProoflineClient(TOKEN, base_url="http://127.0.0.1:9", timeout=30) as client:
        started = time.monotonic()
        result = client.wait_for_review(ORG, REVIEW, timeout=0.4)
        elapsed = time.monotonic() - started
    assert result.status == "TIMED_OUT"
    assert network.tried == [SILENT, SILENT_V6]
    assert elapsed < 1.5


def test_every_refused_address_raises_a_connect_error(network: Network) -> None:
    network.hosts["closed.proofline.invalid"] = [REFUSED, REFUSED_V6]
    with httpx2.Client(transport=_sync_http.Transport(), timeout=5) as client:
        started = time.monotonic()
        with pytest.raises(httpx2.TransportError) as raised:
            client.get("http://closed.proofline.invalid:443/finding")
        elapsed = time.monotonic() - started
    assert not isinstance(raised.value, httpx2.TimeoutException)
    assert network.tried == [REFUSED, REFUSED_V6]
    assert elapsed < _sync_http.ATTEMPT_DELAY


def test_a_stream_that_connects_after_the_race_settles_is_closed() -> None:
    release = threading.Event()
    closed = threading.Event()

    class Stream(httpcore2.MockStream):
        def close(self) -> None:
            closed.set()

    def late() -> httpcore2.NetworkStream:
        release.wait(5)
        return Stream([])

    race = _sync_http.Race()
    race.start(late)
    assert race.settle() is None
    release.set()
    assert closed.wait(5)
    assert race.winner is None


@pytest.mark.parametrize(
    ("resolved", "ordered"),
    [
        (
            ["2001:db8::1", "2001:db8::2", "192.0.2.1", "192.0.2.2"],
            ["2001:db8::1", "192.0.2.1", "2001:db8::2", "192.0.2.2"],
        ),
        (["192.0.2.1", "192.0.2.2", "2001:db8::1"], ["192.0.2.1", "2001:db8::1", "192.0.2.2"]),
        (["192.0.2.1", "192.0.2.2"], ["192.0.2.1", "192.0.2.2"]),
        (["fe80::1%41", "fe80::1%42"], ["fe80::1%41", "fe80::1%42"]),
    ],
)
def test_attempts_alternate_address_families(resolved: list[str], ordered: list[str]) -> None:
    assert _sync_http.interleaved(resolved) == ordered
