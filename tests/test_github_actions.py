"""Tests for GitHub Actions OIDC auth, renewal, event context, and annotations."""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import anyio
import httpx2
import pytest
from pydantic import SecretStr

from proofline import (
    AssessmentGap,
    AsyncGitHubActionsCredentials,
    AsyncProoflineClient,
    CustomerReviewDetail,
    GitHubActionsCredentials,
    ProoflineClient,
    ProoflineError,
    ReviewOutcome,
    format_github_annotations,
    read_github_actions_event,
)
from tests.fixtures import ORG, REPOSITORY, REVIEW, finding, review, summary
from tests.http_server import Reply, Request, Server

RUNNER_SECRET = "gh_runner_secret_canary_value"
OIDC_JWT_1 = "oidc_jwt_canary_first"
OIDC_JWT_2 = "oidc_jwt_canary_second"
JOB_TOKEN_1 = "plj_job_token_canary_first"
JOB_TOKEN_2 = "plj_job_token_canary_second"
SIG_SECRET = "hmac_sig_canary_never_echo"


class MutableClock:
    def __init__(self, start: float = 0.0, utc_start: datetime | None = None) -> None:
        self.monotonic_now = start
        self.utc_now = utc_start or datetime(2026, 11, 27, 12, 0, 0, tzinfo=UTC)

    def monotonic(self) -> float:
        return self.monotonic_now

    def utc(self) -> datetime:
        return self.utc_now

    def advance(self, seconds: float) -> None:
        self.monotonic_now += seconds
        self.utc_now = self.utc_now + timedelta(seconds=seconds)


def _oidc_env(base_url: str, *, query: str = f"api-version=2.0&sig={SIG_SECRET}") -> dict[str, str]:
    return {
        "GITHUB_ACTIONS": "true",
        "ACTIONS_ID_TOKEN_REQUEST_URL": f"{base_url}/github/token?{query}",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": RUNNER_SECRET,
        "PROOFLINE_BASE_URL": base_url,
    }


