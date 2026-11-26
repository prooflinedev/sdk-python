"""Deploy verification follows the checks Proofline recorded for one commit's deploys.

The rules match `proofline ci deploy`: a result is "no regression observed",
never a claim about the deploy itself, and anything Proofline did not
establish reads as INCOMPLETE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from ._generated.models.commit_deploy import CommitDeploy
from ._generated.models.commit_deploy_verifications import CommitDeployVerifications
from ._generated.models.deploy_checkpoint import DeployCheckpoint
from ._generated.types import Unset
from ._transport import invalid_response

Checkpoint = Literal["LANDING", "MINUTES_20", "HOUR_1", "DAY_1"]
DeployStatus = Literal["NO_REGRESSION", "REGRESSED", "INCOMPLETE", "TIMED_OUT"]
ReadingKind = Literal[
    "REGRESSED",
    "WAITING",
    "SUPERSEDED",
    "UNVERIFIED",
    "INACTIVE",
    "ENDED",
    "NOT_ESTABLISHED",
    "UNKNOWN_STATE",
    "NO_REGRESSION",
]

CHECKPOINTS: tuple[Checkpoint, ...] = ("LANDING", "MINUTES_20", "HOUR_1", "DAY_1")
# A state a newer server adds may mean what no check here shows.
KNOWN_STATES = frozenset(
    (
        "VERIFIED",
        "VERIFIED_UNTIL_SUPERSEDED",
        "SUPERSEDED",
        "INCOMPLETE",
        "UNRECORDED",
        "NOT_YET_DUE",
        "UNVERIFIED",
        "FAILED",
        "INACTIVE",
    )
)
_REASONS: dict[str, str] = {
    "UNKNOWN_STATE": "A selected deploy reads a state this SDK does not know.",
    "INACTIVE": "A selected deploy never landed, so the {until} check will not be recorded.",
    "SUPERSEDED": "A later deploy replaced a selected deploy before the {until} check.",
    "ENDED": "Deploy checks ended without recording the {until} check.",
    "UNVERIFIED": "Proofline has no deploy checks of a selected deploy.",
    "NOT_ESTABLISHED": "A check through {until} did not record HEALTHY, or names a gap.",
}


@dataclass(frozen=True)
class DeploySelector:
    """Which deploys of the commit count. Fields left as None match every deploy."""

    environment_id: UUID | None = None
    github_environment: str | None = None
    deployment_task: str | None = None
    github_deployment_id: int | None = None
    workflow_run_id: int | None = None
    workflow_run_attempt: int | None = None
    aws_run_id: str | None = None

    def __post_init__(self) -> None:
        if self.workflow_run_attempt is not None and self.workflow_run_id is None:
            raise ValueError("workflow_run_attempt names an attempt of workflow_run_id.")

    def selects(self, deploy: CommitDeploy) -> bool:
        def same(wanted: object, value: object) -> bool:
            return wanted is None or wanted == value

        def holds(wanted: int | None, values: object) -> bool:
            # A deploy that lists no IDs or attempts never matches one.
            return wanted is None or (isinstance(values, list) and wanted in values)

        return (
            same(self.environment_id, deploy.environment_id)
            and same(self.github_environment, deploy.github_environment)
            and same(self.deployment_task, deploy.deployment_task)
            and same(self.workflow_run_id, deploy.workflow_run_id)
            and same(self.aws_run_id, deploy.aws_run_id)
            and holds(self.github_deployment_id, deploy.github_deployment_ids)
            and holds(self.workflow_run_attempt, deploy.workflow_run_attempts)
        )


@dataclass(frozen=True)
class DeployReading:
    """What one selected deploy's checks through the target checkpoint say."""

    deploy: CommitDeploy = field(repr=False)
    reading: ReadingKind


@dataclass(frozen=True)
class DeployVerificationOutcome:
    status: DeployStatus
    checkpoint: Checkpoint
    readings: tuple[DeployReading, ...] = ()
    verifications: CommitDeployVerifications | None = field(default=None, repr=False)
    reason: str | None = None


def checkpoint_name(value: str) -> Checkpoint:
    if value not in CHECKPOINTS:
        raise ValueError("until must be LANDING, MINUTES_20, HOUR_1 or DAY_1.")
    return CHECKPOINTS[CHECKPOINTS.index(value)]


