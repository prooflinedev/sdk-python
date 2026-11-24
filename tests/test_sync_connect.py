"""The sync transport races resolved addresses so one silent address cannot spend the deadline."""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Callable, Iterator
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


def until(condition: Callable[[], bool], what: str) -> None:
    """Poll a condition a worker thread sets; fail instead of hanging if it never holds."""
    deadline = time.monotonic() + 5
    while not condition():
        if time.monotonic() > deadline:
            pytest.fail(f"Timed out waiting for {what}.")
        time.sleep(0.001)


@dataclass
class Network:
    hosts: dict[str, list[str]] = field(default_factory=dict)
    # Every address the backend tried, in order, with its start time and connect timeout.
    attempts: list[tuple[str, float, float | None]] = field(default_factory=list)
    silence: threading.Event = field(default_factory=threading.Event)

    @property
    def tried(self) -> list[str]:
        return [address for address, _, _ in self.attempts]

    @property
    def timeouts(self) -> list[float | None]:
        return [timeout for _, _, timeout in self.attempts]


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
        state.attempts.append((host, time.monotonic(), timeout))
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
    starts = [at for _, at, _ in network.attempts]
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
    # The second attempt starts one delay later and gets only what is left of the budget.
    first, second = network.timeouts
    assert first is not None and second is not None
    assert first <= 0.6
    assert second <= 0.6 - _sync_http.ATTEMPT_DELAY * 0.8


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
    # Each attempt is bounded by the 0.4 second wait, not the 30 second HTTP timeout.
    first, second = network.timeouts
    assert first is not None and second is not None
    assert first <= 0.4
    assert second <= 0.4 - _sync_http.ATTEMPT_DELAY * 0.8


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


class Stream(httpcore2.MockStream):
    def __init__(self) -> None:
        super().__init__([])
        self.closed = threading.Event()

    def close(self) -> None:
        self.closed.set()


def test_a_stream_that_connects_after_the_race_settles_is_closed() -> None:
    release = threading.Event()
    late = Stream()

    def connect_late() -> httpcore2.NetworkStream:
        release.wait(5)
        return late

    race = _sync_http.Race()
    race.start(connect_late)
    assert race.settle() is None
    release.set()
    assert late.closed.wait(5)
    assert race.winner is None


def test_a_losing_stream_is_closed_and_the_winner_kept() -> None:
    release = threading.Event()
    winner, loser = Stream(), Stream()

    def connect_loser() -> httpcore2.NetworkStream:
        release.wait(5)
        return loser

    race = _sync_http.Race()
    race.start(connect_loser)
    race.start(lambda: winner)
    race.wait(5)
    assert race.settle() is winner
    release.set()
    assert loser.closed.wait(5)
    assert not winner.closed.is_set()


