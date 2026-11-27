"""Waiting for a commit's deploy verifications against a real loopback peer."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest

from proofline import DeployVerdict, DeployVerificationOutcome, ProoflineError
from proofline import client as client_module

from .fixtures import ORG, REPOSITORY
from .http_server import Reply, Request, Server
from .test_http import MODES, Clock, call, session

SHA = "c" * 40
PRODUCTION = UUID("00000000-0000-4000-8000-000000000010")
STAGING = UUID("00000000-0000-4000-8000-000000000011")
PATH = f"/api/v1/organizations/{ORG}/repositories/{REPOSITORY}/commits/{SHA}/deploy-verifications"
CHECKPOINTS = ("LANDING", "MINUTES_20", "HOUR_1", "DAY_1")
DUE = (
    "2026-11-01T00:05:00Z",
    "2026-11-01T00:25:00Z",
    "2026-11-01T01:05:00Z",
    "2026-11-02T00:05:00Z",
)


def checks(*results: str | None, gaps: dict[int, list[str]] | None = None) -> list[dict[str, Any]]:
    """The four checks in order; a result given as None is not recorded yet."""

    padded = (*results, *(None,) * (4 - len(results)))
    recorded = []
    for index, result in enumerate(padded):
        check: dict[str, Any] = {"checkpoint": CHECKPOINTS[index], "due_at": DUE[index]}
        if result is not None:
            check["result"] = result
            check["gaps"] = (gaps or {}).get(index, [])
        recorded.append(check)
    return recorded


def deploy(
    state: str = "NOT_YET_DUE",
    checkpoints: list[dict[str, Any]] | None = None,
    *,
    environment: UUID = PRODUCTION,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "environment_id": str(environment),
        "state": state,
        "regressed": False,
        "gaps": [],
        "checkpoints": checks("HEALTHY") if checkpoints is None else checkpoints,
        "deploy_url": f"https://proofline.sh/deploys/{environment}",
        **extra,
    }


def verifications(*deploys: dict[str, Any]) -> dict[str, Any]:
    return {"recorded": bool(deploys), "deploys": list(deploys)}


def replies(*bodies: dict[str, Any]) -> Callable[[Request, int], Reply]:
    # The last body answers every read after the scripted ones.
    return lambda request, index: Reply(body=bodies[min(index, len(bodies) - 1)])


def verdicts(result: DeployVerificationOutcome) -> list[tuple[UUID, str, tuple[str, ...]]]:
    return [(item.environment_id, item.status, item.reason_codes) for item in result.deploys]


@MODES
async def test_a_healthy_landing_check_settles_on_the_first_read(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with Server(replies(verifications(deploy()))) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert (result.status, result.reason, result.commit_sha) == ("HEALTHY", None, SHA)
        assert verdicts(result) == [(PRODUCTION, "HEALTHY", ())]
        verdict = result.deploys[0]
        assert isinstance(verdict, DeployVerdict)
        assert verdict.state == "NOT_YET_DUE"
        assert verdict.deploy_url == f"https://proofline.sh/deploys/{PRODUCTION}"
        assert result.verifications.recorded is True
        assert SHA not in repr(result)
        assert [(request.method, request.path) for request in server.requests] == [("GET", PATH)]
        assert clock.delays == []


@MODES
async def test_the_wait_follows_checks_until_the_named_one_records(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    bodies = (
        verifications(deploy(checkpoints=[])),
        verifications(deploy()),
        verifications(deploy(checkpoints=checks("HEALTHY", "HEALTHY"))),
    )
    with Server(replies(*bodies)) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client,
                "wait_for_deploy_verification",
                ORG,
                REPOSITORY,
                SHA,
                through="MINUTES_20",
            )
        assert result.status == "HEALTHY"
        assert len(server.requests) == 3
        assert clock.delays == [5, 10]


@MODES
async def test_a_deploy_recorded_after_the_first_read_still_settles_the_wait(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with Server(replies(verifications(), verifications(deploy()))) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert result.status == "HEALTHY"
        assert clock.delays == [5]


@MODES
async def test_a_regression_ends_the_wait_whatever_check_recorded_it(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    # Staging is still due, and the regression is past the check the caller named.
    body = verifications(
        deploy("UNRECORDED", checks(None), environment=STAGING),
        deploy("INCOMPLETE", checks("HEALTHY", "HEALTHY", "REGRESSED"), regressed=True),
    )
    with Server(replies(body)) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert (result.status, result.reason) == ("REGRESSED", "A deploy of the commit regressed.")
        assert verdicts(result) == [
            (STAGING, "PENDING", ("CHECK_NOT_RECORDED",)),
            (PRODUCTION, "REGRESSED", ("CHECK_REGRESSED",)),
        ]
        assert len(server.requests) == 1
        assert clock.delays == []


@MODES
async def test_a_failed_deploy_fails_once_every_deploy_settles(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    failed = deploy("FAILED", [], environment=STAGING)
    bodies = (
        verifications(failed, deploy(checkpoints=[])),
        verifications(failed, deploy()),
    )
    with Server(replies(*bodies)) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert (result.status, result.reason) == ("FAILED", "A deploy of the commit failed.")
        assert verdicts(result) == [
            (STAGING, "FAILED", ("DEPLOYMENT_FAILED",)),
            (PRODUCTION, "HEALTHY", ()),
        ]
        assert clock.delays == [5]


@pytest.mark.parametrize(
    ("record", "reasons"),
    [
        (
            deploy("INCOMPLETE", checks("HEALTHY", gaps={0: ["SIGNAL_NO_DATA"]})),
            ("SIGNAL_NO_DATA",),
        ),
        (
            deploy("INCOMPLETE", checks("INCOMPLETE", gaps={0: ["RUNTIME_INVENTORY_STALE"]})),
            ("RUNTIME_INVENTORY_STALE", "CHECK_INCOMPLETE"),
        ),
        (
            deploy("UNRECORDED", checks(None), verification_ended=True),
            ("CHECK_NEVER_RECORDED",),
        ),
        (deploy("UNVERIFIED", []), ("DEPLOY_UNVERIFIED",)),
        (deploy("SUPERSEDED", checks("SUPERSEDED")), ("SUPERSEDED_BEFORE_LANDING_CHECK",)),
        (deploy(checkpoints=checks("HEALTHY"), rolled_back=True), ("ROLLED_BACK",)),
        (deploy("LATER_STATE", checks("LATER_RESULT")), ("UNKNOWN_CHECK_RESULT",)),
    ],
    ids=["gap", "incomplete", "never-recorded", "unverified", "superseded", "rolled-back", "later"],
)
@MODES
async def test_an_unproven_deploy_is_incomplete_with_its_reasons(
    mode: str, monkeypatch: pytest.MonkeyPatch, record: dict[str, Any], reasons: tuple[str, ...]
) -> None:
    Clock(monkeypatch)
    with Server(replies(verifications(record))) as server:
        async with session(mode, server.url) as client:
            result = await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert (result.status, result.reason) == ("INCOMPLETE", None)
        assert verdicts(result) == [(PRODUCTION, "INCOMPLETE", reasons)]
        assert len(server.requests) == 1


@MODES
async def test_a_check_replaced_after_a_healthy_landing_counts(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    replaced = deploy(
        "VERIFIED_UNTIL_SUPERSEDED", checks("HEALTHY", "HEALTHY", "SUPERSEDED", "SUPERSEDED")
    )
    with Server(replies(verifications(replaced))) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA, through="DAY_1"
            )
        assert result.status == "HEALTHY"
        assert verdicts(result) == [(PRODUCTION, "HEALTHY", ())]


@MODES
async def test_environment_id_holds_the_wait_to_one_environment(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    staging_only = verifications(deploy(environment=STAGING))
    both = verifications(deploy(environment=STAGING), deploy("FAILED", [], environment=PRODUCTION))
    with Server(replies(staging_only, both)) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client,
                "wait_for_deploy_verification",
                ORG,
                REPOSITORY,
                SHA,
                environment_id=PRODUCTION,
            )
        # Staging's healthy deploy never stands in for the production deploy.
        assert result.status == "FAILED"
        assert verdicts(result) == [(PRODUCTION, "FAILED", ("DEPLOYMENT_FAILED",))]
        assert clock.delays == [5]


@MODES
async def test_a_commit_never_recorded_times_out_and_never_reads_healthy(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    with Server(replies(verifications())) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA, timeout=60
            )
        assert (result.status, result.deploys) == ("TIMED_OUT", ())
        assert result.reason == "No deploy of the commit was recorded."
        assert result.verifications.recorded is False
        assert sum(clock.delays) == 60
        assert clock.delays == [5, 10, 20, 25]


@MODES
async def test_a_check_still_due_at_the_deadline_times_out_with_its_verdict(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    with Server(replies(verifications(deploy(checkpoints=checks(None))))) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA, timeout=10
            )
        assert (result.status, result.reason) == ("TIMED_OUT", None)
        assert verdicts(result) == [(PRODUCTION, "PENDING", ("CHECK_NOT_RECORDED",))]


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"commit_sha": SHA.upper()}, "lowercase"),
        ({"commit_sha": "c" * 12}, "40-character"),
        ({"commit_sha": "main"}, "40-character"),
        ({"commit_sha": "c" * 64}, "40-character"),
        ({"through": "WEEK_1"}, "through"),
        ({"timeout": -1}, "timeout"),
        ({"timeout": float("nan")}, "timeout"),
    ],
)
@MODES
async def test_invalid_arguments_are_refused_before_a_request(
    mode: str, arguments: dict[str, Any], message: str
) -> None:
    with Server(replies(verifications(deploy()))) as server:
        async with session(mode, server.url) as client:
            keywords = dict(arguments)
            commit = keywords.pop("commit_sha", SHA)
            with pytest.raises(ValueError, match=message):
                await call(
                    client, "wait_for_deploy_verification", ORG, REPOSITORY, commit, **keywords
                )
        assert server.requests == []


@MODES
async def test_a_problem_ends_the_wait_as_an_error(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    problem = {"title": "not found", "status": 404, "detail": "No such repository."}
    with Server(
        lambda request, index: Reply(404, problem, {"Content-Type": "application/problem+json"})
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert (raised.value.status, raised.value.title) == (404, "not found")
        assert len(server.requests) == 1


@MODES
async def test_an_inconsistent_ledger_is_an_invalid_response(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    Clock(monkeypatch)
    body = {"recorded": False, "deploys": [deploy()]}
    with Server(replies(body)) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA)
        assert raised.value.type == "urn:proofline:sdk:invalid-response"


@MODES
async def test_the_wait_sleeps_until_the_next_check_is_due(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    landed = datetime(2026, 11, 1, 0, 6, tzinfo=UTC)
    # The wall clock moves with the monotonic one the Clock advances.
    monkeypatch.setattr(
        client_module, "utc_now", lambda: landed + timedelta(seconds=clock.now - 100.0)
    )
    bodies = (
        *(verifications(deploy()),) * 4,
        verifications(deploy(checkpoints=checks("HEALTHY", "HEALTHY"))),
    )
    with Server(replies(*bodies)) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client,
                "wait_for_deploy_verification",
                ORG,
                REPOSITORY,
                SHA,
                through="MINUTES_20",
            )
        assert result.status == "HEALTHY"
        # MINUTES_20 is due 19 minutes after the first read: reads at the five-minute
        # ceiling, then the rest of the way, instead of one read a minute.
        assert clock.delays == [300, 300, 300, 240]
        assert len(server.requests) == 5


@MODES
async def test_an_overdue_check_falls_back_to_backoff(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = Clock(monkeypatch)
    monkeypatch.setattr(client_module, "utc_now", lambda: datetime(2026, 11, 1, 0, 30, tzinfo=UTC))
    bodies = (
        verifications(deploy()),
        verifications(deploy()),
        verifications(deploy(checkpoints=checks("HEALTHY", "HEALTHY"))),
    )
    with Server(replies(*bodies)) as server:
        async with session(mode, server.url) as client:
            result = await call(
                client, "wait_for_deploy_verification", ORG, REPOSITORY, SHA, through="MINUTES_20"
            )
        assert result.status == "HEALTHY"
        assert clock.delays == [5, 10]