def test_sync_from_github_actions_exchanges_renews_and_closes() -> None:
    clock = MutableClock()
    lock = threading.Lock()
    issued = 0
    exchanged = 0
    review_calls = 0

    def respond(request: Request, _index: int) -> Reply:
        nonlocal issued, exchanged, review_calls
        assert "Cookie" not in request.headers
        assert request.headers["Accept-Encoding"] == "identity"
        path = urlsplit(request.path).path
        if request.method == "GET" and path == "/github/token":
            qs = parse_qs(urlsplit(request.path).query)
            assert qs["api-version"] == ["2.0"]
            assert qs["sig"] == [SIG_SECRET]
            assert qs["audience"] == ["proofline"]
            assert request.headers["Authorization"] == f"Bearer {RUNNER_SECRET}"
            with lock:
                issued += 1
                token = OIDC_JWT_1 if issued == 1 else OIDC_JWT_2
            return Reply(200, {"value": token})
        if request.method == "POST" and path == "/api/v1/ci/github-actions/credentials":
            with lock:
                exchanged += 1
                expected_jwt = OIDC_JWT_1 if exchanged == 1 else OIDC_JWT_2
                assert request.headers["Authorization"] == f"Bearer {expected_jwt}"
                assert request.body == b""
                job_token = JOB_TOKEN_1 if exchanged == 1 else JOB_TOKEN_2
            expires = (clock.utc() + timedelta(seconds=100)).isoformat().replace("+00:00", "Z")
            return Reply(
                200,
                {
                    "organization_id": str(ORG),
                    "repository_id": str(REPOSITORY),
                    "token": job_token,
                    "expires_at": expires,
                    "scope": "reviews:read reviews:write",
                },
            )
        if path == f"/api/v1/organizations/{ORG}/reviews":
            return Reply(
                200,
                {
                    "items": [summary()],
                    "filters": {"repositories": [], "environments": [], "authors": []},
                    "truncated": False,
                    "next_cursor": None,
                },
            )
        if request.method == "GET" and path == f"/api/v1/organizations/{ORG}/reviews/{REVIEW}":
            review_calls += 1
            if review_calls == 1:
                assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_1}"
                clock.advance(49.0)
                return Reply(200, review("RUNNING"))
            clock.advance(2.0)
            return Reply(200, review("RUNNING") if review_calls == 2 else review("COMPLETED"))
        if request.method == "POST" and path == "/mcp":
            assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_2}"
            payload = json.loads(request.body)
            if payload["method"] == "initialize":
                return Reply(
                    200,
                    {
                        "jsonrpc": "2.0",
                        "id": payload["id"],
                        "result": {"protocolVersion": "2025-11-25"},
                    },
                )
            if payload["method"] == "notifications/initialized":
                return Reply(202, b"")
            return Reply(
                200,
                {
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "result": {
                        "content": [{"type": "text", "text": "ok"}],
                        "structuredContent": {"items": []},
                    },
                },
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.path}")

    with Server(respond) as server:
        creds = GitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        )
        creds.exchange()
        with ProoflineClient(creds) as client:
            assert client.organization_id == ORG
            assert client.repository_id == REPOSITORY
            assert repr(creds) == f"GitHubActionsCredentials(base_url={server.url!r})"
            assert JOB_TOKEN_1 not in repr(client._api)

            # First read uses plj_1, advances clock to 49s (still < 50s half-life).
            first = client.get_review(ORG, REVIEW)
            assert first.status == "RUNNING"
            assert exchanged == 1

            # Second read happens at 49s -> server advances clock to 51s, still on plj_1.
            second = client.get_review(ORG, REVIEW)
            assert second.status == "RUNNING"
            assert exchanged == 1

            # Next read starts at 51s (>= 50s half-life): renews once to plj_2!
            third = client.get_review(ORG, REVIEW)
            assert third.status == "COMPLETED"
            assert exchanged == 2

            # Immediate next call within new 50s window reuses plj_2 without exchanging.
            client.mcp.list_organizations()
            assert exchanged == 2

            rev_requests = [
                r.headers["Authorization"]
                for r in server.requests
                if urlsplit(r.path).path == f"/api/v1/organizations/{ORG}/reviews/{REVIEW}"
            ]
            assert rev_requests == [
                f"Bearer {JOB_TOKEN_1}",
                f"Bearer {JOB_TOKEN_1}",
                f"Bearer {JOB_TOKEN_2}",
            ]
        creds.close()


def test_sync_from_github_actions_factory_owns_and_closes_session() -> None:
    def respond(request: Request, _index: int) -> Reply:
        path = urlsplit(request.path).path
        if path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1})
        if path == "/api/v1/ci/github-actions/credentials":
            return Reply(
                200,
                {
                    "organization_id": str(ORG),
                    "repository_id": str(REPOSITORY),
                    "token": JOB_TOKEN_1,
                    "expires_at": "2026-11-27T13:00:00+00:00",
                },
            )
        if path == f"/api/v1/organizations/{ORG}/reviews":
            return Reply(
                200,
                {
                    "items": [summary()],
                    "filters": {"repositories": [], "environments": [], "authors": []},
                    "truncated": False,
                    "next_cursor": None,
                },
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.path}")

    with Server(respond) as server:
        with ProoflineClient.from_github_actions(environ=_oidc_env(server.url)) as client:
            assert client.organization_id == ORG
            assert client.repository_id == REPOSITORY
            page = client.list_reviews(ORG)
            assert len(page.items) == 1
        assert isinstance(client._token_source, GitHubActionsCredentials)
        assert client._token_source._http.is_closed


