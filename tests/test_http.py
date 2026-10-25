from __future__ import annotations

import asyncio
import gzip
import inspect
import json
import logging
import socket
import threading
import time
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from pydantic import SecretStr

from proofline import (
    AsyncProoflineClient,
    CommitReviewRequest,
    CommitReviewResponse,
    CustomerAssessmentDetail,
    CustomerFinding,
    CustomerReviewDetail,
    FileReviewRequest,
    FileReviewResponse,
    PatchReviewRequest,
    PatchReviewResponse,
    ProoflineClient,
    ProoflineError,
    RepositoryGuidance,
    RepositoryNames,
    RerunResponse,
    ReviewPage,
    RunNowMode,
    RunNowRequest,
    RunNowResponse,
    StopResponse,
    _sync_http,
    _transport,
    models,
)
from proofline import client as client_module
from proofline._generated.models.finding_fix_prompt_type_0 import FindingFixPromptType0
from proofline._generated.models.finding_fix_prompt_type_1 import FindingFixPromptType1
from proofline._generated.types import UNSET

from .fixtures import (
    ASSESSMENT,
    CODE_ASSESSMENT,
    FINDING,
    ORG,
    PRIVATE,
    REPOSITORY,
    REVIEW,
    TOKEN,
    assessment,
    code_assessment,
    finding,
    page,
    review,
)
from .http_server import Reply, Request, Server

Client = ProoflineClient | AsyncProoflineClient
MODES = pytest.mark.parametrize("mode", ["sync", "async"])


@asynccontextmanager
async def session(mode: str, url: str, **kwargs: Any) -> AsyncIterator[Client]:
    if mode == "sync":
        with ProoflineClient(SecretStr(TOKEN), base_url=url, **kwargs) as client:
            yield client
    else:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url, **kwargs) as async_client:
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


