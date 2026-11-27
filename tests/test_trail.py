"""Selection rules of the failed-deploy trail, without HTTP."""

from __future__ import annotations

from typing import Any

import pytest

import proofline
from proofline import ProoflineError, models, trail
from proofline.trail import (
    MAX_EARLIER_COMMITS,
    TrailGap,
    commit_evidence,
    commit_reviews,
    failed_deploy,
    failing_check,
    healthy_deploy,
    trail_commits,
)

from .fixtures import (
    DEPLOY_ENVIRONMENT,
    FAILED_COMMIT,
    HEALTHY_COMMIT,
    MIDDLE_COMMITS,
    OTHER_DEPLOY_ENVIRONMENT,
    PRIVATE,
    assessment,
    code_assessment,
    commit_page,
    deploy,
    finding,
    review,
    summary,
    verifications,
)


def recorded(*deploys: dict[str, Any]) -> models.CommitDeployVerifications:
    return models.CommitDeployVerifications.from_dict(verifications(*deploys))


def test_failed_deploy_is_the_latest_failure_in_the_requested_environment() -> None:
    deploys = recorded(
        deploy("FAILED", task="first", results=()),
        deploy("INCOMPLETE", regressed=True, task="second"),
        deploy("VERIFIED"),
        deploy("FAILED", environment=OTHER_DEPLOY_ENVIRONMENT, task="other", results=()),
    )
    latest = failed_deploy(deploys, None)
    scoped = failed_deploy(deploys, DEPLOY_ENVIRONMENT)
    assert latest is not None and latest.deployment_task == "other"
    assert scoped is not None and scoped.deployment_task == "second"
    assert failed_deploy(recorded(deploy("VERIFIED"), deploy("INCOMPLETE")), None) is None


def test_failing_check_is_the_earliest_regressed_checkpoint() -> None:
    regressed = models.CommitDeploy.from_dict(
        deploy(
            "VERIFIED",
            regressed=True,
            results=("HEALTHY", "INCOMPLETE", "REGRESSED", "REGRESSED"),
        )
    )
    check = failing_check(regressed)
    assert check is not None
    assert check.checkpoint is models.DeployCheckpoint.HOUR_1
    assert check.result == "REGRESSED"
    assert failing_check(models.CommitDeploy.from_dict(deploy("FAILED", results=()))) is None


@pytest.mark.parametrize(
    ("candidate", "matches"),
    [
        (deploy("VERIFIED"), True),
        (deploy("VERIFIED_UNTIL_SUPERSEDED"), True),
        (deploy("VERIFIED", regressed=True), False),
        (deploy("VERIFIED", rolled_back=True), False),
        (deploy("INCOMPLETE"), False),
        (deploy("SUPERSEDED"), False),
        (deploy("NOT_YET_DUE"), False),
        (deploy("LATER_STATE"), False),
        (deploy("VERIFIED", environment=OTHER_DEPLOY_ENVIRONMENT), False),
        (deploy("VERIFIED", task="deploy:web"), False),
        (deploy("VERIFIED", task=None), False),
    ],
)
def test_healthy_deploy_needs_an_unregressed_verification_of_the_same_task(
    candidate: dict[str, Any], matches: bool
) -> None:
    failed = models.CommitDeploy.from_dict(deploy("FAILED", results=()))
    assert (healthy_deploy(recorded(candidate), failed) is not None) is matches


def test_healthy_deploy_is_the_latest_match() -> None:
    failed = models.CommitDeploy.from_dict(deploy("FAILED", results=()))
    found = healthy_deploy(
        recorded(deploy("VERIFIED"), deploy("VERIFIED_UNTIL_SUPERSEDED")), failed
    )
    assert found is not None and found.state == "VERIFIED_UNTIL_SUPERSEDED"


def test_commit_reviews_keep_only_reviews_pinned_to_the_commit() -> None:
    page = models.ReviewPage.from_dict(
        commit_page(
            {**summary(), "head_commit_sha": FAILED_COMMIT},
            {**summary(), "head_commit_sha": FAILED_COMMIT.upper()},
            {**summary(), "head_commit_sha": HEALTHY_COMMIT},
            {**summary(), "head_commit_sha": None},
            summary(),
        )
    )
    kept = commit_reviews(page, FAILED_COMMIT)
    assert [item.head_commit_sha for item in kept] == [FAILED_COMMIT, FAILED_COMMIT.upper()]


def test_commit_evidence_collects_environment_and_code_findings() -> None:
    detail = models.CustomerReviewDetail.from_dict(
        {
            **review(),
            "assessments": [{**assessment(), "findings": [finding()]}],
            "code_assessment": {**code_assessment(), "findings": [finding()]},
        }
    )
    evidence = commit_evidence(FAILED_COMMIT, (), [detail])
    assert (evidence.commit_sha, evidence.deploys, evidence.reviews) == (
        FAILED_COMMIT,
        (),
        (detail,),
    )
    assert [item.claim for item in evidence.findings] == [PRIVATE, PRIVATE]
    assert PRIVATE not in repr(evidence)


@pytest.mark.parametrize(
    ("commit", "earlier"),
    [
        (FAILED_COMMIT[:12], []),
        (FAILED_COMMIT.upper(), []),
        ("f" * 64, []),
        ("g" * 40, []),
        (FAILED_COMMIT, [HEALTHY_COMMIT[:7]]),
        (FAILED_COMMIT, [FAILED_COMMIT]),
        (FAILED_COMMIT, [HEALTHY_COMMIT, HEALTHY_COMMIT]),
        (FAILED_COMMIT, HEALTHY_COMMIT),
        (FAILED_COMMIT, [f"{index:040x}" for index in range(MAX_EARLIER_COMMITS + 1)]),
    ],
)
def test_trail_commits_refuse_anything_but_distinct_full_lowercase_shas(
    commit: str, earlier: Any
) -> None:
    with pytest.raises(ValueError):
        trail_commits(commit, earlier)


def test_trail_commits_keep_the_given_order_up_to_the_bound() -> None:
    assert trail_commits(FAILED_COMMIT, [*MIDDLE_COMMITS, HEALTHY_COMMIT]) == (
        FAILED_COMMIT,
        *MIDDLE_COMMITS,
        HEALTHY_COMMIT,
    )
    bound = [f"{index:040x}" for index in range(MAX_EARLIER_COMMITS)]
    assert trail_commits(FAILED_COMMIT, bound) == (FAILED_COMMIT, *bound)


def test_trail_gap_detaches_the_failed_read() -> None:
    try:
        try:
            raise ValueError(PRIVATE)
        except ValueError:
            raise ProoflineError(0, "urn:proofline:sdk:invalid-response", "static") from None
    except ProoflineError as error:
        gap = TrailGap(FAILED_COMMIT, "DEPLOYS_UNAVAILABLE", error)
    assert gap.error is not None
    assert gap.error.__traceback__ is None
    assert gap.error.__context__ is None
    assert PRIVATE not in repr(gap)


def test_trail_types_are_public() -> None:
    for name in ("CommitEvidence", "FailedDeployTrail", "TrailGap"):
        assert name in proofline.__all__
        assert getattr(proofline, name) is getattr(trail, name)