def test_a_failure_while_an_attempt_starts_still_starts_the_next(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Four silent addresses. The first fails just after the wait before the third attempt
    # times out, so that failure has started nothing yet: the fourth attempt starts at once.
    first_fails = threading.Event()
    silence = threading.Event()
    starts: dict[str, float] = {}
    original_wait = _sync_http.Race.wait
    calls = 0

    def connect_tcp(self: Any, host: str, port: int, timeout: float | None, *args: Any) -> Any:
        starts[host] = time.monotonic()
        if host == "192.0.2.1":
            first_fails.wait(5)
            raise httpcore2.ConnectError("Connection reset")
        silence.wait(timeout)
        raise httpcore2.ConnectTimeout("timed out")

    def wait(race: _sync_http.Race, timeout: float | None, **kwargs: Any) -> int:
        nonlocal calls
        seen = original_wait(race, timeout, **kwargs)
        calls += 1
        if calls == 2:
            failures = race.failures
            first_fails.set()
            until(lambda: race.failures > failures, "the first attempt to fail")
        return seen

    addresses = ["192.0.2.1", "192.0.2.2", "192.0.2.3", "192.0.2.4"]
    monkeypatch.setattr(_sync_http, "resolve", lambda *_: addresses)
    monkeypatch.setattr(httpcore2.SyncBackend, "connect_tcp", connect_tcp)
    monkeypatch.setattr(_sync_http.Race, "wait", wait)
    try:
        with pytest.raises(httpcore2.ConnectTimeout):
            _sync_http.NetworkBackend().connect_tcp("dark.proofline.invalid", 443, 1.2)
    finally:
        silence.set()
    assert list(starts) == addresses
    assert starts["192.0.2.4"] - starts["192.0.2.3"] < _sync_http.ATTEMPT_DELAY / 2


def test_a_failure_after_the_deadline_still_reports_the_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Both attempts hang until the deadline ends the race; one then fails with a reset.
    # The deadline ended the request, so the caller sees a timeout, not the late reset.
    reset = threading.Event()

    def connect_tcp(self: Any, host: str, port: int, timeout: float | None, *args: Any) -> Any:
        reset.wait(10)
        raise httpcore2.ConnectError("Connection reset")

    settle = _sync_http.Race.settle

    def settle_then_fail(race: _sync_http.Race) -> httpcore2.NetworkStream | None:
        winner = settle(race)
        reset.set()
        until(lambda: not race.running, "the late attempts to fail")
        return winner

    monkeypatch.setattr(_sync_http, "resolve", lambda *_: [SILENT, SILENT_V6])
    monkeypatch.setattr(httpcore2.SyncBackend, "connect_tcp", connect_tcp)
    monkeypatch.setattr(_sync_http.Race, "settle", settle_then_fail)
    with pytest.raises(httpcore2.ConnectTimeout):
        _sync_http.NetworkBackend().connect_tcp("dark.proofline.invalid", 443, 0.4)


def test_a_winner_is_closed_when_starting_the_next_attempt_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The first attempt connects just after the scheduler checked for a winner, and then
    # starting the second attempt's thread fails. The error propagates; the stream is closed.
    release = threading.Event()
    winner = Stream()

    def connect_tcp(self: Any, host: str, port: int, timeout: float | None, *args: Any) -> Any:
        release.wait(5)
        return winner

    original_start = _sync_http.Race.start
    starts = 0

    def start(race: _sync_http.Race, connect: Callable[[], httpcore2.NetworkStream]) -> None:
        nonlocal starts
        starts += 1
        if starts == 2:
            release.set()
            until(lambda: race.winner is not None, "the first attempt to connect")
            raise RuntimeError("can't start new thread")
        original_start(race, connect)

    monkeypatch.setattr(_sync_http, "resolve", lambda *_: [SILENT, SILENT_V6])
    monkeypatch.setattr(httpcore2.SyncBackend, "connect_tcp", connect_tcp)
    monkeypatch.setattr(_sync_http.Race, "start", start)
    with pytest.raises(RuntimeError):
        _sync_http.NetworkBackend().connect_tcp("dual.proofline.invalid", 443, 5)
    assert winner.closed.wait(5)


def test_an_attempt_whose_thread_cannot_start_is_not_counted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(thread: threading.Thread) -> None:
        raise RuntimeError("can't start new thread")

    race = _sync_http.Race()
    monkeypatch.setattr(threading.Thread, "start", refuse)
    with pytest.raises(RuntimeError):
        race.start(Stream)
    assert race.running == 0


def test_the_backend_alternates_address_families(network: Network) -> None:
    # The resolver groups addresses by family; attempts must still alternate between them.
    network.hosts["grouped.proofline.invalid"] = [SILENT_V6, REFUSED_V6, SILENT, REFUSED]
    with httpx2.Client(transport=_sync_http.Transport(), timeout=0.8) as client:
        with pytest.raises(httpx2.TimeoutException):
            client.get("http://grouped.proofline.invalid:443/finding")
    assert network.tried == [SILENT_V6, SILENT, REFUSED_V6, REFUSED]


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