@MODES
@pytest.mark.parametrize(
    "terraform",
    [UNSET, None, {"plan": "TAKEN", "addresses": ["aws_s3_bucket.synthetic"], "omitted": 1}],
)
async def test_all_public_operations_use_generated_models_and_scoped_paths(
    mode: str, terraform: Any
) -> None:
    prefix = f"/api/v1/organizations/{ORG}"
    paths = [
        ("GET", f"{prefix}/reviews", page(), ReviewPage),
        ("GET", f"{prefix}/reviews/pr/repo%2Fname/42", page(), ReviewPage),
        (
            "GET",
            f"{prefix}/reviews/pr/repo%2Fname/42/runs/3",
            review(),
            CustomerReviewDetail,
        ),
        (
            "GET",
            f"{prefix}/reviews/deployments/key%2Fwith%3Fquery",
            review(),
            CustomerReviewDetail,
        ),
        ("GET", f"{prefix}/reviews/{REVIEW}", review(), CustomerReviewDetail),
        (
            "GET",
            f"{prefix}/reviews/{REVIEW}/assessments/{ASSESSMENT}",
            {**assessment(), "review_id": str(REVIEW), "subjects": []},
            CustomerAssessmentDetail,
        ),
        ("GET", f"{prefix}/findings/{FINDING}", finding(), CustomerFinding),
        (
            "GET",
            f"{prefix}/findings/{FINDING}/fix-prompt",
            {"status": "AVAILABLE", "untrusted_text": PRIVATE},
            FindingFixPromptType0,
        ),
        (
            "GET",
            f"{prefix}/findings/{FINDING}/fix-prompt",
            {"status": "UNAVAILABLE", "reason": "The recorded finding cannot supply a prompt."},
            FindingFixPromptType1,
        ),
        (
            "GET",
            f"{prefix}/repositories/{REPOSITORY}/review-guidance",
            {"repository_id": str(REPOSITORY), "additional_prompt": PRIVATE},
            RepositoryGuidance,
        ),
        (
            "GET",
            f"{prefix}/repository-names",
            {"repositories": [{"id": str(REPOSITORY), "full_name": "repo/name"}]},
            RepositoryNames,
        ),
        (
            "POST",
            f"{prefix}/repositories/{REPOSITORY}/pull-requests/42/review",
            {
                "review_id": str(REVIEW),
                "run_number": 1,
                "existing": False,
                "automatic_reviews_paused": False,
            },
            RunNowResponse,
        ),
        (
            "POST",
            f"{prefix}/reviews/{REVIEW}/stop",
            {
                "review_id": str(REVIEW),
                "status": "STOPPED",
                "stopped_by": {"github_user_id": 42, "login": "synthetic-user"},
                "stopped_at": "2026-01-01T00:00:00Z",
            },
            StopResponse,
        ),
        (
            "POST",
            f"{prefix}/reviews/{REVIEW}/rerun",
            {"review_id": str(REVIEW), "public_key": "synthetic-review"},
            RerunResponse,
        ),
    ]

    for _, _, body, response_model in paths:
        if response_model is CustomerReviewDetail:
            assessments = body["assessments"]
        elif response_model is CustomerAssessmentDetail:
            assessments = [body]
        else:
            continue
        for entry in assessments:
            reach = {"complete": True, "entities": [], "gaps": [], "outcome": "READ"}
            if terraform is not UNSET:
                reach["terraform"] = terraform
            entry["declared_reach"] = reach

    def respond(request: Request, index: int) -> Reply:
        method, path, body, _ = paths[index]
        assert request.method == method
        assert urlsplit(request.path).path == path
        return Reply(body=body, headers={"Set-Cookie": "session=must-not-replay; Path=/"})

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            calls = [
                ("list_reviews", (ORG,), {"limit": 7, "repository": REPOSITORY}),
                (
                    "list_pull_request_reviews",
                    (ORG, "repo/name", 42),
                    {"filters": {"repository": REPOSITORY, "search": "text & space"}},
                ),
                ("get_pull_request_review", (ORG, "repo/name", 42, 3), {}),
                ("get_deployment_review", (ORG, "key/with?query"), {}),
                ("get_review", (ORG, REVIEW), {}),
                ("get_assessment", (ORG, REVIEW, ASSESSMENT), {}),
                ("get_finding", (ORG, FINDING), {}),
                ("get_finding_fix_prompt", (ORG, FINDING), {}),
                ("get_finding_fix_prompt", (ORG, FINDING), {}),
                ("get_review_guidance", (ORG, REPOSITORY), {}),
                ("list_repositories", (ORG,), {}),
                ("request_review", (ORG, REPOSITORY, 42), {}),
                ("stop_review", (ORG, REVIEW), {}),
                ("rerun_review", (ORG, REVIEW), {}),
            ]
            for index, (name, args, kwargs) in enumerate(calls):
                result = await call(client, name, *args, **kwargs)
                assert isinstance(result, paths[index][3])
                if isinstance(result, (CustomerReviewDetail, CustomerAssessmentDetail)):
                    entries = (
                        result.assessments if isinstance(result, CustomerReviewDetail) else [result]
                    )
                    for entry in entries:
                        roots = entry.declared_reach.terraform
                        if isinstance(terraform, dict):
                            assert isinstance(roots, models.TerraformRootsView)
                            assert roots.plan is models.TerraformPlanView.TAKEN
                            assert roots.addresses == ["aws_s3_bucket.synthetic"]
                            assert roots.omitted == 1
                        else:
                            assert roots is terraform
                if isinstance(result, CustomerFinding):
                    assert result.rule_refs[0].key == "no-sync-io-in-handlers"
                    revision = result.rule_refs[0].revisions[0]
                    assert (revision.scope, revision.source.value, revision.revision) == (
                        "ORGANIZATION",
                        "CONSOLE",
                        1,
                    )
                elif isinstance(result, StopResponse):
                    assert result.review_id == REVIEW
                    assert result.status == "STOPPED"
                    assert result.stopped_by.github_user_id == 42
                elif isinstance(result, FindingFixPromptType0):
                    assert result.untrusted_text == PRIVATE
                elif isinstance(result, FindingFixPromptType1):
                    assert result.reason == paths[index][2]["reason"]
            assert TOKEN not in repr(client)
            assert TOKEN not in repr(client._api)
        assert len(server.requests) == len(paths)
        assert len({request.peer_port for request in server.requests}) == 1
        for request in server.requests:
            assert request.headers["Authorization"] == f"Bearer {TOKEN}"
            assert request.headers["User-Agent"] == "proofline-python/1.0.0"
            assert request.headers["Accept-Encoding"] == "identity"
            assert "Cookie" not in request.headers
            assert "Content-Type" not in request.headers
            assert request.body == b""
        assert parse_qs(urlsplit(server.requests[0].path).query) == {
            "limit": ["7"],
            "repository": [str(REPOSITORY)],
        }
        assert parse_qs(urlsplit(server.requests[1].path).query) == {
            "repository": [str(REPOSITORY)],
            "search": ["text & space"],
        }

    bodies = [
        RunNowRequest(mode=UNSET),
        RunNowRequest(mode=RunNowMode.EXISTING_OR_NEW),
        RunNowRequest(mode=RunNowMode.FULL),
        None,
    ]
    expected = [{}, {"mode": "EXISTING_OR_NEW"}, {"mode": "FULL"}, None]

    def respond_run_now(request: Request, index: int) -> Reply:
        assert request.method == "POST"
        assert request.path == f"{prefix}/repositories/{REPOSITORY}/pull-requests/42/review"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert "Cookie" not in request.headers
        if expected[index] is None:
            assert request.body == b""
            assert "Content-Type" not in request.headers
        else:
            assert request.headers["Content-Type"] == "application/json"
            assert json.loads(request.body) == expected[index]
        return Reply(
            body={
                "review_id": str(REVIEW),
                "run_number": 7,
                "existing": True,
                "automatic_reviews_paused": True,
            },
            headers={"Set-Cookie": "session=must-not-replay; Path=/"},
        )

    with Server(respond_run_now) as server:
        async with session(mode, server.url) as client:
            for body in bodies:
                kwargs = {} if body is None else {"body": body}
                result = await call(client, "request_review", ORG, REPOSITORY, 42, **kwargs)
                assert isinstance(result, RunNowResponse)
                assert result.review_id == REVIEW
                assert result.run_number == 7
                assert result.existing is True
                assert result.automatic_reviews_paused is True
        assert len(server.requests) == len(bodies)
        assert len({request.peer_port for request in server.requests}) == 1


