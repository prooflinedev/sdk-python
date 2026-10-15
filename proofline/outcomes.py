"""Review completion follows recorded assessment and evidence states."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.types import Unset
from ._transport import ProoflineError

OutcomeStatus = Literal["COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"]
COMPLETE_CHECKS = frozenset(("READY", "BLOCKED", "NOT_APPLICABLE"))
COMPLETE_LIFECYCLES = frozenset(("GATING", "SHADOW", "QUARANTINED", "RETIRED"))


@dataclass(frozen=True)
class CheckGap:
    name: str = field(repr=False)
    outcome: str
    lifecycle: str
    unresolved_reason: str | None = field(default=None, repr=False)
    detail: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class AssessmentGap:
    assessment_id: UUID | None
    status: str
    reason_codes: tuple[str, ...] = ()
    incompleteness_kind: str | None = None
    release_evidence_gap: str | None = field(default=None, repr=False)
    checks: tuple[CheckGap, ...] = field(default=(), repr=False)


@dataclass(frozen=True)
class ReviewOutcome:
    status: OutcomeStatus
    review_url: str
    review: CustomerReviewDetail | None = field(default=None, repr=False)
    gaps: tuple[AssessmentGap, ...] = field(default=(), repr=False)
    reason: str | None = None


def text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _invalid() -> ProoflineError:
    return ProoflineError(
        0,
        "urn:proofline:sdk:invalid-response",
        "The review has invalid identity or check metadata.",
    )


def _optional_text(value: object) -> bool:
    return value is None or isinstance(value, (str, Unset))


def _code_assessment(review: CustomerReviewDetail) -> CustomerCodeAssessment | None:
    # A CODE result cannot replace a missing ENV result or its check receipts.
    if review.assessment_count != 0 or review.assessments:
        return None
    code = review.code_assessment
    if (
        not isinstance(code, CustomerCodeAssessment)
        or not isinstance(code.id, UUID)
        or not text(code.base_commit_sha)
        or not text(code.head_commit_sha)
        or not isinstance(code.findings, list)
        or code.status not in ("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "EXCLUDED")
        or not _optional_text(code.incompleteness_kind)
    ):
        return None
    return code


def _validate(review: CustomerReviewDetail, review_id: UUID | None) -> None:
    if (
        not isinstance(review.id, UUID)
        or (review_id is not None and review.id != review_id)
        or not isinstance(review.status, str)
        or type(review.assessment_count) is not int
        or review.assessment_count < 0
        or not isinstance(review.assessments, list)
    ):
        raise _invalid()
    seen: set[UUID] = set()
    for assessment in review.assessments:
        if (
            not isinstance(assessment.id, UUID)
            or not isinstance(assessment.status, str)
            or not isinstance(assessment.checks.status, str)
            or type(assessment.checks.receipt_recorded) is not bool
            or not isinstance(assessment.checks.families, list)
            or not _optional_text(assessment.incompleteness_kind)
            or not _optional_text(assessment.release_evidence_gap)
        ):
            raise _invalid()
        if assessment.id in seen:
            raise _invalid()
        seen.add(assessment.id)
        reasons = assessment.reason_codes
        if not (reasons is None or isinstance(reasons, Unset)) and (
            not isinstance(reasons, list) or any(not isinstance(reason, str) for reason in reasons)
        ):
            raise _invalid()
        for check in assessment.checks.families:
            if (
                not isinstance(check.name, str)
                or not isinstance(check.outcome, str)
                or not isinstance(check.lifecycle, str)
                or not _optional_text(check.detail)
                or not _optional_text(check.unresolved_reason)
            ):
                raise _invalid()


def outcome(
    review: CustomerReviewDetail | None,
    review_url: str,
    forced: OutcomeStatus | None = None,
    *,
    review_id: UUID | None = None,
) -> ReviewOutcome | None:
    gaps: list[AssessmentGap] = []
    if review is None:
        return ReviewOutcome(
            forced or "INCOMPLETE", review_url, reason="No review result is available."
        )
    _validate(review, review_id)
    code_only = review.assessment_count == 0 and not review.assessments
    code = _code_assessment(review)
    if code_only:
        if code is None:
            gaps.append(AssessmentGap(None, "UNKNOWN", ("CODE_ASSESSMENT_UNAVAILABLE",)))
        elif code.status != "COMPLETED" or text(code.incompleteness_kind):
            kind = text(code.incompleteness_kind)
            gaps.append(
                AssessmentGap(
                    code.id,
                    code.status,
                    () if kind else ("CODE_ASSESSMENT_STATE_UNAVAILABLE",),
                    kind,
                )
            )
    elif review.assessment_count != len(review.assessments):
        gaps.append(AssessmentGap(None, "UNKNOWN", ("ASSESSMENT_HISTORY_UNAVAILABLE",)))
    for assessment in review.assessments:
        reasons = (
            tuple(assessment.reason_codes) if isinstance(assessment.reason_codes, list) else ()
        )
        kind = text(assessment.incompleteness_kind)
        evidence = text(assessment.release_evidence_gap)
        checks = tuple(
            CheckGap(
                check.name,
                check.outcome,
                check.lifecycle,
                text(check.unresolved_reason),
                text(check.detail),
            )
            for check in assessment.checks.families
            if check.outcome not in COMPLETE_CHECKS or check.lifecycle not in COMPLETE_LIFECYCLES
        )
        if (
            not assessment.checks.receipt_recorded
            or assessment.checks.status not in COMPLETE_CHECKS
        ):
            reasons = (*reasons, "CHECK_RECEIPT_UNAVAILABLE")
        if assessment.status != "COMPLETED" or reasons or kind or evidence or checks:
            if not reasons and not kind and not evidence and not checks:
                reasons = ("ASSESSMENT_STATE_UNAVAILABLE",)
            gaps.append(
                AssessmentGap(assessment.id, assessment.status, reasons, kind, evidence, checks)
            )
    if forced is not None:
        status = forced
    elif review.status in ("PENDING", "RUNNING"):
        return None
    elif review.status == "FAILED":
        status = "FAILED"
    elif review.status in ("STOPPED", "SUPERSEDED"):
        status = "STOPPED"
    elif review.status == "COMPLETED":
        status = "INCOMPLETE" if gaps else "COMPLETED"
    else:
        status = "INCOMPLETE"
        if not gaps:
            gaps.append(AssessmentGap(None, review.status, ("REVIEW_STATE_UNAVAILABLE",)))
    return ReviewOutcome(status, review_url, review, tuple(gaps))