async def test_async_from_github_actions_single_flight_renewal() -> None:
    clock = MutableClock()
    exchanged = 0

    def respond(request: Request, _index: int) -> Reply:
        nonlocal exchanged
        path = urlsplit(request.path).path
        if request.method == "GET" and path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1 if exchanged == 0 else OIDC_JWT_2})
        if request.method == "POST" and path == "/api/v1/ci/github-actions/credentials":
            exchanged += 1
            expires = (clock.utc() + timedelta(seconds=3600)).isoformat()
            return Reply(
                200,
                {
                    "organization_id": str(ORG),
                    "token": JOB_TOKEN_1 if exchanged == 1 else JOB_TOKEN_2,
                    "expires_at": expires,
                },
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.path}")

    with Server(respond) as server:
        creds = AsyncGitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        )
        await creds.aexchange()
        assert exchanged == 1
        assert creds.repository_id is None

        # Fire concurrent calls past renewal threshold (3600 - 60 = 3540s).
        clock.advance(3545.0)
        async with anyio.create_task_group() as group:
            tokens: list[SecretStr] = []

            async def grab() -> None:
                tokens.append(await creds.atoken())

            for _ in range(5):
                group.start_soon(grab)

        assert exchanged == 2
        assert all(tok.get_secret_value() == JOB_TOKEN_2 for tok in tokens)
        await creds.aclose()


async def test_async_wait_for_review_renews_lease(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = MutableClock()
    exchanged = 0
    polls = 0

    def respond(request: Request, _index: int) -> Reply:
        nonlocal exchanged, polls
        path = urlsplit(request.path).path
        if request.method == "GET" and path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1 if exchanged == 0 else OIDC_JWT_2})
        if request.method == "POST" and path == "/api/v1/ci/github-actions/credentials":
            exchanged += 1
            expires = (clock.utc() + timedelta(seconds=3600)).isoformat()
            return Reply(
                200,
                {
                    "organization_id": str(ORG),
                    "token": JOB_TOKEN_1 if exchanged == 1 else JOB_TOKEN_2,
                    "expires_at": expires,
                },
            )
        if path == f"/api/v1/organizations/{ORG}/reviews":
            return Reply(
                200,
                {
                    "items": [summary()],
                    "filters": {"repositories": [], "environments": [], "authors": []},
                    "truncated": False,
                    "next_cursor": None,
                },
            )
        if request.method == "GET" and path == f"/api/v1/organizations/{ORG}/reviews/{REVIEW}":
            polls += 1
            if polls == 1:
                assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_1}"
                # Advance past 3600 - 60 = 3540s renewal threshold for next poll.
                clock.advance(3545.0)
                return Reply(200, review("RUNNING"))
            assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_2}"
            return Reply(200, review("COMPLETED"))
        raise AssertionError(f"Unexpected request: {request.method} {request.path}")

    async def fast_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr("proofline.client.async_sleep", fast_sleep)

    with Server(respond) as server:
        async with await AsyncProoflineClient.from_github_actions(
            environ=_oidc_env(server.url)
        ) as client:
            assert client.organization_id == ORG
            assert client.repository_id is None
            page = await client.list_reviews(ORG)
            assert len(page.items) == 1
        assert isinstance(client._token_source, AsyncGitHubActionsCredentials)
        assert client._token_source._http.is_closed

    exchanged = 0
    polls = 0
    with Server(respond) as server:
        creds = AsyncGitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        )
        await creds.aexchange()
        async with AsyncProoflineClient(creds) as client:
            outcome = await client.wait_for_review(ORG, REVIEW, timeout=60.0)
            assert outcome.status == "COMPLETED"
            assert exchanged == 2
        await creds.aclose()


def test_sync_concurrent_renewal_single_flight() -> None:
    clock = MutableClock()
    lock = threading.Lock()
    exchanged = 0

    def respond(request: Request, _index: int) -> Reply:
        nonlocal exchanged
        path = urlsplit(request.path).path
        if path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1})
        if path == "/api/v1/ci/github-actions/credentials":
            with lock:
                exchanged += 1
                num = exchanged
            expires = (clock.utc() + timedelta(seconds=100)).isoformat()
            return Reply(
                200, {"organization_id": str(ORG), "token": f"plj_{num}", "expires_at": expires}
            )
        raise AssertionError(path)

    with Server(respond) as server:
        with GitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        ) as creds:
            creds.exchange()
            clock.advance(55.0)
            with ThreadPoolExecutor(max_workers=6) as pool:
                results = [
                    fut.result().get_secret_value()
                    for fut in [pool.submit(creds.token) for _ in range(6)]
                ]
            assert exchanged == 2
            assert set(results) == {"plj_2"}


