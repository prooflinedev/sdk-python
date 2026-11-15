"""The async client runs on every event loop that anyio and httpx support.

The transport already bounds I/O with anyio, so a sleep tied to one event loop
breaks the client on the others. These tests drive the paths that sleep or
time out on each backend instead of only under pytest's asyncio loop.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

import anyio
import pytest
from pydantic import SecretStr

from proofline import AsyncProoflineClient, ProoflineError

from .fixtures import FINDING, ORG, REVIEW, TOKEN, finding, review
from .http_server import Reply, Server

BACKENDS = pytest.mark.parametrize("backend", ["asyncio", "trio"])


def run(backend: str, scenario: Callable[[], Awaitable[None]]) -> None:
    anyio.run(scenario, backend=backend)


@BACKENDS
def test_retry_after_waits_on_every_backend(backend: str) -> None:
    with Server(
        lambda request, index: (
            Reply(503, {"detail": "Unavailable."}, {"Retry-After": "1"})
            if index == 0
            else Reply(body=finding())
        )
    ) as server:

        async def scenario() -> None:
            async with AsyncProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                started = time.monotonic()
                result = await client.get_finding(ORG, FINDING)
                assert result.id == FINDING
                assert time.monotonic() - started >= 1

        run(backend, scenario)
        assert len(server.requests) == 2


@BACKENDS
def test_wait_for_review_sleeps_between_polls_on_every_backend(backend: str) -> None:
    with Server(lambda request, index: Reply(body=review("RUNNING"))) as server:

        async def scenario() -> None:
            async with AsyncProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                started = time.monotonic()
                result = await client.wait_for_review(ORG, REVIEW, timeout=1)
                assert result.status == "TIMED_OUT"
                assert result.review is not None
                assert result.review.id == REVIEW
                # The poll interval is clamped to the remaining deadline, so the
                # wait sleeps until the deadline instead of failing or returning early.
                assert time.monotonic() - started >= 0.9

        run(backend, scenario)
        assert len(server.requests) == 1


@BACKENDS
def test_stalled_body_times_out_on_every_backend(backend: str) -> None:
    with Server(lambda request, index: Reply(body=review(), split=8, pause=3)) as server:

        async def scenario() -> None:
            async with AsyncProoflineClient(
                SecretStr(TOKEN), base_url=server.url, timeout=0.5
            ) as client:
                with pytest.raises(ProoflineError) as caught:
                    await client.get_review(ORG, REVIEW)
                assert caught.value.type == "urn:proofline:sdk:timeout"

        run(backend, scenario)
