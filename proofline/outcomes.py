"""Review completion follows recorded assessment and evidence states."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlsplit
from uuid import UUID

from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.types import Unset
from ._transport import ProoflineError

OutcomeStatus = Literal["COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"]
_OUTCOME_STATUSES = frozenset(("COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"))
COMPLETE_CHECKS = frozenset(("READY", "BLOCKED", "NOT_APPLICABLE"))
COMPLETE_LIFECYCLES = frozenset(("GATING", "SHADOW", "QUARANTINED", "RETIRED"))
_KNOWN_ASSESSMENTS = frozenset(
    ("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "SUPERSEDED", "EXCLUDED")
)
_WITHHELD_MARKER = "[withheld: environment value]"
_HEAD_REASONS = {
    "HEAD_COMMIT_MISMATCH": "The review is pinned to another head commit.",
    "HEAD_COMMIT_UNAVAILABLE": "The review names no head commit.",
}
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_REASON_CODE_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_REVISION_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-")
_GIT_COMMIT_KINDS = frozenset(
    ("PULL_REQUEST", "DEPLOYMENT", "COMMIT", "FILES", "MERGE_GROUP", "REVISION_SCAN")
)


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
    reason_codes: tuple[str, ...] = field(default=(), repr=False)
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


def _is_commit_sha(value: str) -> bool:
    return len(value) in (40, 64) and all(char in _HEX_DIGITS for char in value)


def _is_reason_code(value: str) -> bool:
    return (
        1 <= len(value) <= 128
        and value[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        and all(char in _REASON_CODE_CHARS for char in value)
    )


def _is_pinned_revision(value: str) -> bool:
    return 1 <= len(value) <= 128 and all(char in _REVISION_CHARS for char in value)


def _is_recorded_commit_url(value: str) -> bool:
    if "\r" in value or "\n" in value:
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
    )


def format_review_outcome(outcome: ReviewOutcome) -> str:
    """Return a safe, single-line summary suitable for a CI log.

    `reviewed_commit` requires the recorded commit URL and a documented Git
    review kind. A patch's derived revision is reported as `pinned_revision`
    instead. The requested and provider-current heads are never inputs.
    """

    reviewed_commit = "unknown"
    pinned_revision = "unknown"
    status = outcome.status if outcome.status in _OUTCOME_STATUSES else "unknown"
    if outcome.review is not None:
        head = text(outcome.review.head_commit_sha)
        kind = outcome.review.kind
        if (
            kind in _GIT_COMMIT_KINDS
            and head is not None
            and _is_commit_sha(head)
            and (commit_url := text(outcome.review.head_commit_url)) is not None
            and _is_recorded_commit_url(commit_url)
        ):
            reviewed_commit = head
        elif kind == "PATCH" and head is not None and _is_pinned_revision(head):
            pinned_revision = head
    reason_codes = tuple(
        dict.fromkeys(
            code for gap in outcome.gaps for code in gap.reason_codes if _is_reason_code(code)
        )
    )
    return (
        f"proofline_review status={status} reviewed_commit={reviewed_commit} "
        f"pinned_revision={pinned_revision} "
        f"reason_codes={','.join(reason_codes) if reason_codes else 'unknown'}"
    )


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


def _optional_texts(value: object) -> bool:
    return (
        value is None
        or isinstance(value, Unset)
        or (isinstance(value, list) and all(isinstance(item, str) for item in value))
    )


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
        or not _optional_texts(code.reason_codes)
    ):
        return None
    for recorded, actual in (
        (review.head_commit_sha, code.head_commit_sha),
        (review.base_commit_sha, code.base_commit_sha),
    ):
        if isinstance(recorded, str) and recorded.lower() != actual.lower():
            return None
    if any(finding.risk_domain == _WITHHELD_MARKER for finding in code.findings):
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
        if not _optional_texts(assessment.reason_codes):
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


def _head_gap(review: CustomerReviewDetail, head_commit_sha: str | None) -> str | None:
    # A result is evidence only for the head the review is pinned to.
    if head_commit_sha is None:
        return None
    head = text(review.head_commit_sha)
    if head is None:
        return "HEAD_COMMIT_UNAVAILABLE"
    return None if head.lower() == head_commit_sha.lower() else "HEAD_COMMIT_MISMATCH"


def outcome(
    review: CustomerReviewDetail | None,
    review_url: str,
    forced: OutcomeStatus | None = None,
    *,
    review_id: UUID | None = None,
    head_commit_sha: str | None = None,
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
        elif code.status != "COMPLETED" or text(code.incompleteness_kind) or code.reason_codes:
            kind = text(code.incompleteness_kind)
            reasons = tuple(code.reason_codes) if isinstance(code.reason_codes, list) else ()
            if kind:
                reasons = (*reasons, kind)
            gaps.append(
                AssessmentGap(
                    code.id,
                    code.status,
                    reasons or ("CODE_ASSESSMENT_STATE_UNAVAILABLE",),
                    kind,
                )
            )
    for assessment in review.assessments:
        reasons = (
            tuple(assessment.reason_codes) if isinstance(assessment.reason_codes, list) else ()
        )
        kind = text(assessment.incompleteness_kind)
        evidence = text(assessment.release_evidence_gap)
        if kind:
            reasons = (*reasons, kind)
        if evidence:
            reasons = (*reasons, evidence)
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
        if not assessment.checks.receipt_recorded:
            reasons = (*reasons, "CHECK_RECEIPT_ABSENT")
        elif assessment.checks.status not in COMPLETE_CHECKS or checks:
            reasons = (*reasons, "CHECKS_UNRESOLVED")
        if assessment.status != "COMPLETED" or reasons or kind or evidence or checks:
            if not reasons and not kind and not evidence and not checks:
                reasons = (
                    "ASSESSMENT_RESULT_UNAVAILABLE"
                    if assessment.status in _KNOWN_ASSESSMENTS
                    else "UNKNOWN_ASSESSMENT_STATUS",
                )
            gaps.append(
                AssessmentGap(assessment.id, assessment.status, reasons, kind, evidence, checks)
            )
    if review.assessment_count != len(review.assessments):
        gaps.append(AssessmentGap(None, "UNKNOWN", ("ASSESSMENT_HISTORY_UNAVAILABLE",)))
    head_gap = _head_gap(review, head_commit_sha)
    if forced is not None:
        status = forced
    elif head_gap == "HEAD_COMMIT_MISMATCH":
        # A pinned head does not change, so nothing this review records later
        # can speak for the commit the caller named.
        status = "INCOMPLETE"
    elif review.status in ("PENDING", "RUNNING"):
        return None
    elif review.status == "FAILED":
        status = "FAILED"
    elif review.status in ("STOPPED", "SUPERSEDED"):
        status = "STOPPED"
    elif review.status == "COMPLETED":
        status = "INCOMPLETE" if gaps or head_gap else "COMPLETED"
    else:
        status = "INCOMPLETE"
        if not gaps:
            gaps.append(AssessmentGap(None, review.status, ("REVIEW_STATE_UNAVAILABLE",)))
    if head_gap is None:
        return ReviewOutcome(status, review_url, review, tuple(gaps))
    gaps.append(AssessmentGap(None, "UNKNOWN", (head_gap,)))
    return ReviewOutcome(status, review_url, review, tuple(gaps), _HEAD_REASONS[head_gap])