def _check(deploy: CommitDeploy, at: Checkpoint) -> tuple[str | None, tuple[str, ...]]:
    # Older servers report only the deploy-wide gaps.
    for check in deploy.checkpoints:
        if check.checkpoint == at:
            result = check.result if isinstance(check.result, str) else None
            gaps = check.gaps if isinstance(check.gaps, list) else deploy.gaps
            return result, tuple(gaps)
    return None, tuple(deploy.gaps)


def _read(deploy: CommitDeploy, until: Checkpoint) -> ReadingKind:
    through = CHECKPOINTS[: CHECKPOINTS.index(until) + 1]
    # A regression at any checkpoint, even a later one, decides first.
    if (
        deploy.state == "FAILED"
        or deploy.regressed
        or any(check.result == "REGRESSED" for check in deploy.checkpoints)
    ):
        return "REGRESSED"
    if deploy.state == "UNVERIFIED":
        return "UNVERIFIED"
    if deploy.state == "INACTIVE":
        return "INACTIVE"
    if any(_check(deploy, at)[0] == "SUPERSEDED" for at in through):
        return "SUPERSEDED"
    if _check(deploy, until)[0] is None:
        return "ENDED" if deploy.verification_ended is True else "WAITING"
    if deploy.state not in KNOWN_STATES:
        return "UNKNOWN_STATE"
    if all(_check(deploy, at) == ("HEALTHY", ()) for at in through):
        return "NO_REGRESSION"
    return "NOT_ESTABLISHED"


def _validate(verifications: CommitDeployVerifications) -> None:
    if not isinstance(verifications, CommitDeployVerifications) or not isinstance(
        verifications.deploys, list
    ):
        raise invalid_response()
    for deploy in verifications.deploys:
        if (
            not isinstance(deploy, CommitDeploy)
            or not isinstance(deploy.state, str)
            or type(deploy.regressed) is not bool
            or not isinstance(deploy.checkpoints, list)
            or not isinstance(deploy.gaps, list)
            or any(not isinstance(gap, str) for gap in deploy.gaps)
            or any(not isinstance(check.result, str | Unset | None) for check in deploy.checkpoints)
        ):
            raise invalid_response()


def conclude(
    verifications: CommitDeployVerifications | None,
    until: Checkpoint,
    selector: DeploySelector | None,
    pending: Literal["INCOMPLETE", "TIMED_OUT"] | None,
) -> DeployVerificationOutcome | None:
    """The outcome of one read; None while a check may still come and pending is None."""
    if verifications is None:
        if pending is None:
            return None
        return DeployVerificationOutcome(pending, until, reason="No deploy read is available.")
    _validate(verifications)
    readings = tuple(
        DeployReading(deploy, _read(deploy, until))
        for deploy in verifications.deploys
        if selector is None or selector.selects(deploy)
    )
    kinds = {reading.reading for reading in readings}
    status: DeployStatus
    if "REGRESSED" in kinds:
        status, reason = "REGRESSED", "A selected deploy failed or a check recorded REGRESSED."
    elif not readings or "WAITING" in kinds:
        if pending is None:
            return None
        status = pending
        if readings:
            reason = f"The {until} check is not recorded."
        elif verifications.deploys:
            reason = "No recorded deploy matches the selector."
        else:
            reason = "No deploy of the commit is recorded."
    elif kinds == {"NO_REGRESSION"}:
        return DeployVerificationOutcome("NO_REGRESSION", until, readings, verifications)
    else:
        others = kinds - {"NO_REGRESSION"}
        if "UNKNOWN_STATE" in others:
            kind = "UNKNOWN_STATE"
        elif len(others) == 1:
            kind = others.pop()
        else:
            kind = "NOT_ESTABLISHED"
        status, reason = "INCOMPLETE", _REASONS[kind].format(until=until)
    return DeployVerificationOutcome(status, until, readings, verifications, reason)


def judge_deploy_verifications(
    verifications: CommitDeployVerifications,
    until: Checkpoint | DeployCheckpoint = "LANDING",
    selector: DeploySelector | None = None,
) -> DeployVerificationOutcome:
    """Judge one read of a commit's deploys through `until`.

    A check that is not recorded yet reads INCOMPLETE; use
    `wait_for_deploy_verifications` to wait for it.
    """
    result = conclude(verifications, checkpoint_name(until), selector, "INCOMPLETE")
    assert result is not None
    return result