def test_retry_after_refreshes_authorization_when_sleeping_past_renewal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = MutableClock()
    exchanged = 0
    review_calls = 0

    def respond(request: Request, _index: int) -> Reply:
        nonlocal exchanged, review_calls
        path = urlsplit(request.path).path
        if path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1 if exchanged == 0 else OIDC_JWT_2})
        if path == "/api/v1/ci/github-actions/credentials":
            exchanged += 1
            expires = (clock.utc() + timedelta(seconds=100)).isoformat()
            return Reply(
                200,
                {
                    "organization_id": str(ORG),
                    "token": JOB_TOKEN_1 if exchanged == 1 else JOB_TOKEN_2,
                    "expires_at": expires,
                },
            )
        if path == f"/api/v1/organizations/{ORG}/reviews/{REVIEW}":
            review_calls += 1
            if review_calls == 1:
                assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_1}"
                return Reply(503, {"detail": "busy"}, headers={"Retry-After": "1"})
            assert request.headers["Authorization"] == f"Bearer {JOB_TOKEN_2}"
            return Reply(200, review("COMPLETED"))
        raise AssertionError(path)

    def advance_on_sleep(seconds: float) -> None:
        clock.advance(60.0 + seconds)

    monkeypatch.setattr("proofline._transport.sleep", advance_on_sleep)

    with Server(respond) as server:
        creds = GitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        )
        creds.exchange()
        with ProoflineClient(creds) as client:
            result = client.get_review(ORG, REVIEW)
            assert result.status == "COMPLETED"
            assert exchanged == 2
        creds.close()


def test_security_redaction_no_sig_leak_and_org_mismatch_refusal() -> None:
    exchanged = 0
    other_org = UUID("00000000-0000-4000-8000-000000000099")
    clock = MutableClock()

    def respond_fail_exchange(request: Request, _index: int) -> Reply:
        path = urlsplit(request.path).path
        if path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1})
        if path == "/api/v1/ci/github-actions/credentials":
            return Reply(
                403,
                {
                    "detail": f"denied runner={RUNNER_SECRET} jwt={OIDC_JWT_1} old={JOB_TOKEN_1}",
                },
            )
        raise AssertionError(path)

    with Server(respond_fail_exchange) as server:
        with pytest.raises(ProoflineError) as err:
            ProoflineClient.from_github_actions(environ=_oidc_env(server.url))
        assert err.value.status == 403
        assert RUNNER_SECRET not in err.value.detail
        assert OIDC_JWT_1 not in err.value.detail
        assert SIG_SECRET not in str(err.value)
        assert SIG_SECRET not in err.value.detail

    def respond_oidc_status_error(_request: Request, _index: int) -> Reply:
        return Reply(502, f"upstream echo {SIG_SECRET} {RUNNER_SECRET}")

    with Server(respond_oidc_status_error) as server:
        with pytest.raises(ProoflineError) as err:
            ProoflineClient.from_github_actions(environ=_oidc_env(server.url))
        assert err.value.status == 502
        assert SIG_SECRET not in err.value.detail
        assert RUNNER_SECRET not in err.value.detail
        assert "?sig=" not in err.value.detail

    def respond_org_shift(request: Request, _index: int) -> Reply:
        nonlocal exchanged
        path = urlsplit(request.path).path
        if path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1})
        if path == "/api/v1/ci/github-actions/credentials":
            exchanged += 1
            org_value = ORG if exchanged == 1 else other_org
            expires = (clock.utc() + timedelta(seconds=100)).isoformat()
            return Reply(
                200,
                {"organization_id": str(org_value), "token": JOB_TOKEN_1, "expires_at": expires},
            )
        raise AssertionError(path)

    with Server(respond_org_shift) as server:
        with GitHubActionsCredentials.from_env(
            environ=_oidc_env(server.url),
            monotonic_clock=clock.monotonic,
            utc_now=clock.utc,
        ) as creds:
            creds.exchange()
            clock.advance(60.0)
            with pytest.raises(ProoflineError) as err:
                creds.token()
            assert err.value.type == "urn:proofline:sdk:credential-mismatch"
            assert creds.organization_id == ORG