@MODES
@pytest.mark.parametrize(
    ("operation", "route", "sent", "request_model", "response_model", "extra"),
    [
        (
            "request_patch_review",
            "patch-reviews",
            {"base_commit_sha": "a" * 40, "patch": "diff --git a/x b/x\n"},
            PatchReviewRequest,
            PatchReviewResponse,
            {"patch_digest": "b" * 64, "verify": []},
        ),
        (
            "request_file_review",
            "file-reviews",
            {"commit_sha": "a" * 40, "paths": ["src/main.py"]},
            FileReviewRequest,
            FileReviewResponse,
            {},
        ),
        (
            "request_commit_review",
            "commit-reviews",
            {"base_commit_sha": "a" * 40, "head_commit_sha": "c" * 40},
            CommitReviewRequest,
            CommitReviewResponse,
            {},
        ),
    ],
)
async def test_local_and_commit_reviews_post_their_subject_and_decode_the_review(
    mode: str,
    operation: str,
    route: str,
    sent: dict[str, Any],
    request_model: Any,
    response_model: Any,
    extra: dict[str, Any],
) -> None:
    body = request_model(**sent)

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "POST"
        assert request.path == f"/api/v1/organizations/{ORG}/repositories/{REPOSITORY}/{route}"
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.body) == sent
        return Reply(body={"review_id": str(REVIEW), "existing": True, **extra})

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            result = await call(client, operation, ORG, REPOSITORY, body=body)
            assert isinstance(result, response_model)
            assert (result.review_id, result.existing) == (REVIEW, True)
        assert len(server.requests) == 1


@MODES
@pytest.mark.parametrize("summary_state", ["absent", "null", "published", "withheld"])
async def test_review_reads_preserve_summary_and_exact_code_identity(
    mode: str, summary_state: str
) -> None:
    body = review()
    body.update(head_commit_sha="a" * 40, base_commit_sha="b" * 40)
    if summary_state != "absent":
        body["change_summary"] = (
            None
            if summary_state == "null"
            else {
                "head_sha": "a" * 40,
                "base_sha": "b" * 40,
                "files": [
                    {
                        "path": "src/new.py",
                        "previous_path": "src/old.py",
                        "status": "renamed",
                        "additions": 3,
                        "deletions": 1,
                        "depth": "STANDARD",
                    }
                ],
                "route": "SHORT",
                "prose_outcome": "PUBLISHED",
                "prose": None
                if summary_state == "withheld"
                else {
                    "headline": "[withheld] <script>literal text</script>",
                    "paragraphs": ["Moves the request handler."],
                    "notable_paths": ["src/new.py"],
                },
            }
        )

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "GET"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        return Reply(body=body)

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            for operation, args in [
                ("get_review", (ORG, REVIEW)),
                ("get_pull_request_review", (ORG, "repo/name", 42, 3)),
                ("get_deployment_review", (ORG, "deployment")),
            ]:
                result = await call(client, operation, *args)
                assert result.publication == "WITHHELD"
                assert result.head_commit_sha == "a" * 40
                assert result.base_commit_sha == "b" * 40
                summary = result.change_summary
                if summary_state in {"absent", "null"}:
                    assert summary is (UNSET if summary_state == "absent" else None)
                    continue
                assert isinstance(summary, models.ChangeSummary)
                assert (summary.head_sha, summary.base_sha) == ("a" * 40, "b" * 40)
                assert summary.route is models.SummaryRoute.SHORT
                assert summary.prose_outcome == "PUBLISHED"
                assert len(summary.files) == 1
                file = summary.files[0]
                assert (file.path, file.previous_path, file.status) == (
                    "src/new.py",
                    "src/old.py",
                    "renamed",
                )
                assert (file.additions, file.deletions, file.depth) == (
                    3,
                    1,
                    models.ReviewDepth.STANDARD,
                )
                if summary_state == "withheld":
                    assert summary.prose is None
                else:
                    assert isinstance(summary.prose, models.Prose)
                    assert summary.prose.headline == "[withheld] <script>literal text</script>"
                    assert summary.prose.paragraphs == ["Moves the request handler."]
                    assert summary.prose.notable_paths == ["src/new.py"]


