from __future__ import annotations

import array
import asyncio
import csv
import gzip
import inspect
import io
import json
import logging
import socket
import subprocess
import sys
import threading
import time
import tomllib
import traceback
import weakref
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import httpx2
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
from proofline._generated.models.export_review_kind import ExportReviewKind
from proofline._generated.models.finding_fix_prompt_type_0 import FindingFixPromptType0
from proofline._generated.models.finding_fix_prompt_type_1 import FindingFixPromptType1
from proofline._generated.models.reviews_export_row import ReviewsExportRow
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


@MODES
@pytest.mark.parametrize(
    "view",
    [
        {"reason": "OUT_OF_CREDITS"},
        {"reason": "PLAN_CREDITS_SPENT", "resets": "2026-12-01T00:00:00Z"},
    ],
    ids=["out-of-credits", "plan-credits-spent"],
)
async def test_credit_refusal_keeps_the_server_problem(mode: str, view: dict[str, Any]) -> None:
    body = {
        "title": "payment required",
        "status": 402,
        "detail": f"Credits cannot pay for {TOKEN}.",
        "repository_name": "api",
        "refusal": view,
    }
    with Server(
        lambda request, index: Reply(402, body, {"Content-Type": "application/problem+json"})
    ) as server:
        async with session(mode, server.url) as client:
            for name in REVIEW_REQUESTS:
                args, kwargs = review_request(name)
                with pytest.raises(ProoflineError) as raised:
                    await call(client, name, *args, **kwargs)
                error = raised.value
                assert (error.status, error.type) == (402, "about:blank")
                assert error.title == "payment required"
                assert error.detail == "Credits cannot pay for [redacted]."
                assert (error.refusal, error.repository_name) == (None, None)
        assert len(server.requests) == len(REVIEW_REQUESTS)


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
    clock = Clock(monkeypatch)
    with Server(
        lambda request, index: (
            Reply(429, {"detail": "Rate limit."}, {"Retry-After": "2"})
            if index == 0
            else Reply(body=finding())
        )
    ) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "get_finding", ORG, FINDING)
            assert result.id == FINDING
        assert clock.delays == [2.0]
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
        async with session(mode, server.url) as client:
            assert (await call(client, "get_finding", ORG, FINDING)).id == FINDING
        assert clock.delays == [2.0, 2.0]
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


HEAD = "a" * 40
OTHER_HEAD = "c" * 40
PINNED_ELSEWHERE = (None, "UNKNOWN", ("HEAD_COMMIT_MISMATCH",))
NO_HEAD = (None, "UNKNOWN", ("HEAD_COMMIT_UNAVAILABLE",))


def review_at(head: Any, status: str = "COMPLETED") -> dict[str, Any]:
    return {**review(status), "head_commit_sha": head}


def gap_facts(result: Any) -> list[tuple[Any, str, tuple[str, ...]]]:
    return [(gap.assessment_id, gap.status, gap.reason_codes) for gap in result.gaps]


@MODES
async def test_wait_held_to_a_head_commit_never_completes_for_another(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with Server(lambda request, index: Reply(body=review_at(HEAD))) as server:
        async with session(mode, server.url) as client:
            for held in (HEAD, HEAD.upper()):
                result = await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha=held)
                assert (result.status, result.gaps, result.reason) == ("COMPLETED", (), None)
            result = await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha=OTHER_HEAD)
            assert result.status == "INCOMPLETE"
            assert gap_facts(result) == [PINNED_ELSEWHERE]
            assert result.reason == "The review is pinned to another head commit."
            assert result.review.head_commit_sha == HEAD
            assert result.review_url == f"{server.url}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert HEAD not in repr(result) and OTHER_HEAD not in repr(result)
            # Without the keyword the same record completes, as it always has.
            result = await call(client, "wait_for_review", ORG, REVIEW)
            assert (result.status, result.gaps, result.reason) == ("COMPLETED", (), None)
        assert len(server.requests) == 4
        assert clock.delays == []


@MODES
async def test_wait_ends_on_the_read_that_names_another_head(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    responses = [review("PENDING"), review_at(HEAD, "RUNNING"), review_at(HEAD)]
    with Server(lambda request, index: Reply(body=responses[index])) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_review", ORG, REVIEW, timeout=100, head_commit_sha=HEAD
            )
        assert (result.status, result.gaps, result.reason) == ("COMPLETED", (), None)
        assert len(server.requests) == 3
        assert clock.delays == [5, 10]
    # Mismatch without on_poll ends on the read that names another head (2 requests)
    with Server(lambda request, index: Reply(body=responses[index])) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client,
                "wait_for_review",
                ORG,
                REVIEW,
                timeout=100,
                head_commit_sha=OTHER_HEAD,
            )
        assert result.status == "INCOMPLETE"
        assert result.review.status == "RUNNING"
        assert gap_facts(result) == [PINNED_ELSEWHERE]
        assert result.reason == "The review is pinned to another head commit."
        assert len(server.requests) == 2
        assert clock.delays == [5, 10, 5]

    # Mismatch with on_poll also ends on the read that names another head (2 requests)
    with Server(lambda request, index: Reply(body=responses[index])) as server:
        polled_reviews: list[tuple[Any, int]] = []
        cb = (
            (lambda r: polled_reviews.append((r, len(server.requests))))
            if mode == "sync"
            else (lambda r: polled_reviews.append((r, len(server.requests))))
        )
        async with session(mode, server.url) as client:
            result = await call(
                client,
                "wait_for_review",
                ORG,
                REVIEW,
                timeout=100,
                head_commit_sha=OTHER_HEAD,
                on_poll=cb,
            )
        assert result.status == "INCOMPLETE"
        assert result.review.status == "RUNNING"
        assert gap_facts(result) == [PINNED_ELSEWHERE]
        assert result.reason == "The review is pinned to another head commit."
        # The second read names the head, so the review that would complete is never read.
        assert len(server.requests) == 2
        assert clock.delays == [5, 10, 5, 5]
        assert [p[0].status for p in polled_reviews] == ["PENDING", "RUNNING"]
        assert [p[1] for p in polled_reviews] == [1, 2]
        assert polled_reviews[0][0].head_commit_sha is UNSET
        assert polled_reviews[1][0].head_commit_sha == HEAD