def test_exchange_rejects_redirects_encoding_naive_dates_and_mismatched_clients() -> None:
    def respond_redirect(request: Request, _index: int) -> Reply:
        return Reply(302, "", headers={"Location": "https://attacker.example/steal"})

    with Server(respond_redirect) as server:
        with pytest.raises(ProoflineError) as err:
            ProoflineClient.from_github_actions(environ=_oidc_env(server.url))
        assert "redirect" in err.value.type

    def respond_naive_expiry(request: Request, _index: int) -> Reply:
        if urlsplit(request.path).path == "/github/token":
            return Reply(200, {"value": OIDC_JWT_1})
        return Reply(
            200,
            {
                "organization_id": str(ORG),
                "token": JOB_TOKEN_1,
                "expires_at": "2026-11-27T13:00:00",
            },
        )

    with Server(respond_naive_expiry) as server:
        with pytest.raises(ProoflineError) as err:
            ProoflineClient.from_github_actions(environ=_oidc_env(server.url))
        assert err.value.type == "urn:proofline:sdk:invalid-response"

    # Environment & type validation checks
    with pytest.raises(ValueError):
        GitHubActionsCredentials.from_env(environ={"GITHUB_ACTIONS": "false"})
    with pytest.raises(ValueError):
        GitHubActionsCredentials.from_env(
            environ={
                "GITHUB_ACTIONS": "true",
                "ACTIONS_ID_TOKEN_REQUEST_URL": "http://example.com/github/token",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": RUNNER_SECRET,
            }
        )
    with pytest.raises(ValueError):
        GitHubActionsCredentials.from_env(
            environ={
                "GITHUB_ACTIONS": "true",
                "ACTIONS_ID_TOKEN_REQUEST_URL": "https://user:pass@token.actions.githubusercontent.com/t",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": RUNNER_SECRET,
            }
        )

    sync_creds = GitHubActionsCredentials(
        request_url="https://token.actions.githubusercontent.com/t",
        request_token=RUNNER_SECRET,
        base_url="https://proofline.sh",
    )
    async_creds = AsyncGitHubActionsCredentials(
        request_url="https://token.actions.githubusercontent.com/t",
        request_token=RUNNER_SECRET,
        base_url="https://proofline.sh",
    )
    with pytest.raises(TypeError):
        AsyncProoflineClient(sync_creds)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ProoflineClient(async_creds)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ProoflineClient(sync_creds, base_url="https://other.example")
    sync_creds.close()


