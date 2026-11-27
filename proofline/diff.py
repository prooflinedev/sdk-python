"""Compare settled Proofline reviews without inferring unrecorded outcomes."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from ._generated.models.customer_assessment import CustomerAssessment
from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.finding_placement_view import FindingPlacementView
from .outcomes import (
    COMPLETE_CHECKS,
    COMPLETE_LIFECYCLES,
    ReviewOutcome,
    _code_assessment,
    text,
)

ScopeKind = Literal["environment", "code"]
ScopeGapKind = Literal[
    "MISSING_IN_BASELINE",
    "MISSING_IN_CURRENT",
    "INCOMPLETE_BASELINE",
    "INCOMPLETE_CURRENT",
    "DUPLICATE_SCOPE",
    "AUDIT_UNCOMPARABLE",
    "MISSING_REVIEW",
]
UncorrelatedReason = Literal["MISSING_FINGERPRINT", "DUPLICATE_FINGERPRINT"]


@dataclass(frozen=True)
class ScopedFinding:
    scope_kind: ScopeKind
    scope_name: str
    assessment_id: UUID
    finding: CustomerFinding
    reason: UncorrelatedReason | None = None


@dataclass(frozen=True)
class FindingDelta:
    scope_kind: ScopeKind
    scope_name: str
    fingerprint: str
    baseline: CustomerFinding
    current: CustomerFinding
    severity_changed: bool
    escalated: bool
    placement_changed: bool


@dataclass(frozen=True)
class ScopeGap:
    scope_kind: ScopeKind
    scope_name: str
    kind: ScopeGapKind
    detail: str
    assessment_id: UUID | None = None


@dataclass(frozen=True)
class ReviewDiff:
    baseline_review_id: UUID | None
    current_review_id: UUID | None
    introduced: tuple[ScopedFinding, ...] = ()
    resolved: tuple[ScopedFinding, ...] = ()
    persisting: tuple[FindingDelta, ...] = ()
    uncorrelated_baseline: tuple[ScopedFinding, ...] = ()
    uncorrelated_current: tuple[ScopedFinding, ...] = ()
    scope_gaps: tuple[ScopeGap, ...] = ()

    @property
    def escalated(self) -> tuple[FindingDelta, ...]:
        return tuple(delta for delta in self.persisting if delta.escalated)

    @property
    def severity_changed(self) -> tuple[FindingDelta, ...]:
        return tuple(delta for delta in self.persisting if delta.severity_changed)

    @property
    def has_gaps(self) -> bool:
        return bool(self.scope_gaps or self.uncorrelated_baseline or self.uncorrelated_current)

    @property
    def complete(self) -> bool:
        return not self.has_gaps


@dataclass(frozen=True)
class _IndexedScope:
    scope_kind: ScopeKind
    scope_name: str
    assessment_id: UUID | None
    findings: tuple[CustomerFinding, ...]
    incomplete_detail: str | None


@dataclass
class _ExtractedSide:
    review: CustomerReviewDetail | None
    review_id: UUID | None
    scopes: dict[tuple[ScopeKind, str], _IndexedScope] = field(default_factory=dict)
    gaps: list[ScopeGap] = field(default_factory=list)


def _placement_value(finding: CustomerFinding) -> str | None:
    placement = finding.placement
    if isinstance(placement, FindingPlacementView):
        return placement.placement
    return None


def _is_active(finding: CustomerFinding) -> bool:
    return finding.lifecycle_state != "RESOLVED"


def _assessment_incomplete_detail(assessment: CustomerAssessment) -> str | None:
    if assessment.status != "COMPLETED":
        return f"Assessment status is {assessment.status}."
    kind = text(assessment.incompleteness_kind)
    if kind is not None:
        return f"Assessment is incomplete ({kind})."
    evidence_gap = text(assessment.release_evidence_gap)
    if evidence_gap is not None:
        return f"Release evidence gap recorded ({evidence_gap})."
    if isinstance(assessment.reason_codes, list) and assessment.reason_codes:
        return f"Assessment gap codes recorded: {', '.join(assessment.reason_codes)}."
    if not assessment.checks.receipt_recorded:
        return "Check receipt was not recorded."
    if assessment.checks.status not in COMPLETE_CHECKS:
        return f"Check receipt status is {assessment.checks.status}."
    unresolved = [
        check.name
        for check in assessment.checks.families
        if check.outcome not in COMPLETE_CHECKS or check.lifecycle not in COMPLETE_LIFECYCLES
    ]
    if unresolved:
        return f"Checks are unresolved: {', '.join(unresolved)}."
    return None


def _code_incomplete_detail(code: CustomerCodeAssessment | None) -> str | None:
    if code is None:
        return "Code assessment is unavailable."
    if code.status != "COMPLETED":
        return f"Code assessment status is {code.status}."
    kind = text(code.incompleteness_kind)
    if kind is not None:
        return f"Code assessment is incomplete ({kind})."
    if isinstance(code.reason_codes, list) and code.reason_codes:
        return f"Code assessment gap codes recorded: {', '.join(code.reason_codes)}."
    return None


def _unwrap_review(
    source: CustomerReviewDetail | ReviewOutcome,
    side_label: Literal["baseline", "current"],
) -> _ExtractedSide:
    outcome_status: str | None = None
    outcome_reason: str | None = None
    if isinstance(source, ReviewOutcome):
        review = source.review
        outcome_status = source.status
        outcome_reason = source.reason
    else:
        review = source

    if review is None:
        detail = outcome_reason or (
            f"No {side_label} review detail is available ({outcome_status})."
            if outcome_status is not None
            else f"No {side_label} review detail is available."
        )
        return _ExtractedSide(
            review=None,
            review_id=None,
            gaps=[
                ScopeGap(
                    scope_kind="environment",
                    scope_name="review",
                    kind="MISSING_REVIEW",
                    detail=detail,
                )
            ],
        )

    extracted = _ExtractedSide(review=review, review_id=review.id)
    incomplete_kind: ScopeGapKind = (
        "INCOMPLETE_BASELINE" if side_label == "baseline" else "INCOMPLETE_CURRENT"
    )

    audit_mode = text(review.audit_mode)
    if audit_mode is not None:
        extracted.gaps.append(
            ScopeGap(
                scope_kind="environment",
                scope_name="audit",
                kind="AUDIT_UNCOMPARABLE",
                detail=f"Audit review ({audit_mode}) findings live in its audit report.",
            )
        )
        return extracted

    if review.assessment_count != len(review.assessments):
        extracted.gaps.append(
            ScopeGap(
                scope_kind="environment",
                scope_name="assessments",
                kind=incomplete_kind,
                detail="Review assessment_count does not match recorded assessments.",
            )
        )

    seen_envs: set[str] = set()
    for assessment in review.assessments:
        env_name = assessment.environment_display_name
        key: tuple[ScopeKind, str] = ("environment", env_name)
        if env_name in seen_envs:
            extracted.gaps.append(
                ScopeGap(
                    scope_kind="environment",
                    scope_name=env_name,
                    kind="DUPLICATE_SCOPE",
                    detail=f"Duplicate environment assessment for {env_name!r} in {side_label}.",
                    assessment_id=assessment.id,
                )
            )
            extracted.scopes.pop(key, None)
            continue
        seen_envs.add(env_name)
        extracted.scopes[key] = _IndexedScope(
            scope_kind="environment",
            scope_name=env_name,
            assessment_id=assessment.id,
            findings=tuple(assessment.findings),
            incomplete_detail=_assessment_incomplete_detail(assessment),
        )

    if review.assessment_count == 0 and not review.assessments:
        code = _code_assessment(review)
        extracted.scopes[("code", "code")] = _IndexedScope(
            scope_kind="code",
            scope_name="code",
            assessment_id=code.id if code is not None else None,
            findings=tuple(code.findings) if code is not None else (),
            incomplete_detail=_code_incomplete_detail(code),
        )

    if review.status != "COMPLETED" or (
        outcome_status is not None and outcome_status != "COMPLETED"
    ):
        status_label = outcome_status if outcome_status is not None else review.status
        extracted.gaps.append(
            ScopeGap(
                scope_kind="environment",
                scope_name="review",
                kind=incomplete_kind,
                detail=outcome_reason or f"The {side_label} review status is {status_label}.",
            )
        )

    return extracted


def _partition_findings(
    scope: _IndexedScope,
) -> tuple[dict[str, CustomerFinding], list[ScopedFinding]]:
    assert scope.assessment_id is not None
    active = [item for item in scope.findings if _is_active(item)]
    fingerprints = [text(item.finding_fingerprint) for item in active]
    counts = Counter(fp for fp in fingerprints if fp is not None)

    by_fingerprint: dict[str, CustomerFinding] = {}
    uncorrelated: list[ScopedFinding] = []
    for item, fp in zip(active, fingerprints, strict=True):
        if fp is None:
            uncorrelated.append(
                ScopedFinding(
                    scope_kind=scope.scope_kind,
                    scope_name=scope.scope_name,
                    assessment_id=scope.assessment_id,
                    finding=item,
                    reason="MISSING_FINGERPRINT",
                )
            )
        elif counts[fp] > 1:
            uncorrelated.append(
                ScopedFinding(
                    scope_kind=scope.scope_kind,
                    scope_name=scope.scope_name,
                    assessment_id=scope.assessment_id,
                    finding=item,
                    reason="DUPLICATE_FINGERPRINT",
                )
            )
        else:
            by_fingerprint[fp] = item
    return by_fingerprint, uncorrelated


def _scoped_sort_key(item: ScopedFinding) -> tuple[str, str, str, str]:
    return (
        item.scope_kind,
        item.scope_name,
        text(item.finding.finding_fingerprint) or "",
        str(item.finding.id),
    )


def _delta_sort_key(item: FindingDelta) -> tuple[str, str, str, str]:
    return (item.scope_kind, item.scope_name, item.fingerprint, str(item.current.id))


def _gap_sort_key(item: ScopeGap) -> tuple[str, str, str, str]:
    return (item.scope_kind, item.scope_name, item.kind, str(item.assessment_id or ""))


def diff_reviews(
    baseline: CustomerReviewDetail | ReviewOutcome,
    current: CustomerReviewDetail | ReviewOutcome,
) -> ReviewDiff:
    """Compare two settled Proofline reviews within matching environment and code scopes.

    Missing or incomplete assessments are reported as explicit scope gaps rather than
    inferring that prior findings were resolved or that new findings were introduced.
    """
    base_side = _unwrap_review(baseline, "baseline")
    curr_side = _unwrap_review(current, "current")

    gaps: list[ScopeGap] = [*base_side.gaps, *curr_side.gaps]
    if base_side.review is None or curr_side.review is None:
        gaps.sort(key=_gap_sort_key)
        return ReviewDiff(
            baseline_review_id=base_side.review_id,
            current_review_id=curr_side.review_id,
            scope_gaps=tuple(gaps),
        )

    if any(gap.kind == "AUDIT_UNCOMPARABLE" for gap in gaps):
        gaps.sort(key=_gap_sort_key)
        return ReviewDiff(
            baseline_review_id=base_side.review_id,
            current_review_id=curr_side.review_id,
            scope_gaps=tuple(gaps),
        )

    introduced: list[ScopedFinding] = []
    resolved: list[ScopedFinding] = []
    persisting: list[FindingDelta] = []
    uncorrelated_baseline: list[ScopedFinding] = []
    uncorrelated_current: list[ScopedFinding] = []

    duplicate_keys = {
        (gap.scope_kind, gap.scope_name) for gap in gaps if gap.kind == "DUPLICATE_SCOPE"
    }
    all_keys = sorted(set(base_side.scopes) | set(curr_side.scopes))
    for key in all_keys:
        if key in duplicate_keys:
            continue
        scope_kind, scope_name = key
        base_scope = base_side.scopes.get(key)
        curr_scope = curr_side.scopes.get(key)
        if base_scope is None:
            assert curr_scope is not None
            gaps.append(
                ScopeGap(
                    scope_kind=scope_kind,
                    scope_name=scope_name,
                    kind="MISSING_IN_BASELINE",
                    detail=f"Scope {scope_name!r} was not assessed in the baseline review.",
                    assessment_id=curr_scope.assessment_id,
                )
            )
            continue
        if curr_scope is None:
            gaps.append(
                ScopeGap(
                    scope_kind=scope_kind,
                    scope_name=scope_name,
                    kind="MISSING_IN_CURRENT",
                    detail=f"Scope {scope_name!r} was not assessed in the current review.",
                    assessment_id=base_scope.assessment_id,
                )
            )
            continue

        incomplete = False
        if base_scope.incomplete_detail is not None:
            gaps.append(
                ScopeGap(
                    scope_kind=scope_kind,
                    scope_name=scope_name,
                    kind="INCOMPLETE_BASELINE",
                    detail=base_scope.incomplete_detail,
                    assessment_id=base_scope.assessment_id,
                )
            )
            incomplete = True
        if curr_scope.incomplete_detail is not None:
            gaps.append(
                ScopeGap(
                    scope_kind=scope_kind,
                    scope_name=scope_name,
                    kind="INCOMPLETE_CURRENT",
                    detail=curr_scope.incomplete_detail,
                    assessment_id=curr_scope.assessment_id,
                )
            )
            incomplete = True
        if incomplete or base_scope.assessment_id is None or curr_scope.assessment_id is None:
            continue

        base_map, base_uncorr = _partition_findings(base_scope)
        curr_map, curr_uncorr = _partition_findings(curr_scope)
        uncorrelated_baseline.extend(base_uncorr)
        uncorrelated_current.extend(curr_uncorr)

        for fp in sorted(set(base_map) | set(curr_map)):
            base_item = base_map.get(fp)
            curr_item = curr_map.get(fp)
            if base_item is None:
                assert curr_item is not None
                introduced.append(
                    ScopedFinding(
                        scope_kind=scope_kind,
                        scope_name=scope_name,
                        assessment_id=curr_scope.assessment_id,
                        finding=curr_item,
                    )
                )
            elif curr_item is None:
                resolved.append(
                    ScopedFinding(
                        scope_kind=scope_kind,
                        scope_name=scope_name,
                        assessment_id=base_scope.assessment_id,
                        finding=base_item,
                    )
                )
            else:
                severity_changed = base_item.severity != curr_item.severity
                escalated = base_item.severity == "WARNING" and curr_item.severity == "SERIOUS"
                placement_changed = _placement_value(base_item) != _placement_value(curr_item)
                persisting.append(
                    FindingDelta(
                        scope_kind=scope_kind,
                        scope_name=scope_name,
                        fingerprint=fp,
                        baseline=base_item,
                        current=curr_item,
                        severity_changed=severity_changed,
                        escalated=escalated,
                        placement_changed=placement_changed,
                    )
                )

    introduced.sort(key=_scoped_sort_key)
    resolved.sort(key=_scoped_sort_key)
    persisting.sort(key=_delta_sort_key)
    uncorrelated_baseline.sort(key=_scoped_sort_key)
    uncorrelated_current.sort(key=_scoped_sort_key)
    gaps.sort(key=_gap_sort_key)

    return ReviewDiff(
        baseline_review_id=base_side.review_id,
        current_review_id=curr_side.review_id,
        introduced=tuple(introduced),
        resolved=tuple(resolved),
        persisting=tuple(persisting),
        uncorrelated_baseline=tuple(uncorrelated_baseline),
        uncorrelated_current=tuple(uncorrelated_current),
        scope_gaps=tuple(gaps),
    )
