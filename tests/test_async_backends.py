"""The async client runs on every event loop that anyio and httpx2 support.

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
HEAD = "a" * 40


def run(backend: str, scenario: Callable[[], Awaitable[None]]) -> None:
    anyio.run(scenario, backend=backend)


@BACKENDS
@pytest.mark.parametrize("status", [429, 503])
def test_retry_after_waits_on_every_backend(backend: str, status: int) -> None:
    with Server(
        lambda request, index: (
            Reply(status, {"detail": "Unavailable."}, {"Retry-After": "1"})
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
    body = {**review("RUNNING"), "head_commit_sha": HEAD}
    with Server(lambda request, index: Reply(body=body)) as server:

        async def scenario() -> None:
            async with AsyncProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                started = time.monotonic()
                result = await client.wait_for_review(ORG, REVIEW, timeout=1, head_commit_sha=HEAD)
                assert result.status == "TIMED_OUT"
                assert result.review is not None
                assert result.review.id == REVIEW
                assert result.review.head_commit_sha == HEAD
                # The poll interval is clamped to the remaining deadline, so the
                # wait sleeps until the deadline instead of failing or returning early.
                assert time.monotonic() - started >= 0.9

        run(backend, scenario)
        assert len(server.requests) == 1


@BACKENDS
@pytest.mark.parametrize("final_head", [HEAD, "b" * 40])
def test_wait_for_review_keeps_exact_head_after_sleep_on_every_backend(
    backend: str, final_head: str
) -> None:
    responses = [
        {**review("RUNNING"), "head_commit_sha": HEAD},
        {**review(), "head_commit_sha": final_head},
    ]
    with Server(lambda request, index: Reply(body=responses[min(index, 1)])) as server:

        async def scenario() -> None:
            async with AsyncProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                result = await client.wait_for_review(ORG, REVIEW, timeout=15, head_commit_sha=HEAD)
                assert result.review is not None
                assert result.review.head_commit_sha == final_head
                if final_head == HEAD:
                    assert result.status == "COMPLETED"
                    assert result.gaps == ()
                else:
                    assert result.status == "INCOMPLETE"
                    assert result.gaps[-1].reason_codes == ("HEAD_COMMIT_MISMATCH",)

        run(backend, scenario)
        assert len(server.requests) == 2


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
