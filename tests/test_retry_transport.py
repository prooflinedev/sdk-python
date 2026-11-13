"""Retry policy against a mocked inner httpx transport, with no network or real sleeps."""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest
from pydantic import SecretStr

from proofline import AsyncProoflineClient, ProoflineClient, ProoflineError, _sync_http, _transport

from .fixtures import FINDING, ORG, TOKEN, finding

Responder = Callable[[httpx.Request, int], httpx.Response]


def unavailable(request: httpx.Request, index: int) -> httpx.Response:
    return httpx.Response(503, json={"detail": "Unavailable."}, request=request)


def recover_after(failures: int) -> Responder:
    def respond(request: httpx.Request, index: int) -> httpx.Response:
        if index < failures:
            return unavailable(request, index)
        return httpx.Response(200, json=finding(), request=request)

    return respond


class MockTransport:
    """Stands in for the inner httpx transport each client's RetryTransport wraps."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, respond: Responder) -> None:
        self.requests: list[httpx.Request] = []
        self.delays: list[float] = []
        self._respond = respond

        def handle(_self: object, request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return self._respond(request, len(self.requests) - 1)

        async def handle_async(_self: object, request: httpx.Request) -> httpx.Response:
            return handle(_self, request)

        async def async_sleep(delay: float) -> None:
            self.delays.append(delay)

        monkeypatch.setattr(_sync_http.Transport, "handle_request", handle)
        monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", handle_async)
        monkeypatch.setattr(_transport, "sleep", self.delays.append)
        monkeypatch.setattr(_transport, "async_sleep", async_sleep)


@pytest.mark.parametrize("max_retries", [0, 1, 3, 5])
def test_sync_client_retries_503_up_to_max_retries(
    monkeypatch: pytest.MonkeyPatch, max_retries: int
) -> None:
    transport = MockTransport(monkeypatch, unavailable)
    with ProoflineClient(SecretStr(TOKEN), max_retries=max_retries) as client:
        with pytest.raises(ProoflineError) as raised:
            client.get_finding(ORG, FINDING)
    assert raised.value.status == 503
    assert len(transport.requests) == max_retries + 1
    assert all(request.method == "GET" for request in transport.requests)
    assert transport.delays == [1, 2, 4, 8, 16][:max_retries]


@pytest.mark.asyncio
@pytest.mark.parametrize("max_retries", [0, 1, 3, 5])
async def test_async_client_retries_503_up_to_max_retries(
    monkeypatch: pytest.MonkeyPatch, max_retries: int
) -> None:
    transport = MockTransport(monkeypatch, unavailable)
    async with AsyncProoflineClient(SecretStr(TOKEN), max_retries=max_retries) as client:
        with pytest.raises(ProoflineError) as raised:
            await client.get_finding(ORG, FINDING)
    assert raised.value.status == 503
    assert len(transport.requests) == max_retries + 1
    assert transport.delays == [1, 2, 4, 8, 16][:max_retries]


def test_sync_client_succeeds_when_503_clears_within_max_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = MockTransport(monkeypatch, recover_after(2))
    with ProoflineClient(SecretStr(TOKEN), max_retries=2) as client:
        assert client.get_finding(ORG, FINDING).id == FINDING
    assert len(transport.requests) == 3
    assert transport.delays == [1, 2]


@pytest.mark.asyncio
async def test_async_client_succeeds_when_503_clears_within_max_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = MockTransport(monkeypatch, recover_after(2))
    async with AsyncProoflineClient(SecretStr(TOKEN), max_retries=2) as client:
        assert (await client.get_finding(ORG, FINDING)).id == FINDING
    assert len(transport.requests) == 3
    assert transport.delays == [1, 2]


@pytest.mark.asyncio
async def test_503_outlasting_max_retries_is_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = MockTransport(monkeypatch, recover_after(2))
    async with AsyncProoflineClient(SecretStr(TOKEN), max_retries=1) as client:
        with pytest.raises(ProoflineError) as raised:
            await client.get_finding(ORG, FINDING)
    assert raised.value.status == 503
    assert len(transport.requests) == 2