@MODES
@pytest.mark.parametrize("status", [401, 403, 404])
async def test_authority_problems_do_not_retry_or_disclose_secrets(
    mode: str, status: int, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    with Server(
        lambda request, index: Reply(
            status,
            {"type": "urn:proofline:forbidden", "detail": f"{PRIVATE} {TOKEN}"},
        )
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            error = raised.value
            assert error.status == status
            assert error.type == "urn:proofline:forbidden"
            assert PRIVATE in error.detail
            assert "[redacted]" in error.detail
            diagnostic = repr(error) + str(error) + "".join(traceback.format_exception(error))
            assert PRIVATE not in diagnostic
            assert TOKEN not in diagnostic
            assert PRIVATE not in caplog.text
            assert TOKEN not in caplog.text
            assert len(server.requests) == 1
            with pytest.raises(ProoflineError) as mutation:
                await call(
                    client,
                    "request_review",
                    ORG,
                    REPOSITORY,
                    42,
                    body=RunNowRequest(mode=RunNowMode.FULL),
                )
            assert mutation.value.status == status
            assert PRIVATE not in repr(mutation.value) + str(mutation.value)
            assert TOKEN not in caplog.text
        assert len(server.requests) == 2
        assert server.requests[1].method == "POST"
        assert json.loads(server.requests[1].body) == {"mode": "FULL"}


@MODES
async def test_successful_private_body_decoder_failure_is_static(mode: str) -> None:
    with Server(lambda request, index: Reply(body={"id": PRIVATE, "claim": TOKEN})) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            error = raised.value
            assert error.type == "urn:proofline:sdk:invalid-response"
            assert PRIVATE not in str(error) + repr(error) + error.detail
            assert TOKEN not in "".join(traceback.format_exception(error))


@MODES
async def test_redirect_never_contacts_other_origin(mode: str) -> None:
    with Server(lambda request, index: Reply(body=finding())) as other:
        with Server(
            lambda request, index: Reply(307, None, {"Location": f"{other.url}/stolen"})
        ) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "get_finding", ORG, FINDING)
                assert raised.value.status == 307
                assert raised.value.type == "urn:proofline:sdk:redirect-refused"
            assert len(server.requests) == 1
            assert other.requests == []


@MODES
async def test_retry_after_waits_for_server_then_returns_typed_success(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    with Server(
        lambda request, index: Reply(429, {"detail": "Rate limit."}, {"Retry-After": "2"})
        if index == 0
        else Reply(body=finding())
    ) as server:
        started = time.monotonic()
        async with session(mode, server.url) as client:
            result = await call(client, "get_finding", ORG, FINDING)
            assert result.id == FINDING
        assert time.monotonic() - started >= 2
        assert len(server.requests) == 2

    instant = datetime(2069, 9, 30, tzinfo=UTC)

    class Calendar(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> datetime:
            return instant

    monkeypatch.setattr(_transport, "datetime", Calendar)
    header = (instant + timedelta(seconds=2)).strftime("%A, %d-%b-%y %H:%M:%S GMT")
    with Server(
        lambda request, index: Reply(429, {"detail": "Rate limit."}, {"Retry-After": header})
        if index == 0
        else Reply(body=finding())
    ) as server:
        started = time.monotonic()
        async with session(mode, server.url) as client:
            assert (await call(client, "get_finding", ORG, FINDING)).id == FINDING
        assert time.monotonic() - started >= 2
        assert len(server.requests) == 2


@MODES
@pytest.mark.parametrize("status", [429, 503])
async def test_retry_count_is_bounded_for_rate_limit_and_provider_unavailable(
    mode: str, status: int
) -> None:
    with Server(
        lambda request, index: Reply(status, {"detail": "Unavailable."}, {"Retry-After": "0"})
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            assert raised.value.status == status
        assert len(server.requests) == 4
    with Server(
        lambda request, index: Reply(status, {"detail": "Unavailable."}, {"Retry-After": "0"})
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "rerun_review", ORG, REVIEW)
            assert raised.value.status == status
        assert len(server.requests) == 1
        assert server.requests[0].method == "POST"
        assert server.requests[0].path.endswith(f"/reviews/{REVIEW}/rerun")
    with Server(
        lambda request, index: Reply(status, {"detail": "Unavailable."}, {"Retry-After": "0"})
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(
                    client,
                    "request_review",
                    ORG,
                    REPOSITORY,
                    42,
                    body=RunNowRequest(mode=RunNowMode.FULL),
                )
            assert raised.value.status == status
        assert len(server.requests) == 1
        assert server.requests[0].method == "POST"
        assert server.requests[0].path.endswith(
            f"/repositories/{REPOSITORY}/pull-requests/42/review"
        )
        assert json.loads(server.requests[0].body) == {"mode": "FULL"}


@MODES
async def test_long_retry_after_is_not_retried_early(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Calendar(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> datetime:
            return datetime(2026, 9, 30, tzinfo=UTC)

    monkeypatch.setattr(_transport, "datetime", Calendar)
    future = datetime(2069, 11, 6, 8, 49, 37, tzinfo=UTC)
    for header in ["61", future.strftime("%A, %d-%b-%y %H:%M:%S GMT")]:
        with Server(
            lambda request, index: Reply(503, {"detail": "Unavailable."}, {"Retry-After": header})
        ) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "get_finding", ORG, FINDING)
                assert raised.value.status == 503
            assert len(server.requests) == 1
    # An obsolete year more than fifty years ahead belongs to the past, not a later century.
    for header in [
        "Sunday, 06-Nov-94 08:49:37 GMT",
        "Sun Nov  6 08:49:37 1994",
        "Sun, 06 Nov 1994 08:49:37 GMT",
    ]:
        with Server(
            lambda request, index: Reply(429, {"detail": "Rate limit."}, {"Retry-After": header})
            if index == 0
            else Reply(body=finding())
        ) as server:
            async with session(mode, server.url) as client:
                assert (await call(client, "get_finding", ORG, FINDING)).id == FINDING
            assert len(server.requests) == 2


@MODES
async def test_malformed_retry_after_refuses_retry_without_interpreting_number_as_date(
    mode: str,
) -> None:
    for header in [
        "not a date",
        "NaN",
        "Infinity",
        "-1",
        "1.5",
        "Mon, 06 Nov 1994 08:49:37 GMT",
        "Sun, 31 Feb 2026 08:49:37 GMT",
    ]:
        with Server(
            lambda request, index: Reply(429, {"detail": "Rate limit."}, {"Retry-After": header})
        ) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "get_finding", ORG, FINDING)
                assert raised.value.status == 429
            assert len(server.requests) == 1


@MODES
async def test_success_and_authority_problems_bound_wire_and_encoded_response_bodies(
    mode: str, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    payload = b" " * (_transport.MAX_RESPONSE_BYTES + 1) + json.dumps(finding()).encode()
    for status in [200, 401, 403]:
        with Server(lambda request, index: Reply(status, payload)) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "get_finding", ORG, FINDING)
                assert raised.value.status == status
                assert raised.value.type == "urn:proofline:sdk:invalid-response"
                assert "8 MiB" in raised.value.detail
            assert len(server.requests) == 1
    compressed = gzip.compress(payload)
    assert len(compressed) < _transport.MAX_RESPONSE_BYTES
    with Server(
        lambda request, index: Reply(body=compressed, headers={"Content-Encoding": "gzip"})
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            assert raised.value.type == "urn:proofline:sdk:invalid-response"
            assert "identity encoding" in raised.value.detail
        assert len(server.requests) == 1
    assert PRIVATE not in caplog.text
    assert TOKEN not in caplog.text


@MODES
async def test_wait_retains_evidence_gaps_after_running_review(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    complete = review()
    complete["assessments"][0].update(
        status="INCOMPLETE",
        reason_codes=["WORLD_UNAVAILABLE"],
        incompleteness_kind="WORLD",
        release_evidence_gap=PRIVATE,
    )
    complete["assessments"][0]["checks"] = {
        "receipt_recorded": True,
        "status": "UNRESOLVED",
        "families": [
            {
                "name": "synthetic-check",
                "outcome": "UNRESOLVED",
                "lifecycle": "SHADOW",
                "unresolved_reason": "UNSUPPORTED",
                "detail": PRIVATE,
            }
        ],
    }
    responses = [review("PENDING"), review("RUNNING"), complete]
    with Server(lambda request, index: Reply(body=responses[index])) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=100)
        assert result.status == "INCOMPLETE"
        assert result.review.id == REVIEW
        assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
        gap = result.gaps[0]
        assert gap.assessment_id == ASSESSMENT
        assert gap.reason_codes == ("WORLD_UNAVAILABLE", "CHECK_RECEIPT_UNAVAILABLE")
        assert gap.incompleteness_kind == "WORLD"
        assert gap.release_evidence_gap == PRIVATE
        assert gap.checks[0].unresolved_reason == "UNSUPPORTED"
        assert gap.checks[0].detail == PRIVATE
        assert gap.checks[0].lifecycle == "SHADOW"
        assert PRIVATE not in repr(result) + repr(gap)
        assert clock.delays == [5, 10]


@MODES
async def test_code_only_outcomes_retain_recorded_kind_and_env_precedence(
    mode: str, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    Clock(monkeypatch)
    caplog.set_level(logging.DEBUG)
    bodies: list[dict[str, Any]] = []
    expectations: list[tuple[str, str | None]] = []
    for parent, code_status, kind, expected in [
        ("COMPLETED", "COMPLETED", None, "COMPLETED"),
        ("INCOMPLETE", "INCOMPLETE", "MODEL_BUDGET_EXHAUSTED", "INCOMPLETE"),
        ("COMPLETED", "INCOMPLETE", "FUTURE_CODE_REASON", "INCOMPLETE"),
        ("COMPLETED", "COMPLETED", "EVIDENCE_UNAVAILABLE", "INCOMPLETE"),
        ("FAILED", "INCOMPLETE", "HYPOTHESES_UNRESOLVED", "FAILED"),
        ("STOPPED", "RUNNING", None, "STOPPED"),
        ("COMPLETED", "PENDING", None, "INCOMPLETE"),
        ("EXCLUDED", "EXCLUDED", "POLICY_EXCLUDED", "INCOMPLETE"),
    ]:
        body = review(parent)
        body.update(
            assessment_count=0, assessments=[], code_assessment=code_assessment(code_status)
        )
        body["code_assessment"]["incompleteness_kind"] = kind
        body["code_assessment"]["findings"] = [finding()]
        bodies.append(body)
        expectations.append((expected, kind))
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for expected, kind in expectations:
                result = await call(client, "wait_for_review", ORG, REVIEW)
                assert result.status == expected
                assert result.review.code_assessment.findings[0].claim == PRIVATE
                if result.gaps:
                    assert result.gaps[0].assessment_id == CODE_ASSESSMENT
                    assert result.gaps[0].incompleteness_kind == kind
                    assert result.gaps[0].checks == ()
                    if kind:
                        assert result.gaps[0].reason_codes == ()
                else:
                    assert expected == "COMPLETED"
                assert PRIVATE not in repr(result)
    assert PRIVATE not in caplog.text and TOKEN not in caplog.text

    bodies = []
    expected_states = []
    incomplete_code = code_assessment("INCOMPLETE")
    incomplete_code["incompleteness_kind"] = "POLICY_EXCLUDED"
    for code in [None, {"status": "COMPLETED"}, code_assessment("FUTURE_STATE"), incomplete_code]:
        body = review()
        body["code_assessment"] = code
        bodies.append(body)
        expected_states.append("COMPLETED")
    body = review()
    body["code_assessment"] = code_assessment()
    body["assessments"][0].update(status="INCOMPLETE", reason_codes=["WORLD_UNAVAILABLE"])
    bodies.append(body)
    expected_states.append("INCOMPLETE")
    for count, assessments in [(1, []), (2, [assessment()])]:
        body = review()
        body.update(
            assessment_count=count, assessments=assessments, code_assessment=code_assessment()
        )
        bodies.append(body)
        expected_states.append("INCOMPLETE")
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for expected in expected_states:
                result = await call(client, "wait_for_review", ORG, REVIEW)
                assert result.status == expected
                assert all(gap.assessment_id != CODE_ASSESSMENT for gap in result.gaps)
                if result.review.assessments[0:1] and expected == "INCOMPLETE":
                    assert result.gaps


@MODES
async def test_unusable_code_only_results_never_complete(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    bodies = []
    for code in [UNSET, None, [], {}, {"status": "COMPLETED"}, code_assessment("FUTURE_STATE")]:
        body = review()
        body.update(assessment_count=0, assessments=[])
        if code is not UNSET:
            body["code_assessment"] = code
        bodies.append(body)
    for field, value in [("id", 42), ("findings", None), ("incompleteness_kind", 42)]:
        body = review()
        body.update(assessment_count=0, assessments=[], code_assessment=code_assessment())
        body["code_assessment"][field] = value
        bodies.append(body)
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for _ in bodies:
                result = await call(client, "wait_for_review", ORG, REVIEW)
                assert result.status == "INCOMPLETE"
                assert result.gaps[0].reason_codes == ("CODE_ASSESSMENT_UNAVAILABLE",)


@MODES
async def test_completion_uses_all_declared_lifecycles_and_recorded_checks(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    bodies: list[dict[str, Any]] = []
    expected: list[str] = []
    for lifecycle in ["GATING", "SHADOW", "QUARANTINED", "RETIRED", "UNKNOWN"]:
        for check_outcome in ["READY", "BLOCKED", "NOT_APPLICABLE", "UNRESOLVED"]:
            body = review()
            body["finding_count"] = 1
            body["assessments"][0]["findings"] = [finding()]
            check = {"name": "family", "outcome": check_outcome, "lifecycle": lifecycle}
            if check_outcome == "UNRESOLVED":
                check["unresolved_reason"] = "REGENERATE_SCENARIO"
            body["assessments"][0]["checks"]["families"] = [check]
            bodies.append(body)
            expected.append(
                "INCOMPLETE"
                if lifecycle == "UNKNOWN" or check_outcome == "UNRESOLVED"
                else "COMPLETED"
            )
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for status in expected:
                result = await call(client, "wait_for_review", ORG, REVIEW)
                assert result.status == status
                assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
                assert result.review.assessments[0].findings[0].claim == PRIVATE
        assert len(server.requests) == len(bodies)


@MODES
async def test_unknown_missing_and_unavailable_receipts_never_complete(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    bodies = []
    body = review("FUTURE_STATE")
    bodies.append(body)
    body = review()
    body["assessments"][0]["status"] = "FUTURE_STATE"
    bodies.append(body)
    body = review()
    body["assessments"][0]["checks"]["receipt_recorded"] = False
    bodies.append(body)
    body = review()
    body["assessments"][0]["checks"]["status"] = "UNKNOWN"
    bodies.append(body)
    body = review()
    body["assessments"] = []
    bodies.append(body)
    body = review()
    body["assessment_count"] = 2
    bodies.append(body)
    body = review()
    body["assessments"][0]["incompleteness_kind"] = "SOURCE_UNAVAILABLE"
    bodies.append(body)
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for _ in bodies:
                result = await call(client, "wait_for_review", ORG, REVIEW)
                assert result.status == "INCOMPLETE"
                assert result.gaps


@MODES
async def test_invalid_identity_and_check_shapes_return_protocol_error(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    bodies = []
    body = review()
    body["id"] = str(ASSESSMENT)
    bodies.append(body)
    body = review()
    del body["assessments"][0]["checks"]
    bodies.append(body)
    body = review()
    del body["assessments"][0]["checks"]["families"]
    bodies.append(body)
    body = review()
    body["assessments"][0]["checks"]["receipt_recorded"] = "false"
    bodies.append(body)
    body = review()
    body["assessments"][0]["reason_codes"] = [PRIVATE, 42]
    bodies.append(body)
    body = review()
    body["assessment_count"] = 2
    body["assessments"].append(dict(body["assessments"][0]))
    bodies.append(body)
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for _ in bodies:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "wait_for_review", ORG, REVIEW)
                assert raised.value.type == "urn:proofline:sdk:invalid-response"
                assert PRIVATE not in repr(raised.value) + raised.value.detail


@MODES
@pytest.mark.parametrize("status", ["FAILED", "STOPPED", "SUPERSEDED"])
async def test_failure_and_stop_remain_distinct(
    mode: str, status: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    with Server(lambda request, index: Reply(body=review(status))) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_review", ORG, REVIEW)
            assert result.status == ("FAILED" if status == "FAILED" else "STOPPED")
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert len(server.requests) == 1


@MODES
async def test_polling_backoff_and_timeout_keep_review_url_and_last_record(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    body = review("RUNNING")
    body.update(assessment_count=0, assessments=[], code_assessment=code_assessment("RUNNING"))
    with Server(lambda request, index: Reply(body=body)) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0)
            assert result.status == "TIMED_OUT"
            assert result.review is None
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert server.requests == []
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=260)
            assert result.status == "TIMED_OUT"
            assert result.review.id == REVIEW
            assert result.review.code_assessment.id == CODE_ASSESSMENT
            assert result.gaps[0].assessment_id == CODE_ASSESSMENT
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
        assert clock.delays == [5, 10, 20, 40, 60, 60, 60, 5]
        assert len(server.requests) == 8


@MODES
async def test_retry_after_is_bounded_by_wait_deadline(mode: str) -> None:
    with Server(
        lambda request, index: Reply(503, {"detail": "Unavailable."}, {"Retry-After": "2"})
    ) as server:
        async with session(mode, server.url) as client:
            started = time.monotonic()
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.05)
            assert result.status == "TIMED_OUT"
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert time.monotonic() - started < 0.5
        assert len(server.requests) == 1


@MODES
@pytest.mark.parametrize("status", [429, 503, 403])
async def test_deadline_expiring_with_a_received_problem_chunk_keeps_retry_policy(
    mode: str, status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    checked = _transport.check_stream

    def late(size: int, response_status: int, deadline: float) -> None:
        # The wait deadline passes while a received body chunk is still being checked.
        clock.now += 10
        checked(size, response_status, deadline)

    monkeypatch.setattr(_transport, "check_stream", late)
    with Server(
        lambda request, index: Reply(status, {"detail": PRIVATE}, {"Retry-After": "2"})
    ) as server:
        async with session(mode, server.url) as client:
            if status == 403:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "wait_for_review", ORG, REVIEW, timeout=1)
                assert raised.value.status == 403
            else:
                result = await call(client, "wait_for_review", ORG, REVIEW, timeout=1)
                assert result.status == "TIMED_OUT"
                assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
        assert len(server.requests) == 1
        assert clock.delays == []


@MODES
@pytest.mark.parametrize("status", [200, 403])
async def test_body_stream_deadline_does_not_turn_authority_into_timeout(
    mode: str, status: int
) -> None:
    body = review() if status == 200 else {"detail": PRIVATE}
    with Server(lambda request, index: Reply(status, body, split=8, pause=0.2)) as server:
        async with session(mode, server.url) as client:
            started = time.monotonic()
            if status == 200:
                result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.05)
                assert result.status == "TIMED_OUT"
                assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            else:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "wait_for_review", ORG, REVIEW, timeout=0.05)
                assert raised.value.status == 403
            assert time.monotonic() - started < 0.5
        assert len(server.requests) == 1
    slow_reply = Reply(status, body, split=8, header_pause=0.06, first_pause=0.26, pause=0.24)
    with Server(
        lambda request, index: slow_reply if index == 0 else Reply(body=finding())
    ) as server:
        async with session(mode, server.url) as client:
            started = time.monotonic()
            if status == 200:
                result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.4)
                assert result.status == "TIMED_OUT"
                assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            else:
                with pytest.raises(ProoflineError) as raised:
                    await call(client, "wait_for_review", ORG, REVIEW, timeout=0.4)
                assert raised.value.status == 403
            assert time.monotonic() - started < 0.49
            # The next call inherits neither an expired context nor abandoned response bytes.
            assert (await call(client, "get_finding", ORG, FINDING)).id == FINDING
        assert len(server.requests) == 2
        assert server.requests[0].peer_port != server.requests[1].peer_port
    with Server(lambda request, index: Reply(status, b"")) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "wait_for_review", ORG, REVIEW, timeout=0.1)
            assert raised.value.status == (0 if status == 200 else 403)
            if status == 200:
                assert raised.value.type == "urn:proofline:sdk:invalid-response"

    with Server(lambda request, index: Reply(status, body, header_pause=0.2)) as server:
        async with session(mode, server.url) as client:
            started = time.monotonic()
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.05)
            assert result.status == "TIMED_OUT"
            assert result.review is None
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert time.monotonic() - started < 0.5
        assert len(server.requests) == 1


@MODES
async def test_streaming_and_resolution_keep_deadline_outcomes_explicit(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    with Server(lambda request, index: Reply(body=review(), chunk_size=4, pause=0.01)) as server:
        async with session(mode, server.url) as client:
            started = time.monotonic()
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.06)
            assert result.status == "TIMED_OUT"
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert time.monotonic() - started < 0.5
    with Server(lambda request, index: Reply(body=finding(), chunk_size=4, pause=0.01)) as server:
        async with session(mode, server.url, timeout=0.06) as client:
            started = time.monotonic()
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            assert raised.value.type == "urn:proofline:sdk:timeout"
            assert time.monotonic() - started < 0.5

    original_resolution = socket.getaddrinfo
    resolution_started = threading.Event()
    resolution_finished = threading.Event()
    resolutions: list[bool] = []

    def resolve(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        resolutions.append(True)
        if len(resolutions) > 1:
            return original_resolution(host, port, *args, **kwargs)
        resolution_started.set()
        try:
            time.sleep(0.25)
            return original_resolution("127.0.0.1", port, *args, **kwargs)
        finally:
            resolution_finished.set()

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    with Server(lambda request, index: Reply(body=finding())) as server:
        origin = server.url.replace("http://127.0.0.1", "https://controlled.proofline.invalid")
        async with session(mode, origin) as client:
            started = time.monotonic()
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.05)
            elapsed = time.monotonic() - started
            assert result.status == "TIMED_OUT"
            assert result.review is None
            assert result.review_url == f"{origin}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert resolution_started.is_set()
            assert elapsed < 0.2
            assert not resolution_finished.is_set()
            # Drain the abandoned resolver worker before the loopback peer closes.
            deadline = time.monotonic() + 1
            while not resolution_finished.is_set() and time.monotonic() < deadline:
                await asyncio.sleep(0.01)
            assert resolution_finished.is_set()
            assert server.requests == []


def test_sync_transport_connects_to_each_resolved_address_under_the_original_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lookups: list[tuple[Any, Any]] = []
    scoped_connections: list[str] = []
    refused = socket.socket()
    refused.bind(("127.0.0.1", 0))
    closed_port = refused.getsockname()[1]
    refused.close()

    def resolve(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        lookups.append((host, threading.current_thread().name))
        if host == "missing.proofline.invalid":
            raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")
        if host == "service.proofline.invalid":
            return [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.2", port)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port)),
            ]
        if host == "scoped.proofline.invalid":
            return [
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::1", port, 0, 41)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::1", port, 0, 41)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("fe80::1", port, 0, 42)),
            ]
        if host in {"fe80::1", "fe80::1%41", "fe80::1%42"}:
            # Translate synthetic interface scopes at the OS boundary; TCP stays real.
            scoped_connections.append(host)
            if host == "fe80::1":
                raise socket.gaierror(socket.EAI_NONAME, "The IPv6 scope is missing")
            address = "127.0.0.2" if host == "fe80::1%41" else "127.0.0.1"
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port))]
        return original(host, port, *args, **kwargs)

    original = socket.getaddrinfo
    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    with Server(lambda request, index: Reply(body=finding())) as server:
        port = server.url.rsplit(":", 1)[1]
        with httpx.Client(transport=_sync_http.Transport()) as client:
            response = client.get(f"http://service.proofline.invalid:{port}/finding")
            assert response.json()["id"] == str(FINDING)
            assert server.requests[0].headers["Host"] == f"service.proofline.invalid:{port}"
            assert ("service.proofline.invalid", "proofline-dns") in lookups
            response = client.get(f"http://scoped.proofline.invalid:{port}/finding")
            assert response.json()["id"] == str(FINDING)
            assert server.requests[1].headers["Host"] == f"scoped.proofline.invalid:{port}"
            assert ("scoped.proofline.invalid", "proofline-dns") in lookups
            assert scoped_connections == ["fe80::1%41", "fe80::1%42"]
            with pytest.raises(httpx.TransportError) as raised:
                client.get(f"http://missing.proofline.invalid:{port}/finding")
            assert not isinstance(raised.value, httpx.TimeoutException)
            with pytest.raises(httpx.TransportError):
                client.get(f"http://127.0.0.1:{closed_port}/finding")
        assert len(server.requests) == 2


