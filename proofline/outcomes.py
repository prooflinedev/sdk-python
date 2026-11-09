"""Review completion follows recorded assessment and evidence states."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, cast
from uuid import UUID

from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.open_items_view import OpenItemsView
from ._generated.types import Unset
from ._transport import ProoflineError

OutcomeStatus = Literal["COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"]
SeverityThreshold = Literal["WARNING", "SERIOUS"]
GateResult = Literal["REACHED", "NOT_REACHED", "NOT_COMPLETE", "UNAVAILABLE"]
# Least severe first.
SEVERITIES: tuple[SeverityThreshold, ...] = ("WARNING", "SERIOUS")
COMPLETE_CHECKS = frozenset(("READY", "BLOCKED", "NOT_APPLICABLE"))
COMPLETE_LIFECYCLES = frozenset(("GATING", "SHADOW", "QUARANTINED", "RETIRED"))
_KNOWN_ASSESSMENTS = frozenset(
    ("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "SUPERSEDED", "EXCLUDED")
)
_WITHHELD_MARKER = "[withheld: environment value]"


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

    def gate(self, fail_on: SeverityThreshold) -> GateResult:
        """Measure the review against a severity threshold as `proofline ci review --fail-on`.

        Completeness decides first. A review that is incomplete, failed or stopped is
        NOT_COMPLETE whatever it found, and a wait that timed out is UNAVAILABLE. A
        completed review REACHES the threshold when the server counts an open finding at
        or above it, or when a complete CODE assessment of the review's own commits holds
        an unresolved finding at or above it. Dismissed findings and unexpired risk
        acceptances are not open. A severity this SDK does not know reaches every
        threshold. Without the server's open-finding counts the threshold cannot be
        measured, which is UNAVAILABLE and never NOT_REACHED.
        """
        if fail_on not in SEVERITIES:
            raise ValueError("fail_on must be WARNING or SERIOUS.")
        if self.status == "TIMED_OUT":
            return "UNAVAILABLE"
        if self.status != "COMPLETED":
            return "NOT_COMPLETE"
        if self.review is None:
            return "UNAVAILABLE"
        counts = self.review.open_items
        if not isinstance(counts, OpenItemsView):
            return "UNAVAILABLE"
        count = counts.serious_findings if fail_on == "SERIOUS" else counts.open_findings
        if type(count) is not int or count < 0:
            return "UNAVAILABLE"
        # Complete environments complete a review even beside a partial CODE assessment,
        # whose findings are not its whole result. CODE findings have no recorded
        # decisions, so their lifecycle and severity decide.
        code = _recorded_code(self.review)
        findings = (
            code.findings
            if code is not None
            and code.status == "COMPLETED"
            and not text(code.incompleteness_kind)
            else []
        )
        if count > 0 or any(
            finding.lifecycle_state != "RESOLVED" and _reaches(finding.severity, fail_on)
            for finding in findings
        ):
            return "REACHED"
        return "NOT_REACHED"


def _reaches(severity: object, threshold: SeverityThreshold) -> bool:
    # An unknown severity, which a newer server can send, is never read as below a threshold.
    if severity not in SEVERITIES:
        return True
    return SEVERITIES.index(cast(SeverityThreshold, severity)) >= SEVERITIES.index(threshold)


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
    return _recorded_code(review)


def _recorded_code(review: CustomerReviewDetail) -> CustomerCodeAssessment | None:
    """The CODE record of this review's own commits with published findings, or None."""
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
                    (kind,) if kind else ("CODE_ASSESSMENT_STATE_UNAVAILABLE",),
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
