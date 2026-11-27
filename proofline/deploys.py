"""Deploy verification outcomes follow each recorded deploy's checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID

from ._generated.models.commit_deploy import CommitDeploy
from ._generated.models.commit_deploy_verifications import CommitDeployVerifications
from ._generated.types import Unset
from ._transport import ProoflineError

DeployCheckpointName = Literal["LANDING", "MINUTES_20", "HOUR_1", "DAY_1"]
DeployOutcomeStatus = Literal["HEALTHY", "REGRESSED", "FAILED", "INCOMPLETE", "TIMED_OUT"]
DeployVerdictStatus = Literal["HEALTHY", "REGRESSED", "FAILED", "INCOMPLETE", "PENDING"]

CHECKPOINTS: tuple[DeployCheckpointName, ...] = ("LANDING", "MINUTES_20", "HOUR_1", "DAY_1")
_REASONS = {
    "NOT_RECORDED": "No deploy of the commit was recorded.",
    "REGRESSED": "A deploy of the commit regressed.",
    "FAILED": "A deploy of the commit failed.",
}


@dataclass(frozen=True)
class DeployVerdict:
    """Where one deploy stands against the checks the caller waits for."""

    environment_id: UUID
    status: DeployVerdictStatus
    state: str
    reason_codes: tuple[str, ...] = field(default=(), repr=False)
    deploy_url: str | None = field(default=None, repr=False)
    deploy: CommitDeploy | None = field(default=None, repr=False)


@dataclass(frozen=True)
class DeployVerificationOutcome:
    status: DeployOutcomeStatus
    commit_sha: str = field(repr=False)
    deploys: tuple[DeployVerdict, ...] = field(default=(), repr=False)
    verifications: CommitDeployVerifications | None = field(default=None, repr=False)
    reason: str | None = None


def checkpoint_index(through: str) -> int:
    if through not in CHECKPOINTS:
        raise ValueError("through must be one of LANDING, MINUTES_20, HOUR_1 or DAY_1.")
    return CHECKPOINTS.index(through)


def deploy_commit(value: str) -> None:
    # The route names one exact commit: a full lowercase SHA-1, nothing else.
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError("The deploy commit must be a full 40-character lowercase hexadecimal SHA.")


def _invalid() -> ProoflineError:
    return ProoflineError(
        0,
        "urn:proofline:sdk:invalid-response",
        "The deploy verifications have invalid metadata.",
    )


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _validate(verifications: CommitDeployVerifications) -> None:
    if type(verifications.recorded) is not bool or not isinstance(verifications.deploys, list):
        raise _invalid()
    if not verifications.recorded and verifications.deploys:
        raise _invalid()
    for deploy in verifications.deploys:
        if (
            not isinstance(deploy.environment_id, UUID)
            or not isinstance(deploy.state, str)
            or type(deploy.regressed) is not bool
            or not isinstance(deploy.checkpoints, list)
            or not isinstance(deploy.gaps, list)
        ):
            raise _invalid()
        names = [checkpoint.checkpoint for checkpoint in deploy.checkpoints]
        if names and names != [*CHECKPOINTS[: len(names)]]:
            raise _invalid()
        for checkpoint in deploy.checkpoints:
            if not isinstance(checkpoint.due_at, datetime) or not isinstance(
                checkpoint.gaps, (list, Unset)
            ):
                raise _invalid()


def _gaps(value: object) -> tuple[str, ...]:
    return tuple(gap for gap in value if isinstance(gap, str)) if isinstance(value, list) else ()


def verdict(deploy: CommitDeploy, through: int) -> DeployVerdict:
    """Settle one deploy against every check up to and including ``through``.

    A recorded regression settles a deploy whichever check recorded it. A check
    replaced by a later deploy counts only after a healthy landing check, as
    ``VERIFIED_UNTIL_SUPERSEDED`` reads it.
    """

    def settled(status: DeployVerdictStatus, *reasons: str) -> DeployVerdict:
        return DeployVerdict(
            deploy.environment_id,
            status,
            deploy.state,
            tuple(dict.fromkeys(reasons)),
            _text(deploy.deploy_url),
            deploy,
        )

    ended = deploy.verification_ended is True
    results = [checkpoint.result for checkpoint in deploy.checkpoints]
    if deploy.regressed or "REGRESSED" in results:
        return settled("REGRESSED", "CHECK_REGRESSED")
    if deploy.state == "FAILED":
        return settled("FAILED", "DEPLOYMENT_FAILED")
    if deploy.state == "UNVERIFIED":
        return settled("INCOMPLETE", "DEPLOY_UNVERIFIED")
    window = deploy.checkpoints[: through + 1]
    reasons: list[str] = []
    healthy_landing = False
    for index in range(through + 1):
        if index >= len(window):
            if ended:
                return settled("INCOMPLETE", *reasons, "CHECK_NEVER_RECORDED")
            return settled("PENDING", *reasons, "CHECK_NOT_RECORDED")
        checkpoint = window[index]
        gaps = _gaps(checkpoint.gaps)
        if checkpoint.result is None or isinstance(checkpoint.result, Unset):
            if ended:
                return settled("INCOMPLETE", *reasons, *gaps, "CHECK_NEVER_RECORDED")
            return settled("PENDING", *reasons, *gaps, "CHECK_NOT_RECORDED")
        if checkpoint.result == "SUPERSEDED":
            if not healthy_landing:
                reasons.append("SUPERSEDED_BEFORE_LANDING_CHECK")
            break
        if checkpoint.result == "HEALTHY" and not gaps:
            healthy_landing = healthy_landing or index == 0
            continue
        if checkpoint.result == "HEALTHY":
            reasons.extend(gaps)
        elif checkpoint.result == "INCOMPLETE":
            reasons.extend((*gaps, "CHECK_INCOMPLETE"))
        else:
            # A result this SDK does not know proves nothing.
            reasons.extend((*gaps, "UNKNOWN_CHECK_RESULT"))
    if deploy.rolled_back is True:
        # Healthy checks of a deploy its service no longer serves prove nothing now.
        reasons.append("ROLLED_BACK")
    if reasons:
        return settled("INCOMPLETE", *reasons)
    return settled("HEALTHY")


def next_due(
    verifications: CommitDeployVerifications,
    through: int,
    *,
    environment_id: UUID | None = None,
) -> datetime | None:
    """The earliest due time of a check the wait still needs and that is not recorded."""

    due: list[datetime] = []
    for deploy in verifications.deploys:
        if environment_id is not None and deploy.environment_id != environment_id:
            continue
        for checkpoint in deploy.checkpoints[: through + 1]:
            if checkpoint.result is None or isinstance(checkpoint.result, Unset):
                due.append(checkpoint.due_at)
                break
    return min(due, default=None)


def outcome(
    verifications: CommitDeployVerifications | None,
    commit_sha: str,
    through: int,
    *,
    environment_id: UUID | None = None,
    forced: Literal["TIMED_OUT"] | None = None,
) -> DeployVerificationOutcome | None:
    if verifications is None:
        return DeployVerificationOutcome(
            forced or "INCOMPLETE",
            commit_sha,
            reason="No deploy verification result is available.",
        )
    _validate(verifications)
    deploys = tuple(
        verdict(deploy, through)
        for deploy in verifications.deploys
        if environment_id is None or deploy.environment_id == environment_id
    )

    def result(status: DeployOutcomeStatus, reason: str | None) -> DeployVerificationOutcome:
        return DeployVerificationOutcome(status, commit_sha, deploys, verifications, reason)

    statuses = {deploy.status for deploy in deploys}
    if "REGRESSED" in statuses:
        # A regression is final evidence; nothing a later read records undoes it.
        return result("REGRESSED", _REASONS["REGRESSED"])
    if forced is not None:
        return result(forced, None if deploys else _REASONS["NOT_RECORDED"])
    if not deploys or "PENDING" in statuses:
        # A deploy recorded later, or a check still due, can still settle the wait.
        return None
    if "FAILED" in statuses:
        return result("FAILED", _REASONS["FAILED"])
    if "INCOMPLETE" in statuses:
        return result("INCOMPLETE", None)
    return result("HEALTHY", None)
