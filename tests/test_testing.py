from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

import pytest

from proofline import (
    AsyncProoflineClient,
    ProoflineClient,
    ProoflineError,
    RepositoryNames,
    _sync_http,
    _transport,
)
from proofline import client as client_module
from proofline.testing import (
    DEFAULT_ORGANIZATION_ID,
    FakeProofline,
    FakeRequest,
    FakeResponse,
    fake_finding,
)

Client = ProoflineClient | AsyncProoflineClient
MODES = pytest.mark.parametrize("mode", ["sync", "async"])
ORG = DEFAULT_ORGANIZATION_ID


@asynccontextmanager
async def session(
    mode: str, fake: FakeProofline, token: str | None = None
) -> AsyncIterator[Client]:
    if mode == "sync":
        with ProoflineClient(token or fake.token, base_url=fake.url) as client:
            yield client
    else:
        async with AsyncProoflineClient(token or fake.token, base_url=fake.url) as async_client:
            yield async_client


async def call(client: Client, name: str, *args: Any, **kwargs: Any) -> Any:
    result = getattr(client, name)(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def collect(client: Client, **kwargs: Any) -> list[Any]:
    iterator = client.iter_reviews(ORG, **kwargs)
    if hasattr(iterator, "__aiter__"):
        return [item async for item in iterator]
    return list(iterator)


class Clock:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.now = 100.0
        self.delays: list[float] = []
        monkeypatch.setattr(client_module, "monotonic", lambda: self.now)
        monkeypatch.setattr(_transport, "monotonic", lambda: self.now)
        monkeypatch.setattr(_sync_http, "monotonic", lambda: self.now)
        monkeypatch.setattr(client_module, "sleep", self.sleep)
        monkeypatch.setattr(_transport, "sleep", self.sleep)
        monkeypatch.setattr(client_module, "async_sleep", self.async_sleep)
        monkeypatch.setattr(_transport, "async_sleep", self.async_sleep)

    def sleep(self, delay: float) -> None:
        self.delays.append(delay)
        self.now += delay

    async def async_sleep(self, delay: float) -> None:
        self.sleep(delay)
        await asyncio.sleep(0)


def review_reads(fake: FakeProofline, review_id: UUID) -> list[FakeRequest]:
    path = f"/api/v1/organizations/{ORG}/reviews/{review_id}"
    return [request for request in fake.requests if request.path == path]


@MODES
async def test_wait_for_review_follows_staged_states(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with FakeProofline() as fake:
        review_id = fake.add_review(
            pull_request=7,
            states=["PENDING", "RUNNING", "COMPLETED"],
            findings=[fake_finding(claim="First."), fake_finding(severity="WARNING")],
        )
        async with session(mode, fake) as client:
            outcome = await call(client, "wait_for_review", ORG, review_id)

        assert outcome.status == "COMPLETED"
        assert outcome.review is not None
        assert [finding.claim for finding in outcome.review.assessments[0].findings] == [
            "First.",
            "A fake finding.",
        ]
        assert len(review_reads(fake, review_id)) == 3
        assert clock.delays == [5.0, 10.0]


@MODES
@pytest.mark.parametrize(
    ("state", "expected"),
    [("FAILED", "FAILED"), ("STOPPED", "STOPPED"), ("INCOMPLETE", "INCOMPLETE")],
)
async def test_terminal_states_reach_the_matching_outcome(
    mode: str, state: str, expected: str
) -> None:
    with FakeProofline() as fake:
        review_id = fake.add_review(states=[state])
        async with session(mode, fake) as client:
            outcome = await call(client, "wait_for_review", ORG, review_id)

    assert outcome.status == expected


@MODES
async def test_wait_for_review_times_out_on_a_review_that_keeps_running(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    with FakeProofline() as fake:
        review_id = fake.add_review(states=["RUNNING"])
        async with session(mode, fake) as client:
            outcome = await call(client, "wait_for_review", ORG, review_id, timeout=30)

    assert outcome.status == "TIMED_OUT"


@MODES
async def test_head_commit_pin_is_served_to_the_client(mode: str) -> None:
    with FakeProofline() as fake:
        review_id = fake.add_review(head_commit_sha="a" * 40)
        async with session(mode, fake) as client:
            held = await call(client, "wait_for_review", ORG, review_id, head_commit_sha="a" * 40)
            other = await call(client, "wait_for_review", ORG, review_id, head_commit_sha="b" * 40)

    assert held.status == "COMPLETED"
    assert other.status == "INCOMPLETE"
    assert other.reason == "The review is pinned to another head commit."


@MODES
async def test_request_review_claims_registered_reviews_then_starts_new_runs(mode: str) -> None:
    with FakeProofline() as fake:
        first = fake.add_review(pull_request=7)
        second = fake.add_review(pull_request=7, states=["RUNNING", "FAILED"])
        async with session(mode, fake) as client:
            runs = [
                await call(client, "request_review", ORG, fake.repository_id, 7) for _ in range(3)
            ]
            created = await call(client, "get_review", ORG, runs[2].review_id)

    assert [run.review_id for run in runs[:2]] == [first, second]
    assert [run.run_number for run in runs] == [1, 2, 3]
    assert not any(run.existing for run in runs)
    assert created.status == "COMPLETED"
    assert created.pull_request_number == 7


@MODES
async def test_iter_reviews_follows_fake_cursor_pages(mode: str) -> None:
    with FakeProofline() as fake:
        ids = {fake.add_review(pull_request=number) for number in range(1, 6)}
        async with session(mode, fake) as client:
            items = await collect(client, page_size=2)

        listing = [request for request in fake.requests if request.path.endswith("/reviews")]
        assert {item.id for item in items} == ids
        assert len(listing) == 3
        assert [request.query.get("cursor") for request in listing] == [
            None,
            ["fake:2"],
            ["fake:4"],
        ]


@MODES
async def test_list_filters_by_status(mode: str) -> None:
    with FakeProofline() as fake:
        failed = fake.add_review(states=["FAILED"])
        fake.add_review(states=["COMPLETED"])
        async with session(mode, fake) as client:
            page = await call(client, "list_reviews", ORG, status="FAILED")

    assert [item.id for item in page.items] == [failed]


@MODES
async def test_pull_request_history_and_run_lookup(mode: str) -> None:
    with FakeProofline(repository="acme/payments") as fake:
        first = fake.add_review(pull_request=12)
        second = fake.add_review(pull_request=12)
        fake.add_review(pull_request=13)
        async with session(mode, fake) as client:
            history = await call(client, "list_pull_request_reviews", ORG, "acme/payments", 12)
            run = await call(client, "get_pull_request_review", ORG, "acme/payments", 12, 2)
            with pytest.raises(ProoflineError) as missing:
                await call(client, "get_pull_request_review", ORG, "acme/payments", 12, 9)

        assert {item.id for item in history.items} == {first, second}
        assert run.id == second
        assert run.repository_full_name == "acme/payments"
        assert missing.value.status == 404
        assert any("acme%2Fpayments" in request.path for request in fake.requests)


@MODES
async def test_stop_then_rerun(mode: str) -> None:
    with FakeProofline() as fake:
        review_id = fake.add_review(pull_request=3, states=["RUNNING"])
        async with session(mode, fake) as client:
            with pytest.raises(ProoflineError) as unfinished:
                await call(client, "rerun_review", ORG, review_id)
            stopped = await call(client, "stop_review", ORG, review_id)
            with pytest.raises(ProoflineError) as again:
                await call(client, "stop_review", ORG, review_id)
            outcome = await call(client, "wait_for_review", ORG, review_id)
            rerun = await call(client, "rerun_review", ORG, review_id)
            detail = await call(client, "get_review", ORG, rerun.review_id)

    assert unfinished.value.status == 409
    assert stopped.status == "STOPPED"
    assert again.value.status == 409
    assert outcome.status == "STOPPED"
    assert rerun.run_number == 2
    assert rerun.pull_request_number == 3
    assert detail.trigger_origin == "RERUN"
    assert detail.status == "RUNNING"


@MODES
async def test_queued_problem_reaches_the_client_once(mode: str) -> None:
    with FakeProofline() as fake:
        review_id = fake.add_review()
        fake.fail_next(404, path=f"/reviews/{review_id}", detail="Gone for this test.")
        async with session(mode, fake) as client:
            with pytest.raises(ProoflineError) as error:
                await call(client, "get_review", ORG, review_id)
            detail = await call(client, "get_review", ORG, review_id)

    assert error.value.status == 404
    assert error.value.title == "Not Found"
    assert error.value.detail == "Gone for this test."
    assert detail.id == review_id


@MODES
async def test_rate_limit_goes_through_the_client_retry(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with FakeProofline() as fake:
        review_id = fake.add_review()
        fake.fail_next(429, method="GET", retry_after="3", times=2)
        async with session(mode, fake) as client:
            detail = await call(client, "get_review", ORG, review_id)

    assert detail.id == review_id
    assert clock.delays == [3.0, 3.0]
    assert len(review_reads(fake, review_id)) == 3


@MODES
async def test_a_post_is_not_retried_after_a_rate_limit(mode: str) -> None:
    with FakeProofline() as fake:
        fake.fail_next(429, method="POST", retry_after="1")
        async with session(mode, fake) as client:
            with pytest.raises(ProoflineError) as error:
                await call(client, "request_review", ORG, fake.repository_id, 1)

    assert error.value.status == 429
    assert len(fake.requests) == 1


@MODES
async def test_wrong_token_and_unknown_resources_are_refused(mode: str) -> None:
    other = UUID("00000000-0000-4000-8000-0000000000aa")
    with FakeProofline() as fake:
        review_id = fake.add_review()
        async with session(mode, fake, token="pln_test_someone_else") as stranger:
            with pytest.raises(ProoflineError) as unauthorized:
                await call(stranger, "get_review", ORG, review_id)
        async with session(mode, fake) as client:
            with pytest.raises(ProoflineError) as organization:
                await call(client, "get_review", other, review_id)
            with pytest.raises(ProoflineError) as review:
                await call(client, "get_review", ORG, other)
            with pytest.raises(ProoflineError) as repository:
                await call(client, "request_review", ORG, other, 1)

    assert unauthorized.value.status == 401
    assert organization.value.status == 404
    assert review.value.status == 404
    assert repository.value.status == 404
    assert fake.requests[0].headers["authorization"] == "Bearer pln_test_someone_else"


@MODES
async def test_route_serves_an_endpoint_the_fake_does_not_model(mode: str) -> None:
    seen: list[FakeRequest] = []

    def repositories(request: FakeRequest) -> FakeResponse:
        seen.append(request)
        return FakeResponse(200, {"repositories": []})

    with FakeProofline() as fake:
        fake.route("GET", "/repository-names", repositories)
        async with session(mode, fake) as client:
            names = await call(client, "list_repositories", ORG)

    assert isinstance(names, RepositoryNames)
    assert names.repositories == []
    assert [request.method for request in seen] == ["GET"]


async def test_a_failing_route_answers_with_a_server_problem() -> None:
    def broken(request: FakeRequest) -> FakeResponse:
        raise RuntimeError("route bug")

    with FakeProofline() as fake:
        fake.route("GET", "/repository-names", broken)
        with ProoflineClient(fake.token, base_url=fake.url) as client:
            with pytest.raises(ProoflineError) as error:
                client.list_repositories(ORG)

    assert error.value.status == 500
    assert "route bug" in error.value.detail


def test_request_log_keeps_bodies_and_json() -> None:
    with FakeProofline() as fake:
        with ProoflineClient(fake.token, base_url=fake.url) as client:
            client.request_review(ORG, fake.repository_id, 4)

    request = fake.requests[0]
    assert request.method == "POST"
    assert request.path.endswith(f"/repositories/{fake.repository_id}/pull-requests/4/review")
    assert request.json() in (None, {})


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"states": []}, "at least one review state"),
        ({"states": "COMPLETED"}, "at least one review state"),
        ({"states": ["DONE"]}, "Unknown review states"),
        ({"pull_request": 0}, "positive integer"),
        ({"pull_request": True}, "positive integer"),
        ({"head_commit_sha": "abc"}, "full 40 or 64"),
        ({"findings": [{"id": "not-a-finding"}]}, "public contract"),
    ],
)
def test_add_review_rejects_scenarios_the_contract_cannot_carry(
    arguments: dict[str, Any], message: str
) -> None:
    with FakeProofline() as fake:
        with pytest.raises(ValueError, match=message):
            fake.add_review(**arguments)