@MODES
async def test_cursor_pagination_preserves_filters_and_refuses_cycles_or_bounds(mode: str) -> None:
    def respond(request: Request, index: int) -> Reply:
        query = parse_qs(urlsplit(request.path).query)
        assert query["repository"] == [str(REPOSITORY)]
        assert query["status"] == ["COMPLETED"]
        assert query["limit"] == ["2"]
        if index == 0:
            assert "cursor" not in query
        else:
            assert query["cursor"] == ["opaque+/cursor"]
        return Reply(
            body=page(cursor="opaque+/cursor" if index == 0 else None, truncated=index == 0)
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            items = await collect(
                client, page_size=2, filters={"repository": REPOSITORY, "status": "COMPLETED"}
            )
            assert [item.id for item in items] == [REVIEW, REVIEW]
        assert len(server.requests) == 2
    for cursor in ["repeated", None]:
        with Server(
            lambda request, index: Reply(body=page(cursor=cursor, truncated=True))
        ) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await collect(client)
                assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
            assert len(server.requests) <= 2
    with Server(
        lambda request, index: Reply(body=page(cursor=str(index), truncated=True))
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await collect(client, max_pages=2)
            assert raised.value.type == "urn:proofline:sdk:pagination-limit"
        assert len(server.requests) == 2
    two_items = page()
    two_items["items"].append(dict(two_items["items"][0]))
    with Server(lambda request, index: Reply(body=two_items)) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await collect(client, max_items=1, filters={"cursor": "initial"})
            assert raised.value.type == "urn:proofline:sdk:pagination-limit"


def test_token_environment_and_https_origin_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROOFLINE_TOKEN", TOKEN)
    with ProoflineClient() as client:
        assert client._api.token.get_secret_value() == TOKEN
        assert TOKEN not in repr(client._api)
    for origin in [
        "http://api.example",
        "http://localhost",
        "http://127.0.0.1.example",
        "https://user:password@example.com",
        "https://example.com?token=secret",
        "https://example.com/api/v1",
        " https://example.com",
    ]:
        with pytest.raises(ValueError):
            ProoflineClient(TOKEN, base_url=origin)
    with ProoflineClient(TOKEN, base_url="http://[::1]:8080"):
        pass