def test_read_github_actions_event_extracts_commits_and_guards_payloads(tmp_path: Path) -> None:
    assert read_github_actions_event({}) is None

    pr_sha = "1" * 40
    merge_sha = "2" * 40
    pr_event = tmp_path / "pr.json"
    pr_event.write_text(
        json.dumps({"pull_request": {"number": 42, "head": {"sha": pr_sha.upper()}}}),
        encoding="utf-8",
    )
    event = read_github_actions_event(
        {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REPOSITORY": "acme/web",
            "GITHUB_SHA": merge_sha,
            "GITHUB_EVENT_PATH": str(pr_event),
        }
    )
    assert event is not None
    assert event.pull_request_number == 42
    assert event.commit_under_test == pr_sha

    wr_sha = "3" * 40
    wr_event = tmp_path / "wr.json"
    wr_event.write_text(
        json.dumps({"workflow_run": {"id": 999, "run_attempt": 2, "head_sha": wr_sha}}),
        encoding="utf-8",
    )
    wr = read_github_actions_event(
        {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "workflow_run",
            "GITHUB_SHA": merge_sha,
            "GITHUB_EVENT_PATH": str(wr_event),
        }
    )
    assert wr is not None
    assert wr.commit_under_test == wr_sha
    assert wr.workflow_run_id == 999
    assert wr.workflow_run_attempt == 2

    push_ev = read_github_actions_event(
        {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "push", "GITHUB_SHA": wr_sha}
    )
    assert push_ev is not None
    assert push_ev.commit_under_test == wr_sha

    bad_event = tmp_path / "bad.json"
    bad_event.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError):
        read_github_actions_event(
            {
                "GITHUB_ACTIONS": "true",
                "GITHUB_EVENT_NAME": "pull_request",
                "GITHUB_EVENT_PATH": str(bad_event),
            }
        )


def test_format_github_annotations_sanitizes_sorts_and_flags_gaps() -> None:
    head = "a" * 40
    stale = "b" * 40
    base = review("INCOMPLETE")
    base["head_commit_sha"] = head
    base["assessments"][0]["status"] = "INCOMPLETE"
    base["assessments"][0]["incompleteness_kind"] = "EVIDENCE_UNAVAILABLE"

    f_warn = finding()
    f_warn["id"] = "00000000-0000-4000-8000-000000000010"
    f_warn["severity"] = "WARNING"
    f_warn["risk_domain"] = "RELIABILITY"
    f_warn["claim"] = "Minor retry issue\x1b[31m\n::add-mask::secret\u202e"
    f_warn["impact"] = "Line 2, 100% impact"
    f_warn["evidence_refs"] = [
        {
            "kind": "repository_file",
            "label": "src/a.py:10",
            "provenance_status": "VERIFIED_REPOSITORY_READ",
            "repository_path": "../escape.py",
            "start_line": 1,
        },
        {
            "kind": "repository_file",
            "label": "other/b.py:2",
            "provenance_status": "VERIFIED_REPOSITORY_READ",
            "companion_repository": "acme/other",
            "repository_path": "b.py",
            "start_line": 2,
        },
        {
            "kind": "repository_file",
            "label": "src/good,name:1.py:12-15",
            "provenance_status": "VERIFIED_REPOSITORY_READ",
            "repository_path": "src/good,name:1.py",
            "start_line": 12,
            "end_line": 15,
            "commit_sha": head,
        },
    ]

    f_serious = finding()
    f_serious["id"] = "00000000-0000-4000-8000-000000000011"
    f_serious["severity"] = "SERIOUS"
    f_serious["risk_domain"] = "SECURITY"
    f_serious["claim"] = "Auth check skipped"
    f_serious["evidence_refs"] = [
        {
            "kind": "repository_file",
            "label": "old",
            "provenance_status": "VERIFIED_REPOSITORY_READ",
            "repository_path": "src/auth.py",
            "start_line": 99,
            "commit_sha": stale,
        }
    ]

    f_resolved = finding()
    f_resolved["id"] = "00000000-0000-4000-8000-000000000012"
    f_resolved["lifecycle_state"] = "RESOLVED"
    f_resolved["claim"] = "Already fixed"

    f_withheld = finding()
    f_withheld["id"] = "00000000-0000-4000-8000-000000000013"
    f_withheld["risk_domain"] = "[withheld: environment value]"
    f_withheld["claim"] = "Hidden secret"

    base["assessments"][0]["findings"] = [f_warn, f_resolved, f_serious, f_withheld]
    detail = CustomerReviewDetail.from_dict(base)
    outcome_obj = ReviewOutcome(
        status="INCOMPLETE",
        review_url="https://proofline.sh/orgs/by-id/o/reviews/r",
        review=detail,
        gaps=(
            AssessmentGap(
                UUID("00000000-0000-4000-8000-000000000004"),
                "INCOMPLETE",
                ("EVIDENCE_UNAVAILABLE",),
            ),
        ),
    )

    rendered = format_github_annotations(outcome_obj, head_commit_sha=head)
    lines = rendered.splitlines()
    assert len(lines) == 3
    # Serious comes first and is unpinned because stale commit SHA did not match head.
    assert lines[0].startswith("::error title=Proofline SERIOUS (SECURITY)::Auth check skipped")
    assert "file=" not in lines[0]
    # Warning comes second on the validated non-companion relative path with escaped fields.
    expected_prefix = (
        "::warning file=src/good%2Cname%3A1.py,line=12,endLine=15,"
        "title=Proofline WARNING (RELIABILITY)::"
    )
    assert lines[1].startswith(expected_prefix)
    assert "\x1b" not in lines[1]
    assert "\u202e" not in lines[1]
    assert "%0A::add-mask" in lines[1]
    assert "100%25 impact" in lines[1]
    assert "Already fixed" not in rendered
    assert "Hidden secret" not in rendered
    # Incomplete review emits an explicit warning annotation.
    assert lines[2].startswith(
        "::warning title=Proofline review INCOMPLETE::"
        "status=INCOMPLETE; reasons=EVIDENCE_UNAVAILABLE"
    )