def test_add_review_rejects_a_duplicate_id_and_bad_setup() -> None:
    with FakeProofline() as fake:
        review_id = fake.add_review()
        with pytest.raises(ValueError, match="already exists"):
            fake.add_review(review_id=review_id)
        with pytest.raises(ValueError, match="4xx or 5xx"):
            fake.fail_next(302)
        with pytest.raises(ValueError, match="positive integer"):
            fake.fail_next(500, times=0)
    with pytest.raises(ValueError, match="owner/name"):
        FakeProofline(repository="acme")
    with pytest.raises(ValueError, match="without whitespace"):
        FakeProofline(token="has space")


def test_fake_finding_accepts_contract_fields_and_rejects_others() -> None:
    finding = fake_finding(severity="WARNING", symbols=["handler"])

    assert finding["severity"] == "WARNING"
    assert finding["symbols"] == ["handler"]
    with pytest.raises(ValueError, match="public contract"):
        fake_finding(rule_refs=[{"key": "no-sync-io"}])


@MODES
async def test_bad_paging_and_unknown_pull_request_repositories_are_refused(mode: str) -> None:
    with FakeProofline() as fake:
        fake.add_review(pull_request=5)
        async with session(mode, fake) as client:
            with pytest.raises(ProoflineError) as limit:
                await call(client, "list_reviews", ORG, limit=500)
            with pytest.raises(ProoflineError) as cursor:
                await call(client, "list_reviews", ORG, cursor="not-a-fake-cursor")
            with pytest.raises(ProoflineError) as repository:
                await call(client, "list_pull_request_reviews", ORG, "acme/other", 5)
            short_name = await call(client, "list_pull_request_reviews", ORG, "api", 5)

    assert limit.value.status == 400
    assert cursor.value.status == 400
    assert repository.value.status == 404
    assert len(short_name.items) == 1


def test_unnamed_status_and_closing_twice() -> None:
    fake = FakeProofline()
    fake.start()
    fake.fail_next(499)
    with ProoflineClient(fake.token, base_url=fake.url) as client:
        with pytest.raises(ProoflineError) as error:
            client.list_reviews(ORG)
    fake.close()
    fake.close()

    assert error.value.status == 499
    assert error.value.title == "Error"