@MODES
async def test_a_review_of_another_head_is_incomplete_whatever_its_own_status(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    statuses = ["FAILED", "STOPPED", "SUPERSEDED"]
    with Server(lambda request, index: Reply(body=review_at(HEAD, statuses[index // 2]))) as server:
        async with session(mode, server.url) as client:
            for status in statuses:
                result = await call(
                    client, "wait_for_review", ORG, REVIEW, head_commit_sha=OTHER_HEAD
                )
                assert (result.status, gap_facts(result)) == ("INCOMPLETE", [PINNED_ELSEWHERE])
                assert result.review.status == status
                result = await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha=HEAD)
                assert result.status == ("FAILED" if status == "FAILED" else "STOPPED")
                assert (result.gaps, result.reason) == ((), None)
        assert len(server.requests) == 6


@MODES
async def test_a_review_that_names_no_head_never_completes_for_a_named_commit(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    bodies = [
        review(),
        review_at(None),
        review_at(""),
        review_at(7),
        review_at(None, "FAILED"),
        review_at(None, "SUPERSEDED"),
    ]
    expected = ["INCOMPLETE", "INCOMPLETE", "INCOMPLETE", "INCOMPLETE", "FAILED", "STOPPED"]
    with Server(lambda request, index: Reply(body=bodies[index])) as server:
        async with session(mode, server.url) as client:
            for status in expected:
                result = await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha=HEAD)
                assert result.status == status
                assert gap_facts(result) == [NO_HEAD]
                assert result.reason == "The review names no head commit."
        assert len(server.requests) == len(bodies)
        assert clock.delays == []
    # A review that is still pending may name its head later, so the wait goes on.
    with Server(lambda request, index: Reply(body=review("PENDING"))) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_review", ORG, REVIEW, timeout=12, head_commit_sha=HEAD
            )
        assert result.status == "TIMED_OUT"
        assert gap_facts(result) == [NO_HEAD]
        assert result.reason == "The review names no head commit."
        assert len(server.requests) == 2
        assert clock.delays == [5, 7]


@MODES
async def test_head_commit_must_be_a_full_sha_before_any_request(mode: str) -> None:
    refused = [
        "main",
        "a" * 7,
        "a" * 39,
        "a" * 41,
        "g" * 40,
        "\u0661" * 40,
        HEAD + "\n",
        " " + HEAD[1:],
        "",
        7,
        HEAD.encode(),
    ]
    with Server(lambda request, index: Reply(body=review_at("d" * 64))) as server:
        async with session(mode, server.url) as client:
            for value in refused:
                with pytest.raises(ValueError, match="full 40 or 64 character"):
                    await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha=value)
            assert server.requests == []
            result = await call(client, "wait_for_review", ORG, REVIEW, head_commit_sha="D" * 64)
            assert (result.status, result.gaps, result.reason) == ("COMPLETED", (), None)
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
        async_request = httpx2.AsyncHTTPTransport.handle_async_request

        def expire_sync(
            transport: _sync_http.Transport, request: httpx2.Request
        ) -> httpx2.Response:
            response = sync_request(transport, request)
            clock.now += 10
            return response

        async def expire_async(
            transport: httpx2.AsyncHTTPTransport, request: httpx2.Request
        ) -> httpx2.Response:
            response = await async_request(transport, request)
            clock.now += 10
            return response

        patch.setattr(_sync_http.Transport, "handle_request", expire_sync)
        patch.setattr(httpx2.AsyncHTTPTransport, "handle_async_request", expire_async)
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
        async_request = httpx2.AsyncHTTPTransport.handle_async_request

        def count_sync(transport: _sync_http.Transport, request: httpx2.Request) -> httpx2.Response:
            nonlocal attempts
            attempts += 1
            return sync_request(transport, request)

        async def count_async(
            transport: httpx2.AsyncHTTPTransport, request: httpx2.Request
        ) -> httpx2.Response:
            nonlocal attempts
            attempts += 1
            return await async_request(transport, request)

        patch.setattr(_sync_http.Transport, "handle_request", count_sync)
        patch.setattr(httpx2.AsyncHTTPTransport, "handle_async_request", count_async)
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
    resolution_released = threading.Event()
    resolution_finished = threading.Event()
    resolutions: list[bool] = []

    def resolve(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        resolutions.append(True)
        if len(resolutions) > 1:
            return original_resolution(host, port, *args, **kwargs)
        resolution_started.set()
        try:
            # Hang until the test releases it, so the deadline expires during the lookup
            # whenever the worker starts. The bound only ends a call that waits for it.
            resolution_released.wait(5)
            return original_resolution("127.0.0.1", port, *args, **kwargs)
        finally:
            resolution_finished.set()

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    with Server(lambda request, index: Reply(body=finding())) as server:
        origin = server.url.replace("http://127.0.0.1", "https://controlled.proofline.invalid")
        async with session(mode, origin) as client:
            # The resolver worker starts within a millisecond on an idle host; the deadline
            # leaves a loaded check worker half a second to start it (#19783).
            result = await call(client, "wait_for_review", ORG, REVIEW, timeout=0.5)
            assert result.status == "TIMED_OUT"
            assert result.review is None
            assert result.review_url == f"{origin}/orgs/by-id/{ORG}/reviews/{REVIEW}"
            assert resolution_started.is_set()
            assert not resolution_finished.is_set()
            # Drain the abandoned resolver worker before the loopback peer closes.
            resolution_released.set()
            deadline = time.monotonic() + 5
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
        with httpx2.Client(transport=_sync_http.Transport()) as client:
            response = client.get(f"http://service.proofline.invalid:{port}/finding")
            assert response.json()["id"] == str(FINDING)
            assert server.requests[0].headers["Host"] == f"service.proofline.invalid:{port}"
            assert ("service.proofline.invalid", "proofline-dns") in lookups
            response = client.get(f"http://scoped.proofline.invalid:{port}/finding")
            assert response.json()["id"] == str(FINDING)
            assert server.requests[1].headers["Host"] == f"scoped.proofline.invalid:{port}"
            assert ("scoped.proofline.invalid", "proofline-dns") in lookups
            assert scoped_connections == ["fe80::1%41", "fe80::1%42"]
            with pytest.raises(httpx2.TransportError) as raised:
                client.get(f"http://missing.proofline.invalid:{port}/finding")
            assert not isinstance(raised.value, httpx2.TimeoutException)
            with pytest.raises(httpx2.TransportError):
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
@pytest.mark.parametrize("size", [131_072, 131_073, 150_000, 8 * 1024 * 1024 + 1])
async def test_csv_export_preserves_large_cells(mode: str, size: int) -> None:
    claim = 'é, "quoted"\r\n' + "x" * size
    row = {
        "dataset_version": "1",
        "organization_id": str(ORG),
        "repository_id": str(REPOSITORY),
        "review_id": str(REVIEW),
        "assessment_id": str(ASSESSMENT),
        "environment_id": str(ORG),
        "finding_id": str(FINDING),
        "claim": claim,
        "impact": "Synthetic consequence",
        "risk_domain": "SECURITY",
        "severity": "HIGH",
        "lifecycle_state": "OPEN",
        "created_at": "2026-11-16T00:00:00Z",
        "evidence_refs": "[]",
    }
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(row)
    text = stream.getvalue()
    with Server(
        lambda request, index: Reply(
            body=text.encode(),
            headers={
                "Content-Type": "text/csv",
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-11-16T00:00:00Z",
                "X-Proofline-Export-Next-Cursor": "opaque/+cursor",
            },
        )
    ) as server:
        async with session(mode, server.url) as client:
            kwargs = {"from_time": "2026-11-01T00:00:00Z", "to_time": "2026-11-15T00:00:00Z"}
            if size > 8 * 1024 * 1024:
                with pytest.raises(ProoflineError) as caught:
                    await call(client, "export_reviews", ORG, "findings", format="csv", **kwargs)
                assert caught.value.type == "urn:proofline:sdk:invalid-response"
            else:
                page = await call(client, "export_reviews", ORG, "findings", format="csv", **kwargs)
                assert page.rows == [row]
                assert page.text == text
                assert page.version == 1
                assert page.settled_until == "2026-11-16T00:00:00Z"
                assert page.next_cursor == "opaque/+cursor"
        assert len(server.requests) == 1


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
                b'dataset_version,claim\r\n2,"comma, quote "" and\nnewline"\r\n'
                if is_csv
                else b'{"dataset_version":2,"claim":"hello"}\n'
            ),
            headers={
                "Content-Type": "text/csv" if is_csv else "application/x-ndjson",
                "X-Proofline-Export-Version": "2",
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
            assert exported.rows[0]["dataset_version"] == 2
            assert exported.version == 2
            assert "cursor=opaque%2F%2Bcursor" in server.requests[1].path
            with pytest.raises(ProoflineError) as caught:
                await call(client, "export_reviews", ORG, "findings", cursor="refused", **kwargs)
            assert caught.value.status == 404


async def next_export(iterator: Any) -> Any:
    return await anext(iterator) if hasattr(iterator, "__anext__") else next(iterator)


@MODES
@pytest.mark.parametrize("format", ["csv", "ndjson"])
async def test_export_iterator_preserves_filters_and_streams_empty_pages(
    mode: str, format: str
) -> None:
    def respond(request: Request, index: int) -> Reply:
        assert request.path.startswith(f"/api/v1/organizations/{ORG}/exports/finding_outcomes?")
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        query = parse_qs(urlsplit(request.path).query)
        assert query == {
            "from": ["2026-10-01T00:00:00Z"],
            "to": ["2026-10-25T00:00:00Z"],
            "format": [format],
            "group_by": ["repository"],
            "cursor": ["resume/+cursor" if index == 0 else "next/+cursor"],
        }
        headers = {
            "Content-Type": "text/csv" if format == "csv" else "application/x-ndjson",
            "X-Proofline-Export-Version": "1",
            "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
        }
        if index == 0:
            headers["X-Proofline-Export-Next-Cursor"] = "next/+cursor"
        body = (
            (
                b"dataset_version,claim\r\n"
                if index == 0
                else b"dataset_version,claim\r\n1,hello\r\n"
            )
            if format == "csv"
            else (b"" if index == 0 else b'{"dataset_version":1,"claim":"hello"}\n')
        )
        return Reply(body=body, headers=headers)

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_export_pages(
                ORG,
                "finding_outcomes",
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
                format=format,
                cursor="resume/+cursor",
                group_by="repository",
                max_pages=2,
            )
            assert not server.requests
            first = await next_export(iterator)
            assert first.rows == []
            assert first.next_cursor == "next/+cursor"
            assert first.version == 1
            assert first.settled_until == "2026-10-25T00:00:00Z"
            assert len(server.requests) == 1
            second = await next_export(iterator)
            assert second.rows[0]["claim"] == "hello"
            assert second.next_cursor is None
            assert second.text.endswith("\n")
            if mode == "sync":
                with pytest.raises(StopIteration):
                    next(iterator)
            else:
                with pytest.raises(StopAsyncIteration):
                    await anext(iterator)
        assert len(server.requests) == 2


@MODES
@pytest.mark.parametrize("failure", ["empty", "repeat", "resume", "cycle", "bound", "refused"])
async def test_export_iterator_refuses_invalid_continuations_and_bounds(
    mode: str, failure: str
) -> None:
    def respond(request: Request, index: int) -> Reply:
        if failure == "refused":
            return Reply(status=404, body={"detail": "not found"})
        cursor = {
            "empty": "",
            "repeat": "next",
            "resume": "initial",
            "cycle": "a" if index % 2 == 0 else "b",
            "bound": str(index),
        }[failure]
        return Reply(
            body=b'{"dataset_version":1}\n',
            headers={
                "Content-Type": "application/x-ndjson",
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
                "X-Proofline-Export-Next-Cursor": cursor,
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_export_pages(
                ORG,
                "reviews",
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
                max_pages=3,
                cursor="initial" if failure == "resume" else None,
            )
            with pytest.raises(ProoflineError) as raised:
                for _ in range(4):
                    await next_export(iterator)
            if failure == "refused":
                assert raised.value.status == 404
            else:
                suffix = "pagination-limit" if failure == "bound" else "invalid-pagination"
                assert raised.value.type == f"urn:proofline:sdk:{suffix}"
        expected_requests = {
            "empty": 1,
            "repeat": 2,
            "resume": 1,
            "cycle": 3,
            "bound": 3,
            "refused": 1,
        }
        assert len(server.requests) == expected_requests[failure]


@MODES
@pytest.mark.parametrize("bound", [0, -1, 1001, True, 1.5])
async def test_export_iterator_validates_bound_before_requests(mode: str, bound: Any) -> None:
    with Server(lambda request, index: Reply(body={})) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_export_pages(
                ORG,
                "reviews",
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
                max_pages=bound,
            )
            with pytest.raises(ValueError, match="max_pages"):
                await next_export(iterator)
        assert not server.requests


@MODES
@pytest.mark.parametrize(
    ("cursors", "resume", "yielded"),
    [
        ([""], None, 0),
        (["initial"], "initial", 0),
        (["a", "a"], None, 1),
        (["a", "b", "a"], None, 2),
    ],
    ids=["empty", "resume", "repeat", "cycle"],
)
async def test_export_iterator_never_yields_the_page_with_an_invalid_cursor(
    mode: str, cursors: list[str], resume: str | None, yielded: int
) -> None:
    def respond(request: Request, index: int) -> Reply:
        return Reply(
            body=f'{{"dataset_version":1,"page":{index}}}\n'.encode(),
            headers={
                "Content-Type": "application/x-ndjson",
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
                "X-Proofline-Export-Next-Cursor": cursors[index],
            },
        )

    pages: list[Any] = []
    with Server(respond) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_export_pages(
                ORG,
                "reviews",
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
                cursor=resume,
            )
            with pytest.raises(ProoflineError) as raised:
                while True:
                    pages.append(await next_export(iterator))
        assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
        assert [page.rows[0]["page"] for page in pages] == list(range(yielded))
        assert len(server.requests) == yielded + 1


@MODES
@pytest.mark.parametrize(
    ("format", "content_type"),
    [
        ("csv", "Text/CSV; charset=utf-8"),
        ("ndjson", "Application/X-NDJSON; charset=utf-8"),
    ],
)
async def test_export_accepts_case_insensitive_content_type(
    mode: str, format: str, content_type: str
) -> None:
    def respond(request: Request, index: int) -> Reply:
        body = (
            b"dataset_version,claim\n1,hello\n"
            if format == "csv"
            else b'{"dataset_version":1,"claim":"hello"}\n'
        )
        return Reply(
            body=body,
            headers={
                "Content-Type": content_type,
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            page = await call(
                client,
                "export_reviews",
                ORG,
                "findings",
                format=format,
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
            )
            assert page.rows[0]["claim"] == "hello"


@MODES
async def test_export_versions_follow_the_dataset(mode: str) -> None:
    served = {
        "findings": [("1", 1), ("2", 2), ("2", 1), ("3", 3)],
        "finding_validations": [("2", 2)],
        "reviews": [("1", 1), ("2", 2)],
    }

    seen: dict[str, int] = {}

    def respond(request: Request, index: int) -> Reply:
        dataset = urlsplit(request.path).path.rsplit("/", 1)[1]
        seen[dataset] = seen.get(dataset, 0) + 1
        header, row = served[dataset][seen[dataset] - 1]
        return Reply(
            body=json.dumps({"dataset_version": row}).encode() + b"\n",
            headers={
                "Content-Type": "application/x-ndjson",
                "X-Proofline-Export-Version": header,
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            kwargs = {"from_time": "2026-10-01T00:00:00Z", "to_time": "2026-10-25T00:00:00Z"}
            outcomes = []
            for dataset, replies in served.items():
                for _ in replies:
                    try:
                        page = await call(client, "export_reviews", ORG, dataset, **kwargs)
                        outcomes.append((dataset, page.version))
                    except ProoflineError as error:
                        outcomes.append((dataset, error.type))
            refused = "urn:proofline:sdk:invalid-response"
            assert outcomes == [
                ("findings", 1),
                ("findings", 2),
                ("findings", refused),
                ("findings", refused),
                ("finding_validations", 2),
                ("reviews", 1),
                ("reviews", refused),
            ]


@MODES
@pytest.mark.parametrize("format", ["csv", "ndjson"])
async def test_review_export_retains_every_recorded_kind(mode: str, format: str) -> None:
    kinds = [
        "PULL_REQUEST",
        "DEPLOYMENT",
        "PATCH",
        "COMMIT",
        "FILES",
        "MERGE_GROUP",
        "REVISION_SCAN",
    ]
    rows = [
        {
            "dataset_version": 1,
            "kind": kind,
            "created_at": "2026-10-24T00:00:00Z",
            "organization_id": str(ORG),
            "review_id": "00000000-0000-7000-8000-000000000002",
            "status": "COMPLETED",
            "trigger_origin": "AUTOMATIC",
        }
        for kind in kinds
    ]

    def respond(request: Request, index: int) -> Reply:
        assert request.path.startswith(f"/api/v1/organizations/{ORG}/exports/reviews?")
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        return Reply(
            body=(
                (
                    ",".join(rows[0])
                    + "\r\n"
                    + "".join(",".join(map(str, row.values())) + "\r\n" for row in rows)
                ).encode()
                if format == "csv"
                else ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
            ),
            headers={
                "Content-Type": "text/csv" if format == "csv" else "application/x-ndjson",
                "X-Proofline-Export-Version": "1",
                "X-Proofline-Export-Settled-Until": "2026-10-25T00:00:00Z",
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            page = await call(
                client,
                "export_reviews",
                ORG,
                "reviews",
                format=format,
                from_time="2026-10-01T00:00:00Z",
                to_time="2026-10-25T00:00:00Z",
            )
            assert [row["kind"] for row in page.rows] == kinds
            # The generated wire enum must accept the same retained spellings.
            assert [ExportReviewKind(row["kind"]).value for row in page.rows] == kinds
            if format == "ndjson":
                assert [ReviewsExportRow.from_dict(row).kind.value for row in page.rows] == kinds
            assert page.next_cursor is None


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


@MODES
async def test_wait_for_review_invokes_on_poll_callback(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    calls: list[tuple[str, int]] = []
    responses = [review("RUNNING"), review()]

    with Server(lambda request, index: Reply(body=responses[index])) as server:

        def sync_poll_callback(review_detail: Any) -> None:
            calls.append((f"sync:{review_detail.status}", len(server.requests)))
            if review_detail.status == "RUNNING":
                assert review_detail.completed_at is UNSET

        async def async_poll_callback(review_detail: Any) -> None:
            calls.append((f"async:{review_detail.status}", len(server.requests)))
            if review_detail.status == "RUNNING":
                assert review_detail.completed_at is UNSET
            review_detail.status = "MUTATED"

        async with session(mode, server.url) as client:
            cb = async_poll_callback if mode == "async" else sync_poll_callback
            result = await call(
                client,
                "wait_for_review",
                ORG,
                REVIEW,
                timeout=100,
                on_poll=cb,
            )
            assert (result.status, result.gaps, result.reason) == ("COMPLETED", (), None)
            prefix = "async" if mode == "async" else "sync"
            assert calls == [(f"{prefix}:RUNNING", 1), (f"{prefix}:COMPLETED", 2)]
            assert result.review.status == "COMPLETED"
        assert len(server.requests) == 2
        assert clock.delays == [5]

    # Assert async client also works with regular synchronous callbacks returning None
    if mode == "async":
        with Server(lambda request, index: Reply(body=responses[index])) as server:
            sync_calls: list[tuple[str, int]] = []

            def inline_sync_cb(r: Any) -> None:
                sync_calls.append((r.status, len(server.requests)))
                r.status = "MUTATED"
                r.actions.publish = True
                r.additional_properties["mutated"] = "mutated_value"
                assert len(r.assessments) > 0
                assert r.assessments[0].checks.receipt_recorded is True
                r.assessments[0].checks.receipt_recorded = False

            async with session("async", server.url) as client:
                result = await call(
                    client,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    timeout=100,
                    on_poll=inline_sync_cb,
                )
                assert result.status == "COMPLETED"
                assert sync_calls == [("RUNNING", 1), ("COMPLETED", 2)]
                assert result.review.status == "COMPLETED"
                assert result.review.actions.publish is False
                assert "mutated" not in result.review.additional_properties
                assert result.review.assessments[0].checks.receipt_recorded is True

        # Assert callback TimeoutError before deadline propagates
        async def failing_callback(r: Any) -> None:
            raise TimeoutError("callback failure")

        with Server(lambda request, index: Reply(body=review("RUNNING"))) as server:
            async with session("async", server.url) as client:
                with pytest.raises(TimeoutError, match="callback failure"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10,
                        on_poll=failing_callback,
                    )

        # Assert already-done failed future propagates inline
        failed_inline_futs: list[asyncio.Future[None]] = []

        def failed_future_callback(r: Any) -> asyncio.Future[None]:
            loop = asyncio.get_running_loop()
            fut: asyncio.Future[None] = loop.create_future()
            fut.set_exception(ValueError("inline future error"))
            failed_inline_futs.append(fut)
            return fut

        try:
            with Server(lambda request, index: Reply(body=review("RUNNING"))) as server:
                async with session("async", server.url) as client:
                    with pytest.raises(ValueError, match="inline future error"):
                        await client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=10,
                            on_poll=failed_future_callback,
                        )
        finally:
            for ff in failed_inline_futs:
                try:
                    if not ff.cancelled():
                        ff.exception()
                except BaseException:
                    pass

        # Run the watchdog cases in a subprocess with a hard timeout so cancellation-resistant
        # tasks cannot stall teardown.
        watchdog_code = """
import asyncio
import pytest
import time
import weakref
from typing import Any
from proofline import AsyncProoflineClient
import proofline.client as client_module
import proofline._transport as transport_module
from proofline._generated.models.customer_review_detail import CustomerReviewDetail
from tests.test_http import review, ORG, REVIEW, Server, Reply

class ControlledClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def time(self) -> float:
        return self.now

    def advance(self, dt: float) -> None:
        self.now += dt

async def main() -> None:
    clock = ControlledClock()
    client_module.monotonic = clock.time
    transport_module.monotonic = clock.time

    sleep_forbidden = False
    orig_async_sleep = client_module.async_sleep

    async def guarded_async_sleep(delay: float) -> None:
        if sleep_forbidden:
            raise AssertionError(
                "Ordinary polling sleep occurred before watchdog advanced callback deadline"
            )
        await orig_async_sleep(delay)

    client_module.async_sleep = guarded_async_sleep

    running_detail = CustomerReviewDetail.from_dict(review("RUNNING"))
    completed_detail = CustomerReviewDetail.from_dict(review())

    async def fake_running(org: Any, rev: Any) -> Any:
        return running_detail

    async def fake_completed(org: Any, rev: Any) -> Any:
        return completed_detail

    async with AsyncProoflineClient(
        token="test_token", base_url="https://api.proofline.sh"
    ) as client:
        # Case 1: Pending same-loop Future that times out is detached without cancelling
        # Assert it is still pending before advancing the controlled deadline
        class SignallingFuture(asyncio.Future[None]):
            def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
                super().__init__(loop=loop)
                self.wait_entered = asyncio.Event()

            def add_done_callback(self, fn: Any, *, context: Any = None) -> None:
                super().add_done_callback(fn, context=context)
                self.wait_entered.set()

        pending_fut: SignallingFuture | None = None
        cb_1_started = asyncio.Event()

        def pending_future_callback(r: Any) -> SignallingFuture:
            nonlocal pending_fut
            loop = asyncio.get_running_loop()
            pending_fut = SignallingFuture(loop=loop)
            cb_1_started.set()
            return pending_fut

        client.get_review = fake_running  # type: ignore

        waiter_task_1 = asyncio.create_task(
            client.wait_for_review(
                ORG,
                REVIEW,
                timeout=0.2,
                on_poll=pending_future_callback,
            )
        )
        await cb_1_started.wait()
        assert pending_fut is not None
        await pending_fut.wait_entered.wait()
        assert not waiter_task_1.done()
        assert id(pending_fut) not in client_module._DETACHED_FUTURES
        clock.advance(1.0)
        res_1 = await waiter_task_1
        assert res_1.status == "TIMED_OUT"
        assert not pending_fut.cancelled()
        assert not pending_fut.done()
        assert id(pending_fut) in client_module._DETACHED_FUTURES
        pending_fut.set_result(None)
        await asyncio.sleep(0)
        assert id(pending_fut) not in client_module._DETACHED_FUTURES

        # Case 2: Pending same-loop Future that completes within budget without cancellation
        completed_fut = asyncio.get_running_loop().create_future()
        complete_fut_task: asyncio.Task[None] | None = None

        async def complete_fut_soon() -> None:
            await asyncio.sleep(0.01)
            completed_fut.set_result(None)

        def completing_future_callback(r: Any) -> asyncio.Future[None]:
            nonlocal complete_fut_task
            complete_fut_task = asyncio.create_task(complete_fut_soon())
            return completed_fut

        client.get_review = fake_completed  # type: ignore

        try:
            res = await client.wait_for_review(
                ORG,
                REVIEW,
                timeout=10.0,
                on_poll=completing_future_callback,
            )
            assert res.status == "COMPLETED"
            assert completed_fut.done()
            assert not completed_fut.cancelled()
        finally:
            if complete_fut_task is not None:
                if not complete_fut_task.done():
                    complete_fut_task.cancel()
                try:
                    await complete_fut_task
                except BaseException:
                    pass
            try:
                if not completed_fut.done():
                    completed_fut.cancel()
                elif not completed_fut.cancelled():
                    completed_fut.exception()
            except BaseException:
                pass

        # Case 3: Overdue callback continues running without cancellation on non-terminal review
        callback_running = asyncio.Event()
        callback_finished = asyncio.Event()
        release_callback = asyncio.Event()
        cb_task_3: asyncio.Task[Any] | None = None
        orig_create_task_3 = client_module.async_create_task

        def tracking_create_task_3(coro_arg: Any, **kwargs: Any) -> asyncio.Task[Any]:
            nonlocal cb_task_3
            t = orig_create_task_3(coro_arg, **kwargs)
            cb_task_3 = t
            return t

        client_module.async_create_task = tracking_create_task_3

        async def continuing_coro(r: Any) -> None:
            callback_running.set()
            await release_callback.wait()
            callback_finished.set()

        client.get_review = fake_running  # type: ignore

        sleep_forbidden = True
        try:
            waiter_task_3 = asyncio.create_task(
                client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=0.2,
                    on_poll=continuing_coro,
                )
            )
            await callback_running.wait()
            assert not waiter_task_3.done()
            clock.advance(1.0)
            res_3 = await waiter_task_3
            assert res_3.status == "TIMED_OUT"
            assert callback_running.is_set()
            assert not callback_finished.is_set()
            release_callback.set()
            await callback_finished.wait()
        finally:
            client_module.async_create_task = orig_create_task_3
            sleep_forbidden = False
            release_callback.set()
            if cb_task_3 is not None:
                if not cb_task_3.done():
                    cb_task_3.cancel()
                try:
                    await cb_task_3
                except (asyncio.CancelledError, BaseException):
                    pass

        # Case 3b: Return a Task from a synchronous callback, release it after the polling deadline
        # and waiter exit, and assert its client request succeeds against the local test server.
        task_worker_started = asyncio.Event()
        task_release_3b = asyncio.Event()
        task_success_3b = asyncio.Event()
        cb_task_3b: asyncio.Task[None] | None = None

        with Server(lambda request, index: Reply(body=review("RUNNING"))) as test_server:
            async with AsyncProoflineClient(
                token="test_token", base_url=test_server.url
            ) as real_client:
                async def task_worker_3b() -> None:
                    task_worker_started.set()
                    await task_release_3b.wait()
                    # Real SDK request against the local test server checking deadline:
                    rev_res = await real_client.get_review(ORG, REVIEW)
                    assert rev_res.status == "RUNNING"
                    task_success_3b.set()

                def sync_cb_returning_task(r: Any) -> Any:
                    nonlocal cb_task_3b
                    cb_task_3b = asyncio.create_task(task_worker_3b())
                    return cb_task_3b

                waiter_task_3b = asyncio.create_task(
                    real_client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=0.2,
                        on_poll=sync_cb_returning_task,
                    )
                )
                startup_waiter = asyncio.create_task(task_worker_started.wait())
                try:
                    done, _ = await asyncio.wait(
                        {startup_waiter, waiter_task_3b},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    if waiter_task_3b in done:
                        await waiter_task_3b
                    assert cb_task_3b is not None
                    assert not cb_task_3b.done()
                    clock.advance(1.0)
                    res_3b = await waiter_task_3b
                    assert res_3b.status == "TIMED_OUT"
                    assert not cb_task_3b.done()
                    task_release_3b.set()
                    await asyncio.wait_for(asyncio.shield(cb_task_3b), timeout=1.0)
                finally:
                    if not startup_waiter.done():
                        startup_waiter.cancel()
                    try:
                        await startup_waiter
                    except (asyncio.CancelledError, BaseException):
                        pass
                    if not waiter_task_3b.done():
                        waiter_task_3b.cancel()
                    try:
                        await waiter_task_3b
                    except (asyncio.CancelledError, BaseException):
                        pass
                    if cb_task_3b is not None:
                        if not cb_task_3b.done():
                            cb_task_3b.cancel()
                        try:
                            await cb_task_3b
                        except (asyncio.CancelledError, BaseException):
                            pass

        # Case 4: Overdue callback continues running without cancellation on terminal review
        orig_create_task_4 = client_module.async_create_task
        captured_case4_wrappers: list[Any] = []

        def tracked_create_task_4(coro: Any, *args: Any, **kwargs: Any) -> Any:
            t = orig_create_task_4(coro, *args, **kwargs)
            t.exception_calls = 0
            orig_exc = t.exception

            def tracked_exc() -> Any:
                t.exception_calls += 1
                return orig_exc()

            t.exception = tracked_exc
            captured_case4_wrappers.append(t)
            return t

        client_module.async_create_task = tracked_create_task_4

        callback_running_term = asyncio.Event()
        callback_finished_term = asyncio.Event()
        release_callback_term = asyncio.Event()

        async def continuing_coro_term(r: Any) -> None:
            callback_running_term.set()
            await release_callback_term.wait()
            callback_finished_term.set()
            raise RuntimeError("overdue coroutine failure")

        client.get_review = fake_completed  # type: ignore

        try:
            waiter_task_4 = asyncio.create_task(
                client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=0.2,
                    on_poll=continuing_coro_term,
                )
            )
            await callback_running_term.wait()
            assert not waiter_task_4.done()
            clock.advance(1.0)
            res_4 = await waiter_task_4
            assert res_4.status == "COMPLETED"
            assert callback_running_term.is_set()
            assert not callback_finished_term.is_set()
            release_callback_term.set()
            await callback_finished_term.wait()
            await asyncio.sleep(0.01)
            assert len(captured_case4_wrappers) == 1
            wrapper_4 = captured_case4_wrappers[0]
            assert wrapper_4.done()
            assert not wrapper_4.cancelled()
            assert getattr(wrapper_4, "exception_calls", 0) > 0
        finally:
            client_module.async_create_task = orig_create_task_4
            for w in captured_case4_wrappers:
                if not w.done():
                    w.cancel()
                try:
                    await w
                except (asyncio.CancelledError, BaseException):
                    pass

        # Case 5: Suspending callback that succeeds within budget
        resumed_within_budget = False

        async def suspending_callback(r: Any) -> None:
            nonlocal resumed_within_budget
            await asyncio.sleep(0.01)
            resumed_within_budget = True

        client.get_review = fake_completed  # type: ignore

        res = await client.wait_for_review(
            ORG,
            REVIEW,
            timeout=10.0,
            on_poll=suspending_callback,
        )
        assert res.status == "COMPLETED"
        assert resumed_within_budget

        # Case 6: Overdue callback failure is observed without leaking to loop handler
        unhandled_exceptions: list[dict[str, Any]] = []
        loop = asyncio.get_running_loop()
        old_handler = loop.get_exception_handler()
        loop.set_exception_handler(lambda _loop, ctx: unhandled_exceptions.append(ctx))
        coro_trigger: asyncio.Event | None = None
        waiter_coro_task: asyncio.Task[Any] | None = None
        failing_fut: asyncio.Future[None] | None = None
        orig_create_task_6: Any = None
        captured_case6_wrappers: list[asyncio.Task[Any]] = []
        try:
            # 6a: Future callback cancelled after startup
            failing_fut = loop.create_future()
            future_started = asyncio.Event()

            def failing_future_cb(r: Any) -> asyncio.Future[None]:
                future_started.set()
                assert failing_fut is not None
                return failing_fut

            client.get_review = fake_running  # type: ignore
            waiter_fut_task = asyncio.create_task(
                client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=10.0,
                    on_poll=failing_future_cb,
                )
            )
            await future_started.wait()
            waiter_fut_task.cancel()
            cancelled_fut = False
            try:
                await waiter_fut_task
            except asyncio.CancelledError:
                cancelled_fut = True
            assert cancelled_fut

            assert id(failing_fut) in client_module._DETACHED_FUTURES
            failing_fut.set_exception(RuntimeError("error in cancelled future callback"))
            await asyncio.sleep(0)
            assert id(failing_fut) not in client_module._DETACHED_FUTURES
            failing_fut = None
            import gc

            gc.collect()
            assert unhandled_exceptions == []

            # 6b: Pre-start wrapper cancellation: hold wrapper before entry,
            # cancel waiter with budget remaining, run queued runner and
            # assert callback body never starts
            import inspect

            hold_wrapper = asyncio.Event()
            wrapper_tasks: list[asyncio.Task[Any]] = []
            orig_create_task = client_module.async_create_task

            runner_executed = False

            def holding_create_task(coro_arg: Any, **kwargs: Any) -> asyncio.Task[Any]:
                async def held_wrapper() -> Any:
                    nonlocal runner_executed
                    try:
                        await hold_wrapper.wait()
                        runner_executed = True
                        return await coro_arg
                    except asyncio.CancelledError:
                        if hasattr(coro_arg, "close"):
                            coro_arg.close()
                        raise

                t = orig_create_task(held_wrapper(), **kwargs)
                wrapper_tasks.append(t)
                return t

            client_module.async_create_task = holding_create_task

            user_coro_created: list[Any] = []
            cb_body_started = False

            async def dummy_pre_start_coro(r: Any) -> None:
                nonlocal cb_body_started
                cb_body_started = True

            def pre_start_cb(r: Any) -> Any:
                c = dummy_pre_start_coro(r)
                user_coro_created.append(c)
                return c

            pre_waiter_task: asyncio.Task[Any] | None = None
            try:
                pre_waiter_task = asyncio.create_task(
                    client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10.0,
                        on_poll=pre_start_cb,
                    )
                )
                await asyncio.sleep(0)
                if pre_waiter_task.done():
                    await pre_waiter_task
                assert len(wrapper_tasks) == 1
                assert not wrapper_tasks[0].done()

                # Queue the wrapper before cancelling the waiter in the same loop turn:
                hold_wrapper.set()
                pre_waiter_task.cancel()
                await asyncio.sleep(0)

                assert runner_executed is True

                assert not cb_body_started
                assert len(user_coro_created) == 1
                assert inspect.getcoroutinestate(user_coro_created[0]) == inspect.CORO_CLOSED
                assert wrapper_tasks[0].done()

                with pytest.raises(asyncio.CancelledError):
                    await pre_waiter_task
            finally:
                client_module.async_create_task = orig_create_task
                if pre_waiter_task is not None:
                    if not pre_waiter_task.done():
                        pre_waiter_task.cancel()
                    try:
                        await pre_waiter_task
                    except (asyncio.CancelledError, BaseException):
                        pass
                for wt in wrapper_tasks:
                    if not wt.done():
                        wt.cancel()
                    try:
                        await wt
                    except (asyncio.CancelledError, BaseException):
                        pass
                for c in user_coro_created:
                    try:
                        if (
                            inspect.iscoroutine(c)
                            and inspect.getcoroutinestate(c) == inspect.CORO_CREATED
                        ):
                            c.close()
                    except BaseException:
                        pass

            # Coroutine callback cancelled after startup
            coro_started = asyncio.Event()
            coro_trigger = asyncio.Event()
            about_to_raise = asyncio.Event()
            captured_case6_wrappers.clear()
            orig_create_task_6 = client_module.async_create_task

            def tracked_create_task_6(coro: Any, *args: Any, **kwargs: Any) -> Any:
                t = orig_create_task_6(coro, *args, **kwargs)
                t.exception_calls = 0
                orig_exc = t.exception

                def tracked_exc() -> Any:
                    t.exception_calls += 1
                    return orig_exc()

                t.exception = tracked_exc
                captured_case6_wrappers.append(t)
                return t

            client_module.async_create_task = tracked_create_task_6

            async def failing_overdue_coro(r: Any) -> None:
                coro_started.set()
                await coro_trigger.wait()
                about_to_raise.set()
                raise RuntimeError("error in overdue callback")

            waiter_coro_task = asyncio.create_task(
                client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=10.0,
                    on_poll=failing_overdue_coro,
                )
            )
            await coro_started.wait()
            waiter_coro_task.cancel()
            cancelled_coro = False
            try:
                await waiter_coro_task
            except asyncio.CancelledError:
                cancelled_coro = True
            assert cancelled_coro

            assert len(client_module._DETACHED_TASKS) == 1
            detached_task_id = next(iter(client_module._DETACHED_TASKS.keys()))
            detached_task = client_module._DETACHED_TASKS[detached_task_id]

            coro_trigger.set()
            await asyncio.wait_for(about_to_raise.wait(), timeout=1.0)
            await asyncio.sleep(0.01)

            assert detached_task_id not in client_module._DETACHED_TASKS
            assert detached_task.done()
            assert not detached_task.cancelled()
            assert getattr(detached_task, "exception_calls", 0) > 0
            # import weakref (already imported at module level)

            dt_ref = weakref.ref(detached_task)
            del detached_task
            captured_case6_wrappers.clear()
            gc.collect()
            assert dt_ref() is None
            assert unhandled_exceptions == []
        finally:
            if orig_create_task_6 is not None:
                client_module.async_create_task = orig_create_task_6
            if failing_fut is not None:
                if not failing_fut.done():
                    failing_fut.cancel()
                elif not failing_fut.cancelled():
                    try:
                        failing_fut.exception()
                    except BaseException:
                        pass
            if coro_trigger is not None:
                coro_trigger.set()
            if waiter_coro_task is not None:
                if not waiter_coro_task.done():
                    waiter_coro_task.cancel()
                try:
                    await waiter_coro_task
                except (asyncio.CancelledError, BaseException):
                    pass
            for t in captured_case6_wrappers:
                if hasattr(t, "done") and not t.done():
                    t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, BaseException):
                    pass
            for t in list(client_module._DETACHED_TASKS.values()):
                if hasattr(t, "done") and not t.done():
                    t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, BaseException):
                    pass
            await asyncio.sleep(0.01)
            loop.set_exception_handler(old_handler)

        # Case 7: Overdue callback awaiting the polling task is not cancelled
        polling_waiter_task: asyncio.Task[Any] | None = None
        callback_completed_7 = asyncio.Event()
        cb_7_started = asyncio.Event()

        async def awaiting_runner_callback(r: Any) -> None:
            cb_7_started.set()
            assert polling_waiter_task is not None
            outcome_inner = await polling_waiter_task
            assert outcome_inner.status == "TIMED_OUT"
            callback_completed_7.set()

        client.get_review = fake_running  # type: ignore
        sleep_forbidden = True
        try:
            polling_waiter_task = asyncio.create_task(
                client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=0.2,
                    on_poll=awaiting_runner_callback,
                )
            )
            await cb_7_started.wait()
            assert not polling_waiter_task.done()
            clock.advance(1.0)
            res_7 = await polling_waiter_task
            assert res_7.status == "TIMED_OUT"
            await asyncio.wait_for(callback_completed_7.wait(), timeout=1.0)
        finally:
            sleep_forbidden = False

asyncio.run(main())
"""
        checkout_root = Path(__file__).resolve().parent.parent
        subprocess.run(
            [sys.executable, "-c", watchdog_code],
            cwd=str(checkout_root),
            check=True,
            timeout=10,
        )

    # Assert callback modifying review does not mutate returned review in both sync and async
    mutated_count = 0

    def sync_mutating_callback(r: Any) -> None:
        nonlocal mutated_count
        mutated_count += 1
        r.status = "MUTATED"
        r.actions.publish = True
        r.additional_properties["mutated"] = "mutated_value"
        assert len(r.assessments) > 0
        assert r.assessments[0].checks.receipt_recorded is True
        r.assessments[0].checks.receipt_recorded = False

    async def async_mutating_callback(r: Any) -> None:
        nonlocal mutated_count
        mutated_count += 1
        r.status = "MUTATED"
        r.actions.publish = True
        r.additional_properties["mutated"] = "mutated_value"
        assert len(r.assessments) > 0
        assert r.assessments[0].checks.receipt_recorded is True
        r.assessments[0].checks.receipt_recorded = False

    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session(mode, server.url) as client:
            mut_cb = async_mutating_callback if mode == "async" else sync_mutating_callback
            res = await call(
                client,
                "wait_for_review",
                ORG,
                REVIEW,
                timeout=10,
                on_poll=mut_cb,
            )
            assert mutated_count == 1
            assert res.review.status != "MUTATED"
            assert res.review.actions.publish is False
            assert "mutated" not in res.review.additional_properties
            assert res.review.assessments[0].checks.receipt_recorded is True

    # Test snapshot directly with an in-memory deep extension and custom tuple to bypass HTTP JSON
    deep_container: dict[str, Any] = {}
    curr = deep_container
    for _ in range(3000):
        curr["child"] = {}
        curr = curr["child"]
    curr["val"] = "deepest"

    detail = CustomerReviewDetail.from_dict(responses[1])
    detail.additional_properties["deep"] = deep_container
    detail.additional_properties["custom_tuple"] = ({"nested": "val"}, None, 42)
    detail.additional_properties["none_frozenset_tuple"] = (None, frozenset({1}))

    from proofline.client import _snapshot_review

    snap = _snapshot_review(detail)
    assert snap is not None
    assert snap is not detail
    assert snap.additional_properties is not detail.additional_properties

    # Walk all 3,000 levels, assert the leaf value, and verify mutation leaves original unchanged
    walk_snap = snap.additional_properties["deep"]
    walk_orig = detail.additional_properties["deep"]
    for _ in range(3000):
        assert walk_snap is not walk_orig
        walk_snap = walk_snap["child"]
        walk_orig = walk_orig["child"]
    assert walk_snap["val"] == "deepest"
    assert walk_orig["val"] == "deepest"

    walk_snap["val"] = "mutated_leaf"
    assert walk_orig["val"] == "deepest"

    custom_t = snap.additional_properties["custom_tuple"]
    orig_t = detail.additional_properties["custom_tuple"]
    assert isinstance(custom_t, tuple)
    assert custom_t[0] is not orig_t[0]
    assert custom_t[0]["nested"] == "val"
    assert custom_t[1] is None
    assert custom_t[2] == 42
    custom_t[0]["nested"] = "mutated_nested"
    assert orig_t[0]["nested"] == "val"

    assert "none_frozenset_tuple" in snap.additional_properties
    nft = snap.additional_properties["none_frozenset_tuple"]
    assert isinstance(nft, tuple)
    assert len(nft) == 2
    assert nft[0] is None
    assert nft[1] == frozenset({1})

    # Tuple with deeply nested list must snapshot iteratively without RecursionError
    deep_nested_list: Any = "leaf"
    for _ in range(3000):
        deep_nested_list = [deep_nested_list]
    detail.additional_properties["tuple_with_deep_list"] = (deep_nested_list, 999)
    snap_nested = _snapshot_review(detail)
    assert snap_nested is not None
    assert isinstance(snap_nested.additional_properties["tuple_with_deep_list"], tuple)
    orig_l = detail.additional_properties["tuple_with_deep_list"][0]
    curr_l = snap_nested.additional_properties["tuple_with_deep_list"][0]
    for _ in range(3000):
        assert curr_l is not orig_l
        curr_l = curr_l[0]
        orig_l = orig_l[0]
    assert curr_l == "leaf"
    assert orig_l == "leaf"

    # Assert pending future on closed loop or foreign loop raises ValueError
    if mode == "async":
        other_loop = asyncio.new_event_loop()
        closed_fut = other_loop.create_future()
        other_loop.close()

        with Server(lambda request, index: Reply(body=responses[1])) as server:
            async with session("async", server.url) as client:
                with pytest.raises(ValueError, match="running event loop"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10,
                        on_poll=lambda r: closed_fut,
                    )
        assert not closed_fut.done()

        foreign_loop = asyncio.new_event_loop()
        foreign_fut = foreign_loop.create_future()
        try:

            def foreign_cb_expired(r: Any) -> Any:
                clock.now += 200.0
                return foreign_fut

            with Server(lambda request, index: Reply(body=responses[1])) as server:
                async with session("async", server.url) as client:
                    with pytest.raises(ValueError, match="running event loop"):
                        await client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=10,
                            on_poll=foreign_cb_expired,
                        )
            assert not foreign_fut.done()
            assert not foreign_fut.cancelled()
            assert not getattr(foreign_fut, "_callbacks", None)
        finally:
            foreign_loop.close()

        # Assert already-suspended native coroutine is rejected at callback boundary
        async def dummy_coro() -> None:
            await asyncio.sleep(0)

        suspended_coro = dummy_coro()
        try:
            try:
                suspended_coro.send(None)
            except StopIteration:
                pass

            with Server(lambda request, index: Reply(body=responses[1])) as server:
                async with session("async", server.url) as client:
                    with pytest.raises(ValueError, match="unstarted coroutines"):
                        await client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=10,
                            on_poll=lambda r: suspended_coro,
                        )
        finally:
            suspended_coro.close()

        # Started coroutine raises ValueError even after deadline expiry without closing
        async def dummy_started() -> None:
            await asyncio.sleep(10)

        started_c = dummy_started()
        task_started = asyncio.create_task(started_c)
        try:
            await asyncio.sleep(0)

            def started_coro_cb(r: Any) -> Any:
                clock.now += 100.0
                return started_c

            with Server(lambda request, index: Reply(body=responses[0])) as server:
                async with session("async", server.url) as client:
                    with pytest.raises(ValueError, match="unstarted coroutines"):
                        await client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=5.0,
                            on_poll=started_coro_cb,
                        )
                    assert inspect.getcoroutinestate(started_c) == inspect.CORO_SUSPENDED
        finally:
            task_started.cancel()
            try:
                await task_started
            except asyncio.CancelledError:
                pass

        # Non-None, non-awaitable callback return raises TypeError
        def sync_int_cb(r: Any) -> Any:
            return 42

        with Server(lambda request, index: Reply(body=responses[1])) as server:
            async with session("async", server.url) as client:
                with pytest.raises(TypeError, match="Callbacks must return None or an awaitable"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10,
                        on_poll=sync_int_cb,
                    )

        # Unrestricted awaitables returning values (e.g. int) accepted and result discarded
        int_cb_completed = False

        async def int_returning_callback(r: Any) -> int:
            nonlocal int_cb_completed
            await asyncio.sleep(0)
            int_cb_completed = True
            return 42

        with Server(lambda request, index: Reply(body=responses[1])) as server:
            async with session("async", server.url) as client:
                res_int = await client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=10,
                    on_poll=int_returning_callback,
                )
                assert res_int.status == "COMPLETED"
                assert int_cb_completed is True

        # Unhashable same-loop Future subclass completed after wait starts
        class UnhashableFuture(asyncio.Future[None]):
            __hash__ = None  # type: ignore[assignment]

            def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
                super().__init__(loop=loop)
                self.exception_calls = 0

            def exception(self) -> BaseException | None:
                self.exception_calls += 1
                return super().exception()

        complete_task: asyncio.Task[None] | None = None

        async def complete_unhashable_soon(fut: Any) -> None:
            await asyncio.sleep(0.01)
            fut.set_result(None)

        def complete_unhashable_cb(r: Any) -> Any:
            nonlocal complete_task
            complete_task = asyncio.create_task(complete_unhashable_soon(unhashable_fut))
            return unhashable_fut

        unhashable_fut: Any = UnhashableFuture(loop=asyncio.get_running_loop())
        try:
            with Server(lambda request, index: Reply(body=responses[1])) as server:
                async with session("async", server.url) as client:
                    res_unhash = await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10,
                        on_poll=complete_unhashable_cb,
                    )
                    assert res_unhash.status == "COMPLETED"
                    assert unhashable_fut.done()
        finally:
            if complete_task is not None:
                if not complete_task.done():
                    complete_task.cancel()
                try:
                    await complete_task
                except (asyncio.CancelledError, BaseException):
                    pass
            try:
                if not asyncio.Future.done(unhashable_fut):
                    unhashable_fut.cancel()
                elif not asyncio.Future.cancelled(unhashable_fut):
                    unhashable_fut.exception()
            except BaseException:
                pass

        # Cancel the waiter while an UnhashableFuture is pending, then fail and release
        # the future and assert that the loop reports no unhandled exception.
        from proofline.client import _DETACHED_FUTURES

        unhash_cancel_reports: list[dict[str, Any]] = []
        loop = asyncio.get_running_loop()
        old_h_unhash = loop.get_exception_handler()
        loop.set_exception_handler(lambda _loop, ctx: unhash_cancel_reports.append(ctx))
        try:
            with Server(lambda request, index: Reply(body=responses[0])) as server:
                async with session("async", server.url) as client:
                    unhash_box: list[Any] = [UnhashableFuture(loop=loop)]
                    cb_started = asyncio.Event()

                    def unhash_failing_cb(r: Any) -> Any:
                        cb_started.set()
                        return unhash_box[0]

                    waiter_task = asyncio.create_task(
                        client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=10,
                            on_poll=unhash_failing_cb,
                        )
                    )
                    cb_wait_task = asyncio.create_task(cb_started.wait())
                    try:
                        done_set, _ = await asyncio.wait(
                            {cb_wait_task, waiter_task},
                            timeout=5.0,
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        if waiter_task in done_set and not cb_started.is_set():
                            cb_wait_task.cancel()
                            await waiter_task
                        assert cb_wait_task in done_set, "Callback startup timed out"
                        waiter_task.cancel()
                        cancelled = False
                        try:
                            await waiter_task
                        except asyncio.CancelledError:
                            cancelled = True
                        assert cancelled
                        target_fut = unhash_box[0]
                        fut_weakref = weakref.ref(target_fut)
                        assert id(target_fut) in _DETACHED_FUTURES
                        target_fut.set_exception(RuntimeError("unhashable late failure"))
                        await asyncio.sleep(0)
                        assert id(target_fut) not in _DETACHED_FUTURES
                        assert target_fut.exception_calls > 0
                        del target_fut
                        unhash_box.clear()
                        import gc

                        gc.collect()
                        assert fut_weakref() is None
                        assert unhash_cancel_reports == []
                    finally:
                        for t in (cb_wait_task, waiter_task):
                            if not t.done():
                                t.cancel()
                            try:
                                await t
                            except (asyncio.CancelledError, BaseException):
                                pass
                        if unhash_box:
                            f = unhash_box[0]
                            if not f.done():
                                f.set_result(None)
                            elif not f.cancelled():
                                try:
                                    f.exception()
                                except BaseException:
                                    pass
                        await asyncio.sleep(0)
        finally:
            loop.set_exception_handler(old_h_unhash)

        # Case detaching an overdue callback Future without calling its cancel():
        # the waiter returns TIMED_OUT without calling cancel() or reporting an unhandled exception
        class SyncCancelRaisingFuture(asyncio.Future[None]):
            def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
                super().__init__(loop=loop)
                self.cancel_called = False
                self.exception_calls = 0

            def cancel(self, msg: Any = None) -> bool:
                self.cancel_called = True
                raise RuntimeError("synchronous cancel error")

            def exception(self) -> BaseException | None:
                self.exception_calls += 1
                return super().exception()

        cancel_reports: list[dict[str, Any]] = []
        loop = asyncio.get_running_loop()
        old_h = loop.get_exception_handler()
        loop.set_exception_handler(lambda _loop, ctx: cancel_reports.append(ctx))
        fut_sync_box: list[Any] = []
        try:
            try:
                fut_sync_cancel: Any = SyncCancelRaisingFuture(loop=asyncio.get_running_loop())
                fut_sync_box.append(fut_sync_cancel)
                clock_now = [1000.0]
                orig_client_mono = client_module.monotonic
                orig_trans_mono = _transport.monotonic
                client_module.monotonic = lambda: clock_now[0]
                _transport.monotonic = lambda: clock_now[0]

                def sync_cancel_on_poll(r: Any) -> Any:
                    clock_now[0] += 0.2
                    return fut_sync_cancel

                running_detail = CustomerReviewDetail.from_dict(review("RUNNING"))

                async def fake_sync_cancel_running(org: Any, rev: Any) -> Any:
                    return running_detail

                try:
                    async with AsyncProoflineClient(
                        token="test_token", base_url="https://api.proofline.sh"
                    ) as client:
                        client.get_review = fake_sync_cancel_running  # type: ignore
                        res_sync_cancel = await client.wait_for_review(
                            ORG,
                            REVIEW,
                            timeout=0.1,
                            on_poll=sync_cancel_on_poll,
                        )
                        assert res_sync_cancel.status == "TIMED_OUT"
                        await asyncio.sleep(0)
                        assert fut_sync_cancel.cancel_called is False
                        assert id(fut_sync_cancel) in _DETACHED_FUTURES
                        assert cancel_reports == []

                        # Late-exception and release checks in test body after detachment verified
                        fut_sync_cancel.set_exception(RuntimeError("sync cancel late error"))
                        await asyncio.sleep(0)
                        assert id(fut_sync_cancel) not in _DETACHED_FUTURES
                        assert fut_sync_cancel.exception_calls > 0
                        # import weakref (already imported at module level)

                        fut_sync_ref = weakref.ref(fut_sync_cancel)
                        fut_sync_box.clear()
                        del fut_sync_cancel
                        import gc

                        gc.collect()
                        assert fut_sync_ref() is None
                finally:
                    client_module.monotonic = orig_client_mono
                    _transport.monotonic = orig_trans_mono
            finally:
                if fut_sync_box:
                    f = fut_sync_box[0]
                    try:
                        if not asyncio.Future.done(f):
                            f.set_result(None)
                            await asyncio.sleep(0)
                        elif not asyncio.Future.cancelled(f):
                            f.exception()
                    except BaseException:
                        pass
                    fut_sync_box.clear()
        finally:
            loop.set_exception_handler(old_h)

        # Current task cannot be returned by on_poll
        with Server(lambda request, index: Reply(body=responses[0])) as server:
            async with session("async", server.url) as client:
                with pytest.raises(ValueError, match="running polling task"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=10,
                        on_poll=lambda r: asyncio.current_task(),
                    )

    # Cyclic tuple whose list points back to it
    cyclic_list: list[Any] = []
    cyclic_tuple = (cyclic_list, "tuple_leaf")
    cyclic_list.append(cyclic_tuple)

    detail_cyclic = CustomerReviewDetail.from_dict(responses[1])
    detail_cyclic.additional_properties["cyclic_tuple"] = cyclic_tuple

    snap_cyclic = _snapshot_review(detail_cyclic)
    assert snap_cyclic is not None
    snap_tup = snap_cyclic.additional_properties["cyclic_tuple"]
    assert snap_tup is not cyclic_tuple
    snap_lst = snap_tup[0]
    assert snap_lst is not cyclic_list
    assert snap_lst[0] is snap_tup

    # Writable memoryview copied to independent storage
    orig_bytearray = bytearray(b"hello")
    orig_view = memoryview(orig_bytearray)
    detail_view = CustomerReviewDetail.from_dict(responses[1])
    detail_view.additional_properties["memview"] = orig_view

    snap_view = _snapshot_review(detail_view)
    assert snap_view is not None
    copied_view = snap_view.additional_properties["memview"]
    assert isinstance(copied_view, memoryview)
    assert not copied_view.readonly
    copied_view[0] = ord(b"X")
    assert orig_bytearray == bytearray(b"hello")
    assert bytes(copied_view) == b"Xello"

    # Unsupported mutable value rejected
    import threading

    detail_unsupported = CustomerReviewDetail.from_dict(responses[1])
    detail_unsupported.additional_properties["bad"] = threading.Lock()
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_unsupported)

    # Safe finalization size for tuples skips snapshot delivery
    huge_tuple = tuple(range(1001))
    detail_huge = CustomerReviewDetail.from_dict(responses[1])
    detail_huge.additional_properties["huge"] = huge_tuple
    assert _snapshot_review(detail_huge) is None

    # Oversized buffer skips snapshot delivery
    oversized_buf = bytearray(65_537)
    detail_buf = CustomerReviewDetail.from_dict(responses[1])
    detail_buf.additional_properties["buf"] = oversized_buf
    assert _snapshot_review(detail_buf) is None

    # Multidimensional memoryview checks nbytes against cap
    multi_dim_raw = b"x" * 100_000
    multi_dim_view = memoryview(multi_dim_raw).cast("B", shape=[10, 10_000])
    assert len(multi_dim_view) == 10
    assert multi_dim_view.nbytes == 100_000
    detail_multi_dim = CustomerReviewDetail.from_dict(responses[1])
    detail_multi_dim.additional_properties["multi_dim"] = multi_dim_view
    assert _snapshot_review(detail_multi_dim) is None

    # Scalar subclass instance and attributes copied
    class CustomStr(str):
        pass

    custom_scalar = CustomStr("scalar_val")
    custom_scalar.attached_list = ["mut"]  # type: ignore[attr-defined]
    detail_scalar = CustomerReviewDetail.from_dict(responses[1])
    detail_scalar.additional_properties["scalar"] = custom_scalar

    snap_scalar = _snapshot_review(detail_scalar)
    assert snap_scalar is not None
    copied_scalar = snap_scalar.additional_properties["scalar"]
    assert type(copied_scalar) is CustomStr
    assert copied_scalar is not custom_scalar
    assert copied_scalar.attached_list is not custom_scalar.attached_list
    assert copied_scalar.attached_list == ["mut"]

    # Container subclass (defaultdict) preserves type, default_factory, and attributes
    from collections import defaultdict

    class CustomDict(defaultdict[str, list[str]]):
        pass

    dd = CustomDict(list)
    dd["k"].append("val")
    dd.extra_attr = ["extra"]  # type: ignore[attr-defined]
    detail_dd = CustomerReviewDetail.from_dict(responses[1])
    detail_dd.additional_properties["dd"] = dd

    snap_dd = _snapshot_review(detail_dd)
    assert snap_dd is not None
    copied_dd = snap_dd.additional_properties["dd"]
    assert isinstance(copied_dd, CustomDict)
    assert copied_dd is not dd
    assert copied_dd["k"] is not dd["k"]
    assert copied_dd["k"] == ["val"]
    assert copied_dd["missing"] == []
    assert copied_dd.extra_attr is not dd.extra_attr
    assert copied_dd.extra_attr == ["extra"]

    # Traverse dictionary entries and slot descriptors including private slots
    class SlotBase:
        __slots__ = ("__private_slot", "public_slot")

        def __init__(self) -> None:
            self.__private_slot = ["private_secret"]
            self.public_slot = ["public_secret"]

    class SlotDerived(SlotBase):
        pass

    slot_obj = SlotDerived()
    slot_obj.extra_dict_attr = ["extra"]

    detail_slot = CustomerReviewDetail.from_dict(responses[1])
    detail_slot.additional_properties["slot_obj"] = slot_obj

    snap_slot = _snapshot_review(detail_slot)
    assert snap_slot is not None
    copied_slot_obj = snap_slot.additional_properties["slot_obj"]
    assert copied_slot_obj is not slot_obj
    assert (
        copied_slot_obj._SlotBase__private_slot  # type: ignore[attr-defined]
        is not slot_obj._SlotBase__private_slot
    )
    assert (
        copied_slot_obj._SlotBase__private_slot  # type: ignore[attr-defined]
        == ["private_secret"]
    )
    assert copied_slot_obj.public_slot is not slot_obj.public_slot
    assert copied_slot_obj.public_slot == ["public_secret"]
    assert copied_slot_obj.extra_dict_attr is not slot_obj.extra_dict_attr
    assert copied_slot_obj.extra_dict_attr == ["extra"]

    # Tuple subclass preserves type, isolates elements, copies attributes, and respects size limit
    class CustomTuple(tuple[Any, ...]):
        pass

    ct = CustomTuple(([1, 2], {"a": "b"}))
    ct.extra = ["tuple_attr"]  # type: ignore[attr-defined]
    detail_ct = CustomerReviewDetail.from_dict(responses[1])
    detail_ct.additional_properties["ct"] = ct

    snap_ct = _snapshot_review(detail_ct)
    assert snap_ct is not None
    copied_ct = snap_ct.additional_properties["ct"]
    assert type(copied_ct) is CustomTuple
    assert copied_ct is not ct
    assert copied_ct[0] is not ct[0]
    assert copied_ct[0] == [1, 2]
    assert copied_ct[1] is not ct[1]
    assert copied_ct[1] == {"a": "b"}
    assert copied_ct.extra is not ct.extra
    assert copied_ct.extra == ["tuple_attr"]

    huge_ct = CustomTuple(range(1001))
    detail_huge_ct = CustomerReviewDetail.from_dict(responses[1])
    detail_huge_ct.additional_properties["huge_ct"] = huge_ct
    assert _snapshot_review(detail_huge_ct) is None

    # Nonempty tuple subclass with identical elements constructs distinct subclass instance
    class IdenticalTuple(tuple[Any, ...]):
        pass

    itup = IdenticalTuple((1, "str", False))
    itup.attr = ["orig_attr"]  # type: ignore[attr-defined]
    detail_itup = CustomerReviewDetail.from_dict(responses[1])
    detail_itup.additional_properties["itup"] = itup

    snap_itup = _snapshot_review(detail_itup)
    assert snap_itup is not None
    copied_itup = snap_itup.additional_properties["itup"]
    assert type(copied_itup) is IdenticalTuple
    assert copied_itup is not itup
    assert copied_itup.attr is not itup.attr
    assert copied_itup.attr == ["orig_attr"]
    copied_itup.attr.append("mutated")
    assert itup.attr == ["orig_attr"]

    # Oversized terminal reviews passed to both sync and async clients:
    # on_poll skipped and outcome returned
    detail_oversized = CustomerReviewDetail.from_dict(responses[1])
    detail_oversized.additional_properties["huge"] = tuple(range(1001))

    for test_mode in ("sync", "async"):
        oversized_poll_called = False

        def oversized_poll_cb(r: Any) -> None:
            nonlocal oversized_poll_called
            oversized_poll_called = True

        async with session(test_mode, "https://api.proofline.sh") as client:
            if test_mode == "async":

                async def fake_get_ov(*args: Any, **kwargs: Any) -> Any:
                    return detail_oversized

                monkeypatch.setattr(client, "get_review", fake_get_ov)
            else:

                def fake_get_ov_sync(*args: Any, **kwargs: Any) -> Any:
                    return detail_oversized

                monkeypatch.setattr(client, "get_review", fake_get_ov_sync)

            res_ov = await call(
                client,
                "wait_for_review",
                ORG,
                REVIEW,
                timeout=10,
                on_poll=oversized_poll_cb,
            )
            assert res_ov.status == "COMPLETED"
            assert not oversized_poll_called

    # Lock-bearing reviews passed to both sync and async clients:
    # TypeError propagates and on_poll is not called
    import threading

    detail_lock = CustomerReviewDetail.from_dict(responses[1])
    detail_lock.additional_properties["lock"] = threading.Lock()

    for test_mode in ("sync", "async"):
        lock_poll_called = False

        def lock_poll_cb(r: Any) -> None:
            nonlocal lock_poll_called
            lock_poll_called = True

        async with session(test_mode, "https://api.proofline.sh") as client:
            if test_mode == "async":

                async def fake_get_lock(*args: Any, **kwargs: Any) -> Any:
                    return detail_lock

                monkeypatch.setattr(client, "get_review", fake_get_lock)
            else:

                def fake_get_lock_sync(*args: Any, **kwargs: Any) -> Any:
                    return detail_lock

                monkeypatch.setattr(client, "get_review", fake_get_lock_sync)

            with pytest.raises(TypeError, match="Unsupported mutable value"):
                await call(
                    client,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    timeout=10,
                    on_poll=lock_poll_cb,
                )
            assert not lock_poll_called

    # Multidimensional memoryview shape and format preserved
    raw_mv = bytearray(b"0123456789abcdef")
    mv_orig = memoryview(raw_mv).cast("B", shape=[4, 4])
    detail_mv = CustomerReviewDetail.from_dict(responses[1])
    detail_mv.additional_properties["mv"] = mv_orig

    snap_mv = _snapshot_review(detail_mv)
    assert snap_mv is not None
    copied_mv = snap_mv.additional_properties["mv"]
    assert isinstance(copied_mv, memoryview)
    assert copied_mv.shape == (4, 4)
    assert copied_mv.format == "B"
    assert copied_mv[1, 2] == mv_orig[1, 2]
    copied_mv[1, 2] = ord("Z")
    assert raw_mv != bytearray(copied_mv)

    # Named tuple preserves named fields
    from typing import NamedTuple

    class Point(NamedTuple):
        x: int
        y: int

    pt = Point(10, 20)
    detail_pt = CustomerReviewDetail.from_dict(responses[1])
    detail_pt.additional_properties["pt"] = pt

    snap_pt = _snapshot_review(detail_pt)
    assert snap_pt is not None
    copied_pt = snap_pt.additional_properties["pt"]
    assert type(copied_pt) is Point
    assert copied_pt.x == 10
    assert copied_pt.y == 20

    # Derived slot does not hide base slot
    class BaseSlot:
        __slots__ = ("shared_slot",)

    class DerivedSlot(BaseSlot):
        __slots__ = ("shared_slot",)

    slot_inst = DerivedSlot()
    BaseSlot.shared_slot.__set__(slot_inst, ["base_data"])
    DerivedSlot.shared_slot.__set__(slot_inst, ["derived_data"])
    detail_slots = CustomerReviewDetail.from_dict(responses[1])
    detail_slots.additional_properties["slots"] = slot_inst

    snap_slots = _snapshot_review(detail_slots)
    assert snap_slots is not None
    copied_slots = snap_slots.additional_properties["slots"]
    assert type(copied_slots) is DerivedSlot
    assert BaseSlot.shared_slot.__get__(copied_slots) == ["base_data"]
    assert BaseSlot.shared_slot.__get__(copied_slots) is not BaseSlot.shared_slot.__get__(slot_inst)
    assert DerivedSlot.shared_slot.__get__(copied_slots) == ["derived_data"]
    assert DerivedSlot.shared_slot.__get__(copied_slots) is not DerivedSlot.shared_slot.__get__(
        slot_inst
    )

    # Empty tuple subclass with required __init__ argument
    class EmptyArgTuple(tuple[Any, ...]):
        def __init__(self, required_arg: Any) -> None:
            self.attr = "initialized"

    empty_tup_inst = tuple.__new__(EmptyArgTuple, ())
    empty_tup_inst.attr = "custom_attr"  # type: ignore[attr-defined]
    detail_empty_arg = CustomerReviewDetail.from_dict(responses[1])
    detail_empty_arg.additional_properties["empty_arg"] = empty_tup_inst

    snap_empty_arg = _snapshot_review(detail_empty_arg)
    assert snap_empty_arg is not None
    copied_empty_arg = snap_empty_arg.additional_properties["empty_arg"]
    assert type(copied_empty_arg) is EmptyArgTuple
    assert copied_empty_arg == ()
    assert copied_empty_arg.attr == "custom_attr"

    # Dict keys resolved through memo preserving alias with value
    class KeyValObj:
        def __init__(self, name: str) -> None:
            self.name = name

    shared_obj = KeyValObj("shared_alias")
    key_tup = (shared_obj, 1)
    dict_with_alias = {key_tup: shared_obj}
    detail_alias = CustomerReviewDetail.from_dict(responses[1])
    detail_alias.additional_properties["alias_dict"] = dict_with_alias

    snap_alias = _snapshot_review(detail_alias)
    assert snap_alias is not None
    copied_dict = snap_alias.additional_properties["alias_dict"]
    assert len(copied_dict) == 1
    for k, v in copied_dict.items():
        assert k is not key_tup
        assert k[0] is v
        assert v is not shared_obj
        assert v.name == "shared_alias"

    # Set member containing oversized tuple skips snapshot delivery
    set_with_huge_tuple = {tuple(range(1001))}
    detail_set_huge = CustomerReviewDetail.from_dict(responses[1])
    detail_set_huge.additional_properties["set_huge"] = set_with_huge_tuple
    assert _snapshot_review(detail_set_huge) is None

    # Mutable object whose __copy__ returns self is rejected with TypeError
    class SelfCopyList(list[Any]):
        def __copy__(self) -> Any:
            return self

    self_copy_inst = SelfCopyList([1, 2])
    detail_self_copy = CustomerReviewDetail.from_dict(responses[1])
    detail_self_copy.additional_properties["self_copy"] = self_copy_inst
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_self_copy)

    # Memoryview with invalid destination format for cast raises TypeError
    import ctypes

    c_arr = (ctypes.c_int32 * 4)()
    mv_ctypes = memoryview(c_arr)
    detail_ctypes_mv = CustomerReviewDetail.from_dict(responses[1])
    detail_ctypes_mv.additional_properties["ctypes_mv"] = mv_ctypes
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_ctypes_mv)

    # Empty set subclass copies attributes
    class CustomSet(set[Any]):
        pass

    empty_custom_set = CustomSet()
    empty_custom_set.custom_attr = ["set_attr"]  # type: ignore[attr-defined]
    detail_empty_set = CustomerReviewDetail.from_dict(responses[1])
    detail_empty_set.additional_properties["empty_set"] = empty_custom_set

    snap_empty_set = _snapshot_review(detail_empty_set)
    assert snap_empty_set is not None
    copied_empty_set = snap_empty_set.additional_properties["empty_set"]
    assert type(copied_empty_set) is CustomSet
    assert len(copied_empty_set) == 0
    assert copied_empty_set.custom_attr is not empty_custom_set.custom_attr
    assert copied_empty_set.custom_attr == ["set_attr"]

    # Set subclass requiring extra constructor argument propagates TypeError
    class RequiredArgSet(set[Any]):
        def __init__(self, required_arg: Any) -> None:
            super().__init__()

    req_set = set.__new__(RequiredArgSet)
    detail_req_set = CustomerReviewDetail.from_dict(responses[1])
    detail_req_set.additional_properties["req_set"] = req_set
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_req_set)

    # Bytearray subclass preserves subclass type and copies instance attributes
    class CustomByteArray(bytearray):
        pass

    custom_ba = CustomByteArray(b"custom_bytes")
    custom_ba.extra_attr = ["extra"]  # type: ignore[attr-defined]
    detail_custom_ba = CustomerReviewDetail.from_dict(responses[1])
    detail_custom_ba.additional_properties["custom_ba"] = custom_ba
    snap_ba = _snapshot_review(detail_custom_ba)
    assert snap_ba is not None
    copied_ba = snap_ba.additional_properties["custom_ba"]
    assert type(copied_ba) is CustomByteArray
    assert copied_ba == b"custom_bytes"
    assert copied_ba is not custom_ba
    assert copied_ba.extra_attr is not custom_ba.extra_attr
    assert copied_ba.extra_attr == ["extra"]

    # Class with exhausted __slots__ iterator has installed descriptors enumerated
    class ExhaustedSlotsObj:
        __slots__ = iter(["slot_attr"])

        def __init__(self, val: Any) -> None:
            self.slot_attr = val

        def __copy__(self) -> Any:
            res = ExhaustedSlotsObj.__new__(ExhaustedSlotsObj)
            res.slot_attr = self.slot_attr
            return res

    orig_slots_inst = ExhaustedSlotsObj(["slot_val"])
    detail_slots = CustomerReviewDetail.from_dict(responses[1])
    detail_slots.additional_properties["exhausted_slots"] = orig_slots_inst
    snap_slots = _snapshot_review(detail_slots)
    assert snap_slots is not None
    copied_slots_inst = snap_slots.additional_properties["exhausted_slots"]
    assert copied_slots_inst is not orig_slots_inst
    assert copied_slots_inst.slot_attr is not orig_slots_inst.slot_attr
    assert copied_slots_inst.slot_attr == ["slot_val"]

    # Datetime with custom mutable tzinfo copies tzinfo and avoids leaking mutation
    import datetime as dt_mod

    class CustomMutableTz(dt_mod.tzinfo):
        def __init__(self, offset_minutes: int = 0) -> None:
            self.offset_minutes = offset_minutes
            self.tz_attr = ["tz_state"]

        def utcoffset(self, dt_val: Any) -> timedelta:
            return timedelta(minutes=self.offset_minutes)

        def tzname(self, dt_val: Any) -> str:
            return "CUSTOM"

        def dst(self, dt_val: Any) -> timedelta:
            return timedelta(0)

    custom_tz_inst = CustomMutableTz(60)
    dt_with_custom_tz = datetime(2026, 11, 22, 10, 0, 0, tzinfo=custom_tz_inst)
    detail_dt = CustomerReviewDetail.from_dict(responses[1])
    detail_dt.additional_properties["custom_tz_dt"] = dt_with_custom_tz
    snap_dt = _snapshot_review(detail_dt)
    assert snap_dt is not None
    copied_dt = snap_dt.additional_properties["custom_tz_dt"]
    assert copied_dt == dt_with_custom_tz
    assert copied_dt.tzinfo is not custom_tz_inst
    assert copied_dt.tzinfo.tz_attr is not custom_tz_inst.tz_attr
    assert copied_dt.tzinfo.tz_attr == ["tz_state"]

    # Deceptive tuple subclass reporting len 1 with > 1000 items is skipped
    class DeceptiveTuple(tuple[Any, ...]):
        def __len__(self) -> int:
            return 1

    huge_tup_items = tuple(range(1001))
    deceptive_tup = tuple.__new__(DeceptiveTuple, huge_tup_items)
    detail_deceptive = CustomerReviewDetail.from_dict(responses[1])
    detail_deceptive.additional_properties["deceptive"] = deceptive_tup
    assert _snapshot_review(detail_deceptive) is None

    # Bytearray subclass rejecting single-buffer constructor is allocated via base methods
    class SubByteArray(bytearray):
        def __init__(self, required_arg: int) -> None:
            if not isinstance(required_arg, int) or isinstance(required_arg, bool):
                raise TypeError("required_arg must be an int")
            super().__init__()
            self.required_arg = required_arg

    sub_ba = bytearray.__new__(SubByteArray)
    bytearray.__init__(sub_ba, b"sub_bytes")
    sub_ba.required_arg = 100
    sub_ba.custom_attr = ["sub_attr"]

    detail_sub_ba = CustomerReviewDetail.from_dict(responses[1])
    detail_sub_ba.additional_properties["sub_ba"] = sub_ba
    snap_sub_ba = _snapshot_review(detail_sub_ba)
    assert snap_sub_ba is not None
    copied_sub_ba = snap_sub_ba.additional_properties["sub_ba"]
    assert type(copied_sub_ba) is SubByteArray
    assert copied_sub_ba == b"sub_bytes"
    assert copied_sub_ba.custom_attr is not sub_ba.custom_attr
    assert copied_sub_ba.custom_attr == ["sub_attr"]

    # Datetime subclass cloned and instance attributes snapshotted
    class SubDatetime(datetime):
        pass

    sub_dt = SubDatetime(2026, 11, 22, 12, 0, 0, tzinfo=UTC)
    sub_dt.sub_attr = ["dt_attr"]
    detail_sub_dt = CustomerReviewDetail.from_dict(responses[1])
    detail_sub_dt.additional_properties["sub_dt"] = sub_dt
    snap_sub_dt = _snapshot_review(detail_sub_dt)
    assert snap_sub_dt is not None
    copied_sub_dt = snap_sub_dt.additional_properties["sub_dt"]
    assert type(copied_sub_dt) is SubDatetime
    assert copied_sub_dt == sub_dt
    assert copied_sub_dt is not sub_dt
    assert copied_sub_dt.sub_attr is not sub_dt.sub_attr
    assert copied_sub_dt.sub_attr == ["dt_attr"]

    # Mutable tzinfo returning self from __copy__ is rejected with TypeError
    class SelfCopyTz(dt_mod.tzinfo):
        def __copy__(self) -> Any:
            return self

    self_copy_tz = SelfCopyTz()
    dt_self_copy_tz = datetime(2026, 11, 22, 10, 0, 0, tzinfo=self_copy_tz)
    detail_self_copy_tz = CustomerReviewDetail.from_dict(responses[1])
    detail_self_copy_tz.additional_properties["self_copy_tz"] = dt_self_copy_tz
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_self_copy_tz)

    # SubDatetime with custom mutable tzinfo rebuilds subclass with copied tzinfo
    sub_dt_custom_tz = SubDatetime(2026, 11, 22, 12, 0, 0, tzinfo=custom_tz_inst)
    sub_dt_custom_tz.sub_attr = ["dt_tz_attr"]
    detail_sub_tz = CustomerReviewDetail.from_dict(responses[1])
    detail_sub_tz.additional_properties["sub_dt_tz"] = sub_dt_custom_tz
    snap_sub_tz = _snapshot_review(detail_sub_tz)
    assert snap_sub_tz is not None
    copied_sub_tz = snap_sub_tz.additional_properties["sub_dt_tz"]
    assert type(copied_sub_tz) is SubDatetime
    assert copied_sub_tz == sub_dt_custom_tz
    assert copied_sub_tz.tzinfo is not custom_tz_inst
    assert copied_sub_tz.tzinfo.tz_attr is not custom_tz_inst.tz_attr
    assert copied_sub_tz.sub_attr is not sub_dt_custom_tz.sub_attr

    # Deceptive set subclass returning len 0 with members copies all members
    class DeceptiveSet(set[Any]):
        def __len__(self) -> int:
            return 0

    deceptive_s = DeceptiveSet(["member1", "member2"])
    detail_deceptive_s = CustomerReviewDetail.from_dict(responses[1])
    detail_deceptive_s.additional_properties["deceptive_s"] = deceptive_s
    snap_deceptive_s = _snapshot_review(detail_deceptive_s)
    assert snap_deceptive_s is not None
    copied_deceptive_s = snap_deceptive_s.additional_properties["deceptive_s"]
    assert type(copied_deceptive_s) is DeceptiveSet
    assert "member1" in copied_deceptive_s and "member2" in copied_deceptive_s

    # Set subclass whose constructor inserts extra member does not reintroduce it
    class InjectedSet(set[Any]):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.add("injected_shared_member")

    injected_s = InjectedSet(["orig_member"])
    injected_s.remove("injected_shared_member")
    detail_injected_s = CustomerReviewDetail.from_dict(responses[1])
    detail_injected_s.additional_properties["injected_s"] = injected_s
    snap_injected_s = _snapshot_review(detail_injected_s)
    assert snap_injected_s is not None
    copied_injected_s = snap_injected_s.additional_properties["injected_s"]
    assert type(copied_injected_s) is InjectedSet
    assert "injected_shared_member" not in copied_injected_s
    assert "orig_member" in copied_injected_s

    # Standard built-in set and frozenset properly snapshotted with hashable mutable payload
    class HashablePayload:
        def __init__(self, key: str, payload: list[str]) -> None:
            self.key = key
            self.payload = payload

        def __hash__(self) -> int:
            return hash(self.key)

        def __eq__(self, other: Any) -> bool:
            return isinstance(other, HashablePayload) and self.key == other.key

    leaf_payload = HashablePayload("leaf_key", ["leaf_original"])
    inner_fs = frozenset([leaf_payload])
    outer_fs = frozenset([inner_fs])

    member_payload = HashablePayload("test_key", ["original_val"])
    normal_s = {member_payload}
    normal_fs = frozenset([member_payload])
    detail_sets = CustomerReviewDetail.from_dict(responses[1])
    detail_sets.additional_properties["normal_s"] = normal_s
    detail_sets.additional_properties["normal_fs"] = normal_fs
    detail_sets.additional_properties["nested_fs"] = outer_fs
    detail_sets.additional_properties["fs_list"] = [normal_fs, normal_fs]
    snap_sets = _snapshot_review(detail_sets)
    assert snap_sets is not None
    assert snap_sets.additional_properties["normal_s"] == normal_s
    assert snap_sets.additional_properties["normal_s"] is not normal_s
    copied_fs = snap_sets.additional_properties["normal_fs"]
    assert isinstance(copied_fs, frozenset)
    assert len(copied_fs) == 1
    copied_list = snap_sets.additional_properties["fs_list"]
    assert copied_list[0] is copied_list[1]
    assert copied_list[0] is copied_fs
    cloned_member = next(iter(copied_fs))
    assert cloned_member == member_payload
    assert cloned_member is not member_payload
    assert next(iter(snap_sets.additional_properties["normal_s"])) is cloned_member
    assert cloned_member.payload is not member_payload.payload
    assert cloned_member in copied_fs
    cloned_member.payload.append("mutated_val")
    assert member_payload.payload == ["original_val"]

    copied_outer = snap_sets.additional_properties["nested_fs"]
    assert isinstance(copied_outer, frozenset)
    assert len(copied_outer) == 1
    copied_inner = next(iter(copied_outer))
    assert isinstance(copied_inner, frozenset)
    assert len(copied_inner) == 1
    copied_leaf = next(iter(copied_inner))
    assert copied_leaf == leaf_payload
    assert copied_leaf is not leaf_payload
    assert copied_leaf.payload is not leaf_payload.payload
    assert copied_inner in copied_outer
    assert copied_leaf in copied_inner
    copied_leaf.payload.append("leaf_mutated")
    assert leaf_payload.payload == ["leaf_original"]

    # Deque traversed and snapshotted, and weakref inside deque rejected
    from collections import deque

    dq: deque[Any] = deque(["elem1", ["nested_list"]])
    detail_dq = CustomerReviewDetail.from_dict(responses[1])
    detail_dq.additional_properties["dq"] = dq
    snap_dq = _snapshot_review(detail_dq)
    assert snap_dq is not None
    copied_dq = snap_dq.additional_properties["dq"]
    assert isinstance(copied_dq, deque)
    assert copied_dq == dq
    assert copied_dq is not dq
    assert copied_dq[1] is not dq[1]

    # Deque subclass preserves subclass type, maxlen, and restores attributes
    class CustomDeque(deque[Any]):
        pass

    c_dq: CustomDeque = CustomDeque(["d1", "d2"], maxlen=5)
    c_dq.custom_dq_attr = ["dq_attr"]  # type: ignore[attr-defined]
    detail_c_dq = CustomerReviewDetail.from_dict(responses[1])
    detail_c_dq.additional_properties["c_dq"] = c_dq
    snap_c_dq = _snapshot_review(detail_c_dq)
    assert snap_c_dq is not None
    copied_c_dq = snap_c_dq.additional_properties["c_dq"]
    assert type(copied_c_dq) is CustomDeque
    assert copied_c_dq.maxlen == 5
    assert copied_c_dq == c_dq
    assert copied_c_dq is not c_dq
    assert copied_c_dq.custom_dq_attr is not c_dq.custom_dq_attr
    assert copied_c_dq.custom_dq_attr == ["dq_attr"]

    # Deceptive bytearray subclass underreporting len with > 65536 bytes is skipped
    class DeceptiveByteArray(bytearray):
        def __len__(self) -> int:
            return 1

    huge_ba = bytearray.__new__(DeceptiveByteArray)
    bytearray.__init__(huge_ba, b"x" * 65537)
    detail_huge_ba = CustomerReviewDetail.from_dict(responses[1])
    detail_huge_ba.additional_properties["huge_ba"] = huge_ba
    assert _snapshot_review(detail_huge_ba) is None

    # Weak references in snapshot extension data are rejected with TypeError
    # import weakref (already imported at module level)

    class TargetObj:
        pass

    dummy_target = TargetObj()
    weak_ref_obj = weakref.ref(dummy_target)
    detail_weakref = CustomerReviewDetail.from_dict(responses[1])
    detail_weakref.additional_properties["weakref"] = weak_ref_obj
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_weakref)

    # Deque containing weak reference rejected with TypeError
    dq_weakref: deque[Any] = deque([weak_ref_obj])
    detail_dq_weakref = CustomerReviewDetail.from_dict(responses[1])
    detail_dq_weakref.additional_properties["dq_weakref"] = dq_weakref
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_dq_weakref)

    # Synchronous wait_for_review passed an async callback raises TypeError
    async def async_cb_on_sync_client(r: Any) -> None:
        pass

    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session("sync", server.url) as sync_cli:
            with pytest.raises(TypeError, match="AsyncProoflineClient"):
                await call(
                    sync_cli,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    timeout=10,
                    on_poll=async_cb_on_sync_client,
                )

    # Synchronous wait_for_review rejecting non-None return with TypeError
    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session("sync", server.url) as sync_cli:
            with pytest.raises(TypeError, match="Callbacks must return None"):
                await call(
                    sync_cli,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    timeout=10,
                    on_poll=lambda r: False,
                )

    # Synchronous wait_for_review closes generator awaitable in GEN_CREATED
    import types

    @types.coroutine
    def gen_coro_cb(r: Any) -> Any:
        yield

    gen_cb_inst = gen_coro_cb(None)

    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session("sync", server.url) as sync_cli:
            with pytest.raises(TypeError, match="AsyncProoflineClient"):
                await call(
                    sync_cli,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    timeout=10,
                    on_poll=lambda r: gen_cb_inst,
                )
    assert inspect.getgeneratorstate(gen_cb_inst) == inspect.GEN_CLOSED

    # wait_for_review cleans up already-failed foreign-loop future returned when budget is exhausted
    class TrackedForeignFuture(asyncio.Future[None]):
        def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
            super().__init__(loop=loop)
            self.exception_retrieved = False

        def exception(self) -> BaseException | None:
            self.exception_retrieved = True
            return super().exception()

            # import weakref (already imported at module level)

    foreign_loop_failed = asyncio.new_event_loop()
    foreign_reports: list[dict[str, Any]] = []
    foreign_loop_failed.set_exception_handler(lambda _loop, ctx: foreign_reports.append(ctx))
    try:
        foreign_failed_box: list[Any] = [TrackedForeignFuture(loop=foreign_loop_failed)]
        foreign_failed_box[0].set_exception(RuntimeError("foreign future failed"))
        foreign_failed_fut_ref = weakref.ref(foreign_failed_box[0])

        def foreign_fail_cb(r: Any) -> Any:
            clock.now += 150.0
            return foreign_failed_box[0]

        with Server(lambda request, index: Reply(body=responses[1])) as server:
            async with session("async", server.url) as client:
                res_foreign = await client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=100.0,
                    on_poll=foreign_fail_cb,
                )
                assert res_foreign.status == "COMPLETED"
                tracked_ref = foreign_failed_fut_ref()
                assert tracked_ref is not None
                assert tracked_ref.exception_retrieved is True
                del tracked_ref
                foreign_failed_box.clear()
                import gc

                gc.collect()
                assert foreign_failed_fut_ref() is None
                assert foreign_reports == []
    finally:
        if foreign_failed_box:
            try:
                ff = foreign_failed_box[0]
                if not ff.cancelled():
                    ff.exception()
            except BaseException:
                pass
            foreign_failed_box.clear()
        foreign_loop_failed.close()

    # Datetime subclass whose replace fails and fallback lacks copied_tz raises TypeError
    class BrokenSubDatetime(datetime):
        def __new__(cls, y: int, m: int, d: int, tzinfo: Any = None) -> Any:
            return super().__new__(cls, y, m, d, tzinfo=tzinfo)

        def replace(self, **kwargs: Any) -> Any:
            raise RuntimeError("cannot replace")

        def __copy__(self) -> Any:
            return super().__new__(
                BrokenSubDatetime, self.year, self.month, self.day, tzinfo=self.tzinfo
            )

    broken_dt = BrokenSubDatetime(2026, 11, 22, tzinfo=custom_tz_inst)
    detail_broken_dt = CustomerReviewDetail.from_dict(responses[1])
    detail_broken_dt.additional_properties["broken_dt"] = broken_dt
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_broken_dt)

    # Slotted extension object with class-level mutable list such as __shared__ is rejected
    class SlottedSharedAttrObj:
        __slots__ = ("instance_attr",)
        __shared__ = [1, 2, 3]

        def __init__(self, val: Any) -> None:
            self.instance_attr = val

    slotted_shared = SlottedSharedAttrObj("val")
    detail_slotted = CustomerReviewDetail.from_dict(responses[1])
    detail_slotted.additional_properties["shared"] = slotted_shared
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_slotted)

    # Set member is a tuple containing an object with a custom hash that reads an inner dict
    class CustomHashWithDict:
        def __init__(self, d: dict[str, Any]) -> None:
            self.d = d

        def __hash__(self) -> int:
            return hash(tuple(sorted(self.d.items())))

        def __eq__(self, other: Any) -> bool:
            return isinstance(other, CustomHashWithDict) and self.d == other.d

    inner_dict = {"key": "val"}
    custom_obj = CustomHashWithDict(inner_dict)
    tuple_with_custom = (custom_obj,)
    set_with_tuple = {tuple_with_custom}
    detail_tuple_custom = CustomerReviewDetail.from_dict(responses[1])
    detail_tuple_custom.additional_properties["set_tuple"] = set_with_tuple
    snap_tc = _snapshot_review(detail_tuple_custom)
    assert snap_tc is not None
    copied_set = snap_tc.additional_properties["set_tuple"]
    copied_tuple = next(iter(copied_set))
    assert copied_tuple[0].d == {"key": "val"}
    assert copied_tuple[0].d is not inner_dict

    # Snapshot overlapping views of one subclass exporter, visiting a view first:
    # assert shared writes, original isolation, copied attributes, and scalar shape ()
    class SubclassByteArray(bytearray):
        pass

    sub_ba = SubclassByteArray(b"0123456789abcdef")
    sub_ba.extra_attr = ["isolated_extra"]  # type: ignore[attr-defined]

    sub_mv1 = memoryview(sub_ba)[0:10]
    sub_scalar = memoryview(sub_ba)[6:7].cast("B", shape=())
    sub_mv2 = memoryview(sub_ba)[5:15]

    detail_view_first = CustomerReviewDetail.from_dict(responses[1])
    detail_view_first.additional_properties = {
        "view1": sub_mv1,
        "scalar": sub_scalar,
        "view2": sub_mv2,
        "exporter": sub_ba,
    }

    snap_vf = _snapshot_review(detail_view_first)
    assert snap_vf is not None
    copied_v1 = snap_vf.additional_properties["view1"]
    copied_scalar = snap_vf.additional_properties["scalar"]
    copied_v2 = snap_vf.additional_properties["view2"]
    copied_exp = snap_vf.additional_properties["exporter"]

    assert copied_scalar.shape == ()
    assert copied_scalar.ndim == 0
    assert copied_scalar[()] == ord("6")
    assert type(copied_exp) is SubclassByteArray
    assert copied_exp.extra_attr == ["isolated_extra"]
    assert copied_exp.extra_attr is not sub_ba.extra_attr

    copied_v1[6] = ord("X")
    assert copied_v2[1] == ord("X")
    assert copied_scalar[()] == ord("X")
    assert copied_exp[6] == ord("X")
    assert sub_ba[6] == ord("6")
    assert sub_mv1[6] == ord("6")
    assert sub_mv2[1] == ord("6")
    assert sub_scalar[()] == ord("6")
    copied_exp.extra_attr.append("new_val")
    assert "new_val" not in sub_ba.extra_attr

    # Also test with array.array subclass exporter and integer views:
    class SubclassIntArray(array.array):
        pass

    sub_arr = SubclassIntArray("i", [10, 20, 30, 40, 50, 60, 70, 80])
    sub_arr.custom_dict = {"prop": "val"}  # type: ignore[attr-defined]
    arr_v1 = memoryview(sub_arr)[1:6]
    arr_scalar = memoryview(sub_arr).cast("B")[12:16].cast("i", shape=())
    arr_v2 = memoryview(sub_arr)[2:7]

    detail_arr_vf = CustomerReviewDetail.from_dict(responses[1])
    detail_arr_vf.additional_properties = {
        "arr_v1": arr_v1,
        "arr_scalar": arr_scalar,
        "arr_v2": arr_v2,
        "arr_exp": sub_arr,
    }

    snap_arr = _snapshot_review(detail_arr_vf)
    assert snap_arr is not None
    c_arr_v1 = snap_arr.additional_properties["arr_v1"]
    c_arr_scalar = snap_arr.additional_properties["arr_scalar"]
    c_arr_v2 = snap_arr.additional_properties["arr_v2"]
    c_arr_exp = snap_arr.additional_properties["arr_exp"]

    assert c_arr_scalar.shape == ()
    assert c_arr_scalar.ndim == 0
    assert c_arr_scalar[()] == 40
    assert type(c_arr_exp) is SubclassIntArray
    assert c_arr_exp.custom_dict == {"prop": "val"}
    assert c_arr_exp.custom_dict is not sub_arr.custom_dict

    c_arr_v1[2] = 999
    assert c_arr_v2[1] == 999
    assert c_arr_scalar[()] == 999
    assert c_arr_exp[3] == 999
    assert sub_arr[3] == 40
    assert arr_v1[2] == 40

    # Class-state rejection for set subclass and views over bytearray and array.array subclasses
    class SetWithClassList(set[Any]):
        __shared_list__ = [1, 2]

    detail_set_class_list = CustomerReviewDetail.from_dict(responses[1])
    detail_set_class_list.additional_properties["set_sub"] = SetWithClassList([1, 2])
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_set_class_list)

    class ByteArrayWithClassList(bytearray):
        __shared_list__ = [1, 2]

    ba_sub_shared = ByteArrayWithClassList(b"hello")
    detail_ba_view = CustomerReviewDetail.from_dict(responses[1])
    detail_ba_view.additional_properties["ba_view"] = memoryview(ba_sub_shared)
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_ba_view)

    class ArrayWithClassList(array.array):
        __shared_list__ = [1, 2]

    arr_sub_shared = ArrayWithClassList("i", [1, 2, 3])
    detail_arr_view = CustomerReviewDetail.from_dict(responses[1])
    detail_arr_view.additional_properties["arr_view"] = memoryview(arr_sub_shared)
    with pytest.raises(TypeError, match="Unsupported mutable value"):
        _snapshot_review(detail_arr_view)

    # Key whose custom hash reads a deferred dictionary through a frozenset member
    class DictHolder:
        def __init__(self, d: dict[str, Any]) -> None:
            self.d = d

    class CustomHashWithFrozenset:
        def __init__(self, f_set: frozenset[Any]) -> None:
            self.f_set = f_set

        def __hash__(self) -> int:
            for item in self.f_set:
                if hasattr(item, "d"):
                    return hash(tuple(sorted(item.d.items())))
            return 0

        def __eq__(self, other: Any) -> bool:
            return isinstance(other, CustomHashWithFrozenset) and self.f_set == other.f_set

    deferred_dict = {"ready_key": "ready_val"}
    f_set = frozenset([DictHolder(deferred_dict)])
    custom_fs_obj = CustomHashWithFrozenset(f_set)
    set_with_fs_custom = {custom_fs_obj}
    detail_fs_custom = CustomerReviewDetail.from_dict(responses[1])
    detail_fs_custom.additional_properties["fs_custom"] = set_with_fs_custom
    snap_fsc = _snapshot_review(detail_fs_custom)
    assert snap_fsc is not None
    copied_fsc_set = snap_fsc.additional_properties["fs_custom"]
    copied_obj = next(iter(copied_fsc_set))
    copied_holder = next(iter(copied_obj.f_set))
    assert copied_holder.d == {"ready_key": "ready_val"}
    assert copied_holder.d is not deferred_dict

    # Strided memoryview over immutable bytes preserves strides and c_contiguous
    b_data = b"0123456789abcdef"
    mv_strided = memoryview(b_data)[::2]
    detail_strided = CustomerReviewDetail.from_dict(responses[1])
    detail_strided.additional_properties["strided"] = mv_strided
    snap_strided = _snapshot_review(detail_strided)
    assert snap_strided is not None
    c_strided = snap_strided.additional_properties["strided"]
    assert c_strided.strides == mv_strided.strides
    assert c_strided.c_contiguous == mv_strided.c_contiguous
    assert bytes(c_strided) == bytes(mv_strided)

    # 1-byte view over backing buffer > 65,536 bytes skips delivery (returns None)
    big_backing = b"A" * 65537
    mv_1byte = memoryview(big_backing)[0:1]
    detail_1byte = CustomerReviewDetail.from_dict(responses[1])
    detail_1byte.additional_properties["mv_1b"] = mv_1byte
    assert _snapshot_review(detail_1byte) is None

    # Invalid callback return raising property on close
    class RaisingCloseReturn:
        @property
        def close(self) -> Any:
            raise RuntimeError("close property lookup failed")

    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session("sync", server.url) as client_sync:
            with pytest.raises(TypeError, match="Callbacks must return None"):
                await call(
                    client_sync,
                    "wait_for_review",
                    ORG,
                    REVIEW,
                    on_poll=lambda r: RaisingCloseReturn(),
                )