def test_format_github_annotations_handles_no_review_and_code_lane() -> None:
    empty_outcome = ReviewOutcome(
        status="TIMED_OUT",
        review_url="https://proofline.sh/orgs/by-id/o/reviews/r",
        review=None,
        reason="Timed out waiting for review.",
    )
    rendered_empty = format_github_annotations(empty_outcome)
    assert rendered_empty.startswith("::warning title=Proofline review TIMED_OUT::")
    assert "Timed out waiting for review." in rendered_empty

    completed_empty = ReviewOutcome(
        status="COMPLETED",
        review_url="https://proofline.sh/orgs/by-id/o/reviews/r",
        review=CustomerReviewDetail.from_dict(review("COMPLETED")),
    )
    assert format_github_annotations(completed_empty) == ""

    code_finding = finding()
    code_finding["severity"] = "SERIOUS"
    code_finding["risk_domain"] = "SECURITY"
    code_finding["claim"] = "Missing check in code lane"
    code_review = review("COMPLETED")
    code_review["assessment_count"] = 0
    code_review["assessments"] = []
    code_review["code_assessment"] = {
        "id": "00000000-0000-4000-8000-000000000006",
        "status": "COMPLETED",
        "head_commit_sha": "a" * 40,
        "base_commit_sha": "b" * 40,
        "findings": [code_finding],
        "incompleteness_kind": None,
    }
    code_outcome = ReviewOutcome(
        status="COMPLETED",
        review_url="https://proofline.sh/orgs/by-id/o/reviews/r",
        review=CustomerReviewDetail.from_dict(code_review),
    )
    code_rendered = format_github_annotations(code_outcome)
    assert code_rendered.startswith(
        "::error title=Proofline SERIOUS (SECURITY)::Missing check in code lane"
    )


def test_transport_exception_type_used_on_socket_failure() -> None:
    with GitHubActionsCredentials(
        request_url="https://127.0.0.1:1/github/token?sig=secret_sig",
        request_token=RUNNER_SECRET,
        base_url="https://127.0.0.1:1",
        timeout=0.5,
    ) as creds:
        # Force real connect failure via invalid endpoint / httpx2.HTTPError simulation
        creds._http.close()

        class FailingTransport(httpx2.BaseTransport):
            def handle_request(self, request: httpx2.Request) -> httpx2.Response:
                raise httpx2.ConnectError(f"failed {request.url}", request=request)

        creds._http = httpx2.Client(transport=FailingTransport(), timeout=0.5)
        with pytest.raises(ProoflineError) as err:
            creds.exchange()
        assert err.value.type == "urn:proofline:sdk:transport"
        assert "secret_sig" not in err.value.detail
        assert "?sig=" not in err.value.detail
