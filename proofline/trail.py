"""Evidence for a failed deploy: its failing check, last healthy deploy and the commits between."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from ._generated.models.commit_deploy import CommitDeploy
from ._generated.models.commit_deploy_verifications import CommitDeployVerifications
from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.deploy_coverage_checkpoint import DeployCoverageCheckpoint
from ._generated.models.review_page import ReviewPage
from ._generated.models.review_summary import ReviewSummary
from ._transport import ProoflineError

TrailGapReason = Literal[
    "COMMIT_NOT_RECORDED",
    "NO_FAILED_DEPLOY",
    "NO_FAILING_CHECK",
    "NO_HEALTHY_DEPLOY",
    "DEPLOYS_UNAVAILABLE",
    "REVIEWS_UNAVAILABLE",
    "REVIEWS_TRUNCATED",
    "REVIEW_UNAVAILABLE",
]
MAX_EARLIER_COMMITS = 50
_HEALTHY_STATES = frozenset(("VERIFIED", "VERIFIED_UNTIL_SUPERSEDED"))
_LOWER_HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class TrailGap:
    """What the trail could not establish for one commit.

    error is the ProoflineError of the read that failed, when a read failed.
    """

    commit_sha: str
    reason: TrailGapReason
    error: ProoflineError | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # A gap outlives its failed read; the error must not keep that read's frames or body.
        if self.error is not None:
            self.error.__traceback__ = None
            self.error.__context__ = None


@dataclass(frozen=True)
class CommitEvidence:
    """One commit of the range with its recorded deploys, reviews and their findings."""

    commit_sha: str
    deploys: tuple[CommitDeploy, ...] = field(repr=False)
    reviews: tuple[CustomerReviewDetail, ...] = field(repr=False)
    findings: tuple[CustomerFinding, ...] = field(repr=False)


@dataclass(frozen=True)
class FailedDeployTrail:
    """The evidence around a commit whose deploy failed.

    commit_range starts with the failed commit and runs back, newest first, to the
    commit just after healthy_commit_sha, or to the last earlier commit read when no
    healthy deploy was found. gaps names everything the trail could not establish.
    """

    commit_sha: str
    failed_deploy: CommitDeploy | None = field(repr=False)
    failing_check: DeployCoverageCheckpoint | None = field(repr=False)
    healthy_commit_sha: str | None
    healthy_deploy: CommitDeploy | None = field(repr=False)
    commit_range: tuple[CommitEvidence, ...] = field(repr=False)
    gaps: tuple[TrailGap, ...]


def _commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40 or not set(value) <= _LOWER_HEX:
        raise ValueError("A trail commit must be a full 40-character lowercase hexadecimal SHA.")
    return value


def trail_commits(commit_sha: str, earlier_commits: Sequence[str]) -> tuple[str, ...]:
    # The deploy route accepts only full lowercase SHA-1s, and each commit costs a request.
    if isinstance(earlier_commits, str) or len(earlier_commits) > MAX_EARLIER_COMMITS:
        raise ValueError(
            f"earlier_commits takes a sequence of at most {MAX_EARLIER_COMMITS} commit SHAs."
        )
    commits = (_commit(commit_sha), *(_commit(sha) for sha in earlier_commits))
    if len(set(commits)) != len(commits):
        raise ValueError("A commit can appear only once in a trail.")
    return commits


def failed_deploy(
    verifications: CommitDeployVerifications, environment_id: UUID | None
) -> CommitDeploy | None:
    # Deploys are listed earliest landing first, so the last match is the latest failure.
    failures = [
        deploy
        for deploy in verifications.deploys
        if (environment_id is None or deploy.environment_id == environment_id)
        and (deploy.state == "FAILED" or deploy.regressed is True)
    ]
    return failures[-1] if failures else None


def failing_check(deploy: CommitDeploy) -> DeployCoverageCheckpoint | None:
    # The four checks are listed in order, so this is the earliest regression.
    return next((check for check in deploy.checkpoints if check.result == "REGRESSED"), None)


def healthy_deploy(
    verifications: CommitDeployVerifications, failed: CommitDeploy
) -> CommitDeploy | None:
    matches = [
        deploy
        for deploy in verifications.deploys
        if deploy.environment_id == failed.environment_id
        and _task(deploy) == _task(failed)
        and deploy.state in _HEALTHY_STATES
        and deploy.regressed is False
        and deploy.rolled_back is not True
    ]
    return matches[-1] if matches else None


def _task(deploy: CommitDeploy) -> str | None:
    return deploy.deployment_task if isinstance(deploy.deployment_task, str) else None


def commit_reviews(pages: Sequence[ReviewPage], commit_sha: str) -> list[ReviewSummary]:
    # A review is evidence only for the head commit it is pinned to, and is read once.
    found: dict[UUID, ReviewSummary] = {}
    for page in pages:
        for summary in page.items:
            if (
                isinstance(summary.head_commit_sha, str)
                and summary.head_commit_sha.lower() == commit_sha
            ):
                found.setdefault(summary.id, summary)
    return list(found.values())


def commit_evidence(
    commit_sha: str, deploys: tuple[CommitDeploy, ...], reviews: list[CustomerReviewDetail]
) -> CommitEvidence:
    findings = [finding for review in reviews for finding in _findings(review)]
    return CommitEvidence(commit_sha, deploys, tuple(reviews), tuple(findings))


def _findings(review: CustomerReviewDetail) -> list[CustomerFinding]:
    findings = [finding for assessment in review.assessments for finding in assessment.findings]
    if isinstance(review.code_assessment, CustomerCodeAssessment):
        findings.extend(review.code_assessment.findings)
    return findings