async def test_wait_for_review_pending_futures_and_clock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = Clock(monkeypatch)
    responses = [review("RUNNING"), review()]

    # Assert remaining budget with controlled clock
    wait_timeouts: list[float | None] = []
    orig_async_wait = client_module.async_wait

    async def tracking_wait(fs: Any, *, timeout: float | None = None) -> Any:
        wait_timeouts.append(timeout)
        return await orig_async_wait(fs, timeout=timeout)

    monkeypatch.setattr(client_module, "async_wait", tracking_wait)

    async def dummy_async_cb(r: Any) -> None:
        pass

    def cb_consuming_clock(r: Any) -> Any:
        clock.now += 35.0
        return dummy_async_cb(r)

    with Server(lambda request, index: Reply(body=responses[1])) as server:
        async with session("async", server.url) as client:
            await client.wait_for_review(
                ORG,
                REVIEW,
                timeout=100.0,
                on_poll=cb_consuming_clock,
            )
    assert wait_timeouts == [65.0]
    monkeypatch.setattr(client_module, "async_wait", orig_async_wait)

    # Timely pending future failure propagates even if done() lies
    class LyingDoneFuture(asyncio.Future[None]):
        def done(self) -> bool:
            return False

    timely_fut: Any = LyingDoneFuture(loop=asyncio.get_running_loop())
    timely_producer: asyncio.Task[None] | None = None

    async def fail_timely_soon() -> None:
        await asyncio.sleep(0.01)
        timely_fut.set_exception(ValueError("timely failure"))

    def timely_fail_cb(r: Any) -> asyncio.Future[None]:
        nonlocal timely_producer
        timely_producer = asyncio.create_task(fail_timely_soon())
        return timely_fut

    try:
        with Server(lambda request, index: Reply(body=responses[0])) as server:
            async with session("async", server.url) as client:
                with pytest.raises(ValueError, match="timely failure"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=100.0,
                        on_poll=timely_fail_cb,
                    )
    finally:
        if timely_producer is not None:
            if not timely_producer.done():
                timely_producer.cancel()
            try:
                await timely_producer
            except BaseException:
                pass
        try:
            if not asyncio.Future.done(timely_fut):
                timely_fut.cancel()
            elif not asyncio.Future.cancelled(timely_fut):
                timely_fut.exception()
        except BaseException:
            pass

    # Timely pending future failure propagates when clock advances after SDK done-callback
    # but before waiter resumes
    class ClockAdvancingFuture(asyncio.Future[None]):
        def add_done_callback(self, fn: Any, *, context: Any = None) -> None:
            super().add_done_callback(fn, context=context)
            super().add_done_callback(lambda _: setattr(clock, "now", clock.now + 200.0))

    timely_late_fut: Any = ClockAdvancingFuture(loop=asyncio.get_running_loop())
    timely_late_producer: asyncio.Task[None] | None = None

    async def fail_timely_late_soon() -> None:
        await asyncio.sleep(0.01)
        timely_late_fut.set_exception(ValueError("timely failure with late resumption"))

    def timely_late_fail_cb(r: Any) -> asyncio.Future[None]:
        nonlocal timely_late_producer
        timely_late_producer = asyncio.create_task(fail_timely_late_soon())
        return timely_late_fut

    try:
        with Server(lambda request, index: Reply(body=responses[0])) as server:
            async with session("async", server.url) as client:
                with pytest.raises(ValueError, match="timely failure with late resumption"):
                    await client.wait_for_review(
                        ORG,
                        REVIEW,
                        timeout=100.0,
                        on_poll=timely_late_fail_cb,
                    )
        assert clock.now >= 200.0
    finally:
        if timely_late_producer is not None:
            if not timely_late_producer.done():
                timely_late_producer.cancel()
            try:
                await timely_late_producer
            except BaseException:
                pass
        try:
            if not asyncio.Future.done(timely_late_fut):
                timely_late_fut.cancel()
            elif not asyncio.Future.cancelled(timely_late_fut):
                timely_late_fut.exception()
        except BaseException:
            pass

    # Late-observed pending future failure preserves the classified outcome
    class TrackedFuture(asyncio.Future[None]):
        def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
            super().__init__(loop=loop)
            self.exception_retrieved = False

        def exception(self) -> BaseException | None:
            self.exception_retrieved = True
            return super().exception()

            # import weakref (already imported at module level)

    late_fut: TrackedFuture | None = TrackedFuture(loop=asyncio.get_running_loop())
    late_fut_ref = weakref.ref(late_fut)
    late_fut.add_done_callback(lambda _: setattr(clock, "now", clock.now + 200.0))
    producer_task: asyncio.Task[None] | None = None

    async def fail_late_soon() -> None:
        await asyncio.sleep(0)
        if late_fut is not None:
            late_fut.set_exception(ValueError("late failure"))

    def late_fail_cb(r: Any) -> asyncio.Future[None]:
        nonlocal producer_task
        producer_task = asyncio.create_task(fail_late_soon())
        assert late_fut is not None
        return late_fut

    unhandled_reports: list[dict[str, Any]] = []
    loop = asyncio.get_running_loop()
    old_h = loop.get_exception_handler()
    loop.set_exception_handler(lambda _loop, ctx: unhandled_reports.append(ctx))
    try:
        with Server(lambda request, index: Reply(body=responses[1])) as server:
            async with session("async", server.url) as client:
                res_late = await client.wait_for_review(
                    ORG,
                    REVIEW,
                    timeout=100.0,
                    on_poll=late_fail_cb,
                )
                assert res_late.status == "COMPLETED"
                assert late_fut is not None
                assert late_fut.done()
                assert clock.now >= 200.0
                if producer_task is not None:
                    await producer_task
                await asyncio.sleep(0)
                assert late_fut.exception_retrieved is True
                assert id(late_fut) not in client_module._DETACHED_FUTURES
                late_fut = None
                import gc

                gc.collect()
                assert late_fut_ref() is None
                assert unhandled_reports == []
    finally:
        if producer_task is not None:
            if not producer_task.done():
                producer_task.cancel()
            try:
                await producer_task
            except (asyncio.CancelledError, BaseException):
                pass
        if late_fut is not None:
            if not late_fut.done():
                late_fut.cancel()
            elif not late_fut.cancelled():
                try:
                    late_fut.exception()
                except BaseException:
                    pass
        loop.set_exception_handler(old_h)
