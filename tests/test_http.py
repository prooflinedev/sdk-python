from __future__ import annotations

import asyncio
import gzip
import inspect
import json
import logging
import socket
import subprocess
import sys
import threading
import time
import tomllib
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import httpx
import pytest
from pydantic import SecretStr

from proofline import (
    AsyncProoflineClient,
    CommitReviewRequest,
    CommitReviewResponse,
    CoverageUploadRequest,
    CoverageUploadResponse,
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
    UploadedReport,
    _sync_http,
    _transport,
    models,
)
from proofline import client as client_module
from proofline._generated.models.finding_fix_prompt_type_0 import FindingFixPromptType0
from proofline._generated.models.finding_fix_prompt_type_1 import FindingFixPromptType1
from proofline._generated.types import UNSET
from proofline._transport import REFUSAL_SHAPES

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
STRUCTURED_QUERY = '(status:COMPLETED OR status:FAILED) AND -author:"release bot"'


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
async def test_all_public_operations_use_generated_models_and_scoped_paths(mode: str) -> None:
    metadata = Path(__file__).resolve().parents[1] / "pyproject.toml"
    package_version = tomllib.loads(metadata.read_text())["project"]["version"]
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

    def respond(request: Request, index: int) -> Reply:
        method, path, body, _ = paths[index]
        assert request.method == method
        assert urlsplit(request.path).path == path
        return Reply(body=body, headers={"Set-Cookie": "session=must-not-replay; Path=/"})

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            calls = [
                (
                    "list_reviews",
                    (ORG,),
                    {"limit": 7, "repository": REPOSITORY, "query": STRUCTURED_QUERY},
                ),
                (
                    "list_pull_request_reviews",
                    (ORG, "repo/name", 42),
                    {
                        "filters": {
                            "repository": REPOSITORY,
                            "search": "text & space",
                            "query": STRUCTURED_QUERY,
                        }
                    },
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
            assert request.headers["User-Agent"] == f"proofline-python/{package_version}"
            assert request.headers["Accept-Encoding"] == "identity"
            assert "Cookie" not in request.headers
            assert "Content-Type" not in request.headers
            assert request.body == b""
        assert parse_qs(urlsplit(server.requests[0].path).query) == {
            "limit": ["7"],
            "repository": [str(REPOSITORY)],
            "query": [STRUCTURED_QUERY],
        }
        assert parse_qs(urlsplit(server.requests[1].path).query) == {
            "repository": [str(REPOSITORY)],
            "search": ["text & space"],
            "query": [STRUCTURED_QUERY],
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
async def test_coverage_upload_preserves_reports_commit_and_server_refusal(mode: str) -> None:
    content = "SF:src/main.py\nDA:1,1\nDA:2,0\nend_of_record\n"
    body = CoverageUploadRequest(
        tested_sha="a" * 40,
        reports=[UploadedReport(name="python/lcov.info", content=content)],
    )

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "POST"
        assert request.path == (
            f"/api/v1/organizations/{ORG}/repositories/{REPOSITORY}/coverage-reports"
        )
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.body) == {
            "tested_sha": "a" * 40,
            "reports": [{"name": "python/lcov.info", "content": content}],
        }
        if index == 2:
            return Reply(
                status=422,
                body={
                    "title": "unprocessable coverage upload",
                    "status": 422,
                    "detail": "The coverage upload was refused.",
                },
            )
        return Reply(
            status=201 if index == 0 else 200,
            body={
                "report_id": str(REVIEW),
                "tested_sha": "a" * 40,
                "created": index == 0,
                "formats": ["LCOV"],
                "instrumented_lines": 2,
                "covered_lines": 1,
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            for created in (True, False):
                result = await call(client, "upload_coverage_reports", ORG, REPOSITORY, body=body)
                assert isinstance(result, CoverageUploadResponse)
                assert result.report_id == REVIEW
                assert result.tested_sha == "a" * 40
                assert result.created is created
                assert result.formats == ["LCOV"]
                assert (result.covered_lines, result.instrumented_lines) == (1, 2)
            with pytest.raises(ProoflineError) as refused:
                await call(client, "upload_coverage_reports", ORG, REPOSITORY, body=body)
            error = refused.value
            assert (error.status, error.type) == (422, "about:blank")
            assert error.title == "unprocessable coverage upload"
            assert error.detail == "The coverage upload was refused."
            assert (error.refusal, error.repository_name) == (None, None)
        assert len(server.requests) == 3


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


CONTRACT = json.loads((Path(__file__).parents[1] / "openapi.public.json").read_text())
REFUSAL_VARIANTS = CONTRACT["components"]["schemas"]["RunNowRefusalView"]["oneOf"]
ENVIRONMENT = {
    "id": str(ASSESSMENT),
    "external_key": "production",
    "display_name": "Production",
    "status": "PENDING",
}
COMMIT = CommitReviewRequest(base_commit_sha="b" * 40, head_commit_sha="c" * 40)
REVIEW_REQUESTS = {
    "request_review": (42,),
    "request_patch_review": (),
    "request_file_review": (),
    "request_commit_review": (),
}


def review_request(name: str) -> tuple[tuple[Any, ...], dict[str, Any]]:
    bodies = {
        "request_review": UNSET,
        "request_patch_review": PatchReviewRequest(
            base_commit_sha="b" * 40, patch="diff --git a/x b/x\n"
        ),
        "request_file_review": FileReviewRequest(commit_sha="c" * 40, paths=["src/main.py"]),
        "request_commit_review": COMMIT,
    }
    return (ORG, REPOSITORY, *REVIEW_REQUESTS[name]), {"body": bodies[name]}


def refusal_view(variant: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {"reason": variant["properties"]["reason"]["const"]}
    for name in variant["required"]:
        if name == "environment":
            view[name] = dict(ENVIRONMENT, display_name=f"{PRIVATE} {TOKEN}")
        elif name == "detail":
            view[name] = f"Configuration names {TOKEN}."
    return view


def refused(view: Any) -> dict[str, Any]:
    return {
        "title": "invalid request",
        "status": 400,
        "detail": f"Nothing was created for {TOKEN}.",
        "repository_name": "api",
        "refusal": view,
    }


@MODES
@pytest.mark.parametrize(
    "variant", REFUSAL_VARIANTS, ids=[v["properties"]["reason"]["const"] for v in REFUSAL_VARIANTS]
)
async def test_review_requests_return_each_documented_refusal(
    mode: str, variant: dict[str, Any]
) -> None:
    view = refusal_view(variant)
    with Server(
        lambda request, index: Reply(
            400, refused(view), {"Content-Type": "application/problem+json"}
        )
    ) as server:
        async with session(mode, server.url) as client:
            for name in REVIEW_REQUESTS:
                args, kwargs = review_request(name)
                with pytest.raises(ProoflineError) as raised:
                    await call(client, name, *args, **kwargs)
                error = raised.value
                assert (error.status, error.type) == (400, "about:blank")
                assert error.title == "invalid request"
                assert error.detail == "Nothing was created for [redacted]."
                assert error.repository_name == "api"
                assert error.refusal is not None
                assert error.refusal.reason == view["reason"]
                decoded = error.refusal.to_dict()
                assert TOKEN not in json.dumps(decoded)
                if "environment" in view:
                    assert decoded["environment"]["display_name"] == f"{PRIVATE} [redacted]"
                diagnostic = repr(error) + str(error) + "".join(traceback.format_exception(error))
                assert PRIVATE not in diagnostic and TOKEN not in diagnostic
        assert len(server.requests) == len(REVIEW_REQUESTS)


@MODES
@pytest.mark.parametrize(
    "body",
    [
        refused({"reason": "NOT_A_DOCUMENTED_REASON"}),
        refused({"reason": "ENVIRONMENT_REVIEWS_OFF"}),
        refused("NO_LINKED_ENVIRONMENT"),
        dict(refused({"reason": "NO_LINKED_ENVIRONMENT"}), repository_name=7),
        {k: v for k, v in refused({"reason": "NO_LINKED_ENVIRONMENT"}).items() if k != "detail"},
        refused({"reason": "INVALID_DELIVERY_CONFIGURATION", "detail": 7, "environment": 7}),
        refused({"reason": "INVALID_DELIVERY_CONFIGURATION", "detail": "d", "environment": 7}),
        refused({"reason": "ENVIRONMENT_REVIEWS_OFF", "environment": dict(ENVIRONMENT, id=7)}),
        refused(
            {
                "reason": "INVALID_DELIVERY_CONFIGURATION",
                "detail": "d",
                "environment": dict(ENVIRONMENT, id="not-a-uuid"),
            }
        ),
        refused({"reason": "ENVIRONMENT_REVIEWS_OFF", "environment": dict(ENVIRONMENT, id="x")}),
        refused(
            {"reason": "ENVIRONMENT_NOT_READY", "environment": ENVIRONMENT, "status_detail": 7}
        ),
    ],
    ids=[
        "unknown-reason",
        "missing-environment",
        "untyped-refusal",
        "repository-name",
        "detail",
        "numeric-delivery-fields",
        "numeric-delivery-environment",
        "environment-field",
        "delivery-environment-id",
        "required-environment-id",
        "status-detail",
    ],
)
async def test_malformed_refusal_keeps_fixed_sdk_problem_type(
    mode: str, body: dict[str, Any]
) -> None:
    with Server(lambda request, index: Reply(400, body)) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "request_commit_review", ORG, REPOSITORY, body=COMMIT)
            error = raised.value
            assert (error.status, error.type) == (400, "urn:proofline:sdk:invalid-response")
            assert error.title == "invalid request"
            assert (error.refusal, error.repository_name) == (None, None)
            assert TOKEN not in error.detail


def test_every_documented_refusal_reason_has_a_field_check() -> None:
    reasons = {variant["properties"]["reason"]["const"] for variant in REFUSAL_VARIANTS}
    assert set(REFUSAL_SHAPES) == reasons


@MODES
async def test_problem_without_detail_keeps_status_and_title(mode: str) -> None:
    with Server(
        lambda request, index: Reply(
            500, {"title": "internal error", "status": 500, "detail": None}
        )
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "get_finding", ORG, FINDING)
            error = raised.value
            assert (error.status, error.type, error.title) == (500, "about:blank", "internal error")
            assert "without a problem document" not in error.detail
            assert "internal error" in error.detail
            assert error.refusal is None
        assert len(server.requests) == 1


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
        lambda request, index: (
            Reply(429, {"detail": "Rate limit."}, {"Retry-After": "2"})
            if index == 0
            else Reply(body=finding())
        )
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
        lambda request, index: (
            Reply(429, {"detail": "Rate limit."}, {"Retry-After": header})
            if index == 0
            else Reply(body=finding())
        )
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
            lambda request, index: (
                Reply(429, {"detail": "Rate limit."}, {"Retry-After": header})
                if index == 0
                else Reply(body=finding())
            )
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
                "files": [
                    {
                        "revision": "PROPOSED_CODE_REVISION",
                        "path": {"untrusted_text": "<b>deploy</b>.yml"},
                    },
                    {
                        "revision": "BASE_CODE_REVISION",
                        "path": {"untrusted_text": "deploy.yml"},
                    },
                ],
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
        assert gap.reason_codes == ("WORLD_UNAVAILABLE", "WORLD", PRIVATE, "CHECKS_UNRESOLVED")
        assert gap.incompleteness_kind == "WORLD"
        assert gap.release_evidence_gap == PRIVATE
        assert gap.checks[0].unresolved_reason == "UNSUPPORTED"
        assert gap.checks[0].detail == PRIVATE
        assert gap.checks[0].lifecycle == "SHADOW"
        files = result.review.assessments[0].checks.families[0].files
        assert [(file.revision, file.path.untrusted_text) for file in files] == [
            ("PROPOSED_CODE_REVISION", "<b>deploy</b>.yml"),
            ("BASE_CODE_REVISION", "deploy.yml"),
        ]
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
                        assert result.gaps[0].reason_codes == (kind,)
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
            check = {
                "name": "family",
                "outcome": check_outcome,
                "lifecycle": lifecycle,
                "files": [],
            }
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
async def test_retry_after_is_bounded_by_wait_deadline(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with Server(
        lambda request, index: Reply(503, {"detail": "Unavailable."}, {"Retry-After": "20"})
    ) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=10)
            assert result.status == "TIMED_OUT"
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
        assert len(server.requests) == 1
        assert clock.delays == [10]


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
    mode: str, status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = review() if status == 200 else {"detail": PRIVATE}
    # Expire only after the real transport receives the status. A short wall-clock
    # timeout can expire before headers on a busy worker, when TIMED_OUT is correct.
    with monkeypatch.context() as patch:
        clock = Clock(patch)
        sync_request = _sync_http.Transport.handle_request
        async_request = httpx.AsyncHTTPTransport.handle_async_request

        def expire_sync(transport: _sync_http.Transport, request: httpx.Request) -> httpx.Response:
            response = sync_request(transport, request)
            clock.now += 10
            return response

        async def expire_async(
            transport: httpx.AsyncHTTPTransport, request: httpx.Request
        ) -> httpx.Response:
            response = await async_request(transport, request)
            clock.now += 10
            return response

        patch.setattr(_sync_http.Transport, "handle_request", expire_sync)
        patch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", expire_async)
        with Server(lambda request, index: Reply(status, body, split=8, pause=0.2)) as server:
            async with session(mode, server.url) as client:
                if status == 200:
                    result = await call(client, "wait_for_review", ORG, REVIEW, timeout=10)
                    assert result.status == "TIMED_OUT"
                    assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
                else:
                    with pytest.raises(ProoflineError) as raised:
                        await call(client, "wait_for_review", ORG, REVIEW, timeout=10)
                    assert raised.value.status == 403
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

    # The headers wait far past a deadline that leaves time to connect and send. The
    # client counts its own attempts, so the no-retry proof needs no scheduler timing.
    attempts = 0
    with monkeypatch.context() as patch:
        sync_request = _sync_http.Transport.handle_request
        async_request = httpx.AsyncHTTPTransport.handle_async_request

        def count_sync(transport: _sync_http.Transport, request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            return sync_request(transport, request)

        async def count_async(
            transport: httpx.AsyncHTTPTransport, request: httpx.Request
        ) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            return await async_request(transport, request)

        patch.setattr(_sync_http.Transport, "handle_request", count_sync)
        patch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", count_async)
        with Server(lambda request, index: Reply(status, body, header_pause=2.0)) as server:
            async with session(mode, server.url) as client:
                started = time.monotonic()
                result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.3)
                assert result.status == "TIMED_OUT"
                assert result.review is None
                assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
                assert time.monotonic() - started < 1.5
            assert attempts == 1
            # The request was sent before the header wait, so the server reads it
            # even after the client gives up.
            recorded = time.monotonic() + 5
            while not server.requests and time.monotonic() < recorded:
                time.sleep(0.01)
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
        assert urlsplit(request.path).path == f"/api/v1/organizations/{ORG}/reviews"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        query = parse_qs(urlsplit(request.path).query)
        assert query["repository"] == [str(REPOSITORY)]
        assert query["status"] == ["COMPLETED"]
        assert query["limit"] == ["2"]
        assert query["query"] == [STRUCTURED_QUERY]
        assert query["search"] == ["text & space"]
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
                client,
                page_size=2,
                filters={
                    "repository": REPOSITORY,
                    "status": "COMPLETED",
                    "query": STRUCTURED_QUERY,
                    "search": "text & space",
                },
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


@MODES
async def test_export_pages_preserve_csv_and_refuse_foreign_cursor(mode: str) -> None:
    def respond(request: Request, index: int) -> Reply:
        query = parse_qs(urlsplit(request.path).query)
        assert request.path.startswith(f"/api/v1/organizations/{ORG}/exports/findings?")
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        if query.get("cursor") == ["refused"]:
            return Reply(status=404, body={"detail": "not found"})
        is_csv = query.get("format") == ["csv"]
        return Reply(
            body=(
                b'dataset_version,claim\r\n1,"comma, quote "" and\nnewline"\r\n'
                if is_csv
                else b'{"dataset_version":1,"claim":"hello"}\n'
            ),
            headers={
                "Content-Type": "text/csv" if is_csv else "application/x-ndjson",
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
                "X-Proofline-Export-Next-Cursor": "opaque/+cursor",
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            kwargs = {"from_time": "2026-10-01T00:00:00Z", "to_time": "2026-10-25T00:00:00Z"}
            exported = await call(client, "export_reviews", ORG, "findings", format="csv", **kwargs)
            assert exported.rows[0]["claim"] == 'comma, quote " and\nnewline'
            assert exported.next_cursor == "opaque/+cursor"
            exported = await call(
                client, "export_reviews", ORG, "findings", cursor=exported.next_cursor, **kwargs
            )
            assert exported.rows[0]["dataset_version"] == 1
            assert "cursor=opaque%2F%2Bcursor" in server.requests[1].path
            with pytest.raises(ProoflineError) as caught:
                await call(client, "export_reviews", ORG, "findings", cursor="refused", **kwargs)
            assert caught.value.status == 404


@MODES
async def test_knowledge_negotiation_scope_and_no_retry(mode: str) -> None:
    refusal = False
    wrong_id = False

    def respond(request: Request, index: int) -> Reply:
        body = json.loads(request.body)
        assert request.path == "/mcp"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        if body["method"] == "initialize":
            return Reply(
                body={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}
            )
        assert request.headers["MCP-Protocol-Version"] == "2025-11-25"
        if body["method"] == "notifications/initialized":
            return Reply(status=202, body=b"")
        assert body["params"] == {
            "name": "get_wiki_page",
            "arguments": {"repository": "owner/name", "page_key": "index", "commit": "a" * 40},
        }
        if refusal:
            return Reply(status=503, body={"detail": "unavailable"})
        return Reply(
            body={
                "jsonrpc": "2.0",
                "id": 99 if wrong_id else 2,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": "RESOURCE_NOT_FOUND"}],
                },
            }
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:

            async def invoke() -> Any:
                result = client.knowledge.get_wiki_page("owner/name", "index", commit="a" * 40)
                return await result if inspect.isawaitable(result) else result

            assert (await invoke())["isError"] is True
            wrong_id = True
            with pytest.raises(ProoflineError):
                await invoke()
            refusal = True
            with pytest.raises(ProoflineError):
                await invoke()
        assert len(server.requests) == 9


@MODES
async def test_fixes_preserve_unavailable_context_and_never_retry(mode: str) -> None:
    observed: list[dict[str, Any]] = []
    refuse = False
    result = {
        "content": [{"type": "text", "text": "untrusted source"}],
        "structuredContent": {"status": "UNAVAILABLE", "items": None},
    }

    def respond(request: Request, index: int) -> Reply:
        body = json.loads(request.body)
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        if body["method"] == "initialize":
            return Reply(
                body={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}
            )
        if body["method"] == "notifications/initialized":
            return Reply(status=202, body=b"")
        observed.append(body["params"])
        if refuse:
            return Reply(status=503, body={"detail": "unavailable"}, headers={"Retry-After": "0"})
        return Reply(body={"jsonrpc": "2.0", "id": 2, "result": result})

    with Server(respond) as server:
        async with session(mode, server.url) as client:

            async def invoke(name: str, *args: Any, **kwargs: Any) -> Any:
                answer = getattr(client.fixes, name)(*args, **kwargs)
                return await answer if inspect.isawaitable(answer) else answer

            assert await invoke("list_open_findings", "owner/name", 7) == result
            assert await invoke("get_fix_context", str(REVIEW)) == result
            assert (
                await invoke(
                    "request_reverification",
                    str(REVIEW),
                    [str(REVIEW)],
                    "a" * 40,
                    note="fixed code",
                )
                == result
            )
            assert await invoke("get_reverification", str(REVIEW)) == result
            assert observed == [
                {
                    "name": "list_open_findings",
                    "arguments": {"repository": "owner/name", "pull_request_number": 7},
                },
                {"name": "get_fix_context", "arguments": {"finding_id": str(REVIEW)}},
                {
                    "name": "request_reverification",
                    "arguments": {
                        "review_id": str(REVIEW),
                        "finding_ids": [str(REVIEW)],
                        "commit_sha": "a" * 40,
                        "note": "fixed code",
                    },
                },
                {"name": "get_reverification", "arguments": {"request_id": str(REVIEW)}},
            ]
            refuse = True
            with pytest.raises(ProoflineError):
                await invoke("request_reverification", str(REVIEW), [str(REVIEW)], "a" * 40)
            assert len(observed) == 5


@MODES
async def test_shared_review_outcome_contract(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    Clock(monkeypatch)
    fixture = json.loads((Path(__file__).parent / "fixtures/review-outcomes.json").read_text())
    for case in fixture["cases"]:
        body = case["review"]
        pending = case["outcome"] is None
        settled = next(
            item["review"] for item in fixture["cases"] if item["name"] == "review-completed"
        )
        with Server(
            lambda request, index: Reply(body=settled if pending and index else body)
        ) as server:
            async with session(mode, server.url) as client:
                result = await call(client, "wait_for_review", ORG, UUID(body["id"]))
            assert result.status == ("COMPLETED" if pending else case["outcome"]), case["name"]
            assert len(server.requests) == (2 if pending else 1), case["name"]
            assert [
                {
                    "assessment_id": str(gap.assessment_id) if gap.assessment_id else None,
                    "reason_codes": list(gap.reason_codes),
                }
                for gap in result.gaps
            ] == case["gaps"], case["name"]


@MODES
async def test_mcp_per_call_organizations_and_refusals(mode: str) -> None:
    first, second, foreign = (str(ORG), str(REVIEW), str(ASSESSMENT))
    admitted = [first, second]
    observed: list[dict[str, Any]] = []
    concurrent = False
    overlap = threading.Barrier(2)

    def respond(request: Request, index: int) -> Reply:
        assert request.path == "/mcp"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = json.loads(request.body)
        if body["method"] == "initialize":
            return Reply(
                body={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}
            )
        assert request.headers["MCP-Protocol-Version"] == "2025-11-25"
        if body["method"] == "notifications/initialized":
            return Reply(status=202, body=b"")
        params = body["params"]
        observed.append(params)
        if params["name"] == "list_organizations":
            assert params["arguments"] == {}
            result: dict[str, Any] = {
                "content": [],
                "structuredContent": {
                    "ok": True,
                    "data": {"organizations": [{"organization_id": value} for value in admitted]},
                },
            }
        else:
            if concurrent:
                # Neither response completes until both tool calls have arrived.
                overlap.wait(timeout=5)
            target = params["arguments"].get("organization_id")
            code = (
                "ORGANIZATION_REQUIRED"
                if target is None
                else "NOT_AUTHORIZED"
                if target not in admitted
                else None
            )
            payload = (
                {
                    "ok": False,
                    "error": {"code": code, "message": "Target refused", "retryable": False},
                }
                if code
                else {"ok": True, "data": {"organization_id": target}}
            )
            result = {
                "isError": code is not None,
                "content": [{"type": "text", "text": json.dumps(payload)}],
                "structuredContent": payload,
            }
        return Reply(body={"jsonrpc": "2.0", "id": 2, "result": result})

    with Server(respond) as server:
        async with session(mode, server.url) as client:

            async def invoke(group: str, name: str, *args: Any, **kwargs: Any) -> Any:
                result = getattr(getattr(client, group), name)(*args, **kwargs)
                return await result if inspect.isawaitable(result) else result

            discovery = await invoke("mcp", "list_organizations")
            assert discovery["structuredContent"]["data"]["organizations"] == [
                {"organization_id": first},
                {"organization_id": second},
            ]
            cases = [
                (
                    "knowledge",
                    "list_wiki_pages",
                    ("owner/name",),
                    {"commit": "a" * 40},
                    {"repository": "owner/name", "commit": "a" * 40},
                ),
                (
                    "knowledge",
                    "get_wiki_page",
                    ("owner/name", "index"),
                    {},
                    {"repository": "owner/name", "page_key": "index"},
                ),
                (
                    "knowledge",
                    "ask_codebase",
                    ("owner/name", "How?"),
                    {},
                    {"repository": "owner/name", "question": "How?"},
                ),
                (
                    "knowledge",
                    "get_architecture_document",
                    (str(REVIEW),),
                    {},
                    {"environment_id": str(REVIEW)},
                ),
                ("knowledge", "get_plan", (str(REVIEW),), {}, {"plan_id": str(REVIEW)}),
                (
                    "knowledge",
                    "start_plan_implementation",
                    (str(REVIEW),),
                    {},
                    {"plan_id": str(REVIEW)},
                ),
                (
                    "knowledge",
                    "get_plan_implementation",
                    (str(REVIEW),),
                    {},
                    {"implementation_id": str(REVIEW)},
                ),
                (
                    "fixes",
                    "list_open_findings",
                    ("owner/name", 7),
                    {},
                    {"repository": "owner/name", "pull_request_number": 7},
                ),
                ("fixes", "get_fix_context", (str(REVIEW),), {}, {"finding_id": str(REVIEW)}),
                (
                    "fixes",
                    "request_reverification",
                    (str(REVIEW), [str(REVIEW)], "a" * 40),
                    {"note": "fixed"},
                    {
                        "review_id": str(REVIEW),
                        "finding_ids": [str(REVIEW)],
                        "commit_sha": "a" * 40,
                        "note": "fixed",
                    },
                ),
                ("fixes", "get_reverification", (str(REVIEW),), {}, {"request_id": str(REVIEW)}),
            ]
            for group, name, args, kwargs, expected in cases:
                for target in (first, second):
                    answer = await invoke(group, name, *args, **kwargs, organization_id=target)
                    assert answer["structuredContent"]["data"]["organization_id"] == target
                    assert observed[-1] == {
                        "name": name,
                        "arguments": {**expected, "organization_id": target},
                    }

            if mode == "async":
                concurrent = True
                answers = await asyncio.gather(
                    invoke("knowledge", "get_plan", str(REVIEW), organization_id=first),
                    invoke("fixes", "get_fix_context", str(REVIEW), organization_id=second),
                )
                concurrent = False
                assert [
                    answer["structuredContent"]["data"]["organization_id"] for answer in answers
                ] == [first, second]

            async def refused(target: str | None, code: str) -> None:
                before = len(observed)
                kwargs = {} if target is None else {"organization_id": target}
                answer = await invoke(
                    "fixes",
                    "request_reverification",
                    str(REVIEW),
                    [str(REVIEW)],
                    "a" * 40,
                    **kwargs,
                )
                assert answer["isError"] is True
                assert answer["structuredContent"]["error"]["code"] == code
                assert json.loads(answer["content"][0]["text"]) == answer["structuredContent"]
                assert len(observed) == before + 1
                assert observed[-1]["arguments"].get("organization_id") == target
                assert ("organization_id" in observed[-1]["arguments"]) == (target is not None)

            # An earlier explicit target must never become an implicit default.
            await refused(None, "ORGANIZATION_REQUIRED")
            await refused(foreign, "NOT_AUTHORIZED")
            admitted.remove(first)
            await refused(first, "NOT_AUTHORIZED")
            remaining = await invoke("mcp", "list_organizations")
            assert remaining["structuredContent"]["data"]["organizations"] == [
                {"organization_id": second}
            ]
            answer = await invoke("fixes", "get_fix_context", str(REVIEW), organization_id=second)
            assert answer["structuredContent"]["data"]["organization_id"] == second
        assert len(server.requests) == len(observed) * 3


def test_mcp_public_types_accept_legacy_and_targeted_calls(tmp_path: Path) -> None:
    # Compile consumer code through the public entry point; dynamic HTTP tests
    # cannot catch a missing keyword in just one sync/async method signature.
    lines = ["from proofline import ProoflineClient, AsyncProoflineClient, KnowledgeResult"]
    calls = [
        'knowledge.list_wiki_pages("owner/name", commit="a" * 40)',
        'knowledge.get_wiki_page("owner/name", "index")',
        'knowledge.ask_codebase("owner/name", "How?")',
        'knowledge.get_architecture_document("environment-id")',
        'knowledge.get_plan("plan-id")',
        'knowledge.start_plan_implementation("plan-id")',
        'knowledge.get_plan_implementation("implementation-id")',
        'fixes.list_open_findings("owner/name", 7)',
        'fixes.get_fix_context("finding-id")',
        'fixes.request_reverification("review-id", ["finding-id"], "a" * 40, note="fixed")',
        'fixes.get_reverification("request-id")',
    ]
    for prefix, kind, wait in [
        ("", "ProoflineClient", ""),
        ("async ", "AsyncProoflineClient", "await "),
    ]:
        lines.append(f"{prefix}def use_{kind}(client: {kind}) -> None:")
        lines.append(f"    result: KnowledgeResult = {wait}client.mcp.list_organizations()")
        for expression in calls:
            lines.append(f"    result = {wait}client.{expression}")
            targeted = expression[:-1] + ', organization_id="00000000-0000-7000-8000-000000000001")'
            lines.append(f"    result = {wait}client.{targeted}")
    fixture = tmp_path / "mcp_types.py"
    fixture.write_text("\n".join(lines))
    # Use the same mypy configuration as the SDK qualification gate.
    subprocess.run([sys.executable, "-m", "mypy", str(fixture)], check=True)


@MODES
async def test_export_ndjson_preserves_unicode_line_separators(mode: str) -> None:
    kwargs = {
        "from_time": "2026-10-01T00:00:00Z",
        "to_time": "2026-10-25T00:00:00Z",
    }

    for separator in ("\x85", "\u2028", "\u2029"):
        row = {
            "dataset_version": 1,
            "claim": f"before{separator}after",
        }
        body = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")

        def respond(request: Request, index: int) -> Reply:
            return Reply(
                body=body,
                headers={
                    "Content-Type": "application/x-ndjson",
                    "X-Proofline-Export-Version": "1",
                    "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
                    "X-Proofline-Export-Next-Cursor": "next-page",
                },
            )

        with Server(respond) as server:
            async with session(mode, server.url) as client:
                exported = await call(
                    client,
                    "export_reviews",
                    ORG,
                    "findings",
                    format="ndjson",
                    **kwargs,
                )

                assert len(exported.rows) == 1
                assert exported.rows[0]["claim"] == row["claim"]
                assert exported.next_cursor == "next-page"
