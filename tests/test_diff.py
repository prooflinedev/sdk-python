from __future__ import annotations

from typing import Any
from uuid import UUID

from proofline import CustomerReviewDetail, ReviewOutcome, diff_reviews

from .fixtures import (
    CODE_ASSESSMENT,
    FINDING,
    ORG,
    REVIEW,
    assessment,
    code_assessment,
    finding,
    review,
)

REVIEW_2 = UUID("00000000-0000-4000-8000-000000000103")
ASSESSMENT_2 = UUID("00000000-0000-4000-8000-000000000104")
ASSESSMENT_3 = UUID("00000000-0000-4000-8000-000000000204")
FINDING_2 = UUID("00000000-0000-4000-8000-000000000105")
FINDING_3 = UUID("00000000-0000-4000-8000-000000000205")
FINDING_4 = UUID("00000000-0000-4000-8000-000000000305")
FINDING_5 = UUID("00000000-0000-4000-8000-000000000405")


def _finding_dict(
    finding_id: UUID,
    *,
    fingerprint: str | None = "fp-default",
    severity: str = "WARNING",
    lifecycle_state: str = "NEW",
    placement: str | None = None,
) -> dict[str, Any]:
    payload = finding()
    payload["id"] = str(finding_id)
    payload["severity"] = severity
    payload["lifecycle_state"] = lifecycle_state
    if fingerprint is not None:
        payload["finding_fingerprint"] = fingerprint
    if placement is not None:
        payload["placement"] = {"placement": placement, "reason": "Synthetic placement."}
    return payload


def _review_model(
    review_id: UUID = REVIEW,
    *,
    status: str = "COMPLETED",
    assessments: list[dict[str, Any]] | None = None,
    assessment_count: int | None = None,
    code: dict[str, Any] | None = None,
    audit_mode: str | None = None,
) -> CustomerReviewDetail:
    payload = review(status=status)
    payload["id"] = str(review_id)
    env_assessments = assessments if assessments is not None else [assessment()]
    payload["assessments"] = env_assessments
    payload["assessment_count"] = (
        len(env_assessments) if assessment_count is None else assessment_count
    )
    payload["environment_display_names"] = [
        item["environment_display_name"] for item in env_assessments
    ]
    if code is not None:
        payload["code_assessment"] = code
    if audit_mode is not None:
        payload["audit_mode"] = audit_mode
    return CustomerReviewDetail.from_dict(payload)


def test_diff_reviews_tracks_introduced_resolved_escalated_and_placement() -> None:
    resolved_item = _finding_dict(FINDING, fingerprint="fp-resolved", severity="SERIOUS")
    escalated_base = _finding_dict(
        FINDING_2, fingerprint="fp-escalated", severity="WARNING", placement="CHECK_ONLY"
    )
    deescalated_base = _finding_dict(
        FINDING_3, fingerprint="fp-downgraded", severity="SERIOUS", lifecycle_state="UNCHANGED"
    )
    already_closed = _finding_dict(
        FINDING_4, fingerprint="fp-already-closed", lifecycle_state="RESOLVED"
    )

    escalated_curr = _finding_dict(
        FINDING_2, fingerprint="fp-escalated", severity="SERIOUS", placement="INLINE"
    )
    deescalated_curr = _finding_dict(
        FINDING_3, fingerprint="fp-downgraded", severity="WARNING", lifecycle_state="UNCHANGED"
    )
    introduced_item = _finding_dict(FINDING_5, fingerprint="fp-new", severity="SERIOUS")

    base_env = assessment()
    base_env["findings"] = [resolved_item, escalated_base, deescalated_base, already_closed]
    curr_env = assessment()
    curr_env["id"] = str(ASSESSMENT_2)
    curr_env["findings"] = [escalated_curr, deescalated_curr, introduced_item]

    baseline = _review_model(REVIEW, assessments=[base_env])
    current = _review_model(REVIEW_2, assessments=[curr_env])

    diff = diff_reviews(baseline, current)

    assert diff.complete is True
    assert diff.has_gaps is False
    assert [item.finding.finding_fingerprint for item in diff.introduced] == ["fp-new"]
    assert [item.finding.finding_fingerprint for item in diff.resolved] == ["fp-resolved"]
    assert [item.fingerprint for item in diff.persisting] == ["fp-downgraded", "fp-escalated"]
    assert [item.fingerprint for item in diff.escalated] == ["fp-escalated"]
    assert [item.fingerprint for item in diff.severity_changed] == [
        "fp-downgraded",
        "fp-escalated",
    ]
    assert diff.escalated[0].placement_changed is True


def test_diff_reviews_isolates_missing_and_duplicate_fingerprints() -> None:
    missing_fp = _finding_dict(FINDING, fingerprint=None)
    blank_fp = _finding_dict(FINDING_2, fingerprint="")
    dup_a = _finding_dict(FINDING_3, fingerprint="fp-dup")
    dup_b = _finding_dict(FINDING_4, fingerprint="fp-dup")
    matched = _finding_dict(FINDING_5, fingerprint="fp-stable")

    base_env = assessment()
    base_env["findings"] = [missing_fp, dup_a, dup_b, matched]
    curr_env = assessment()
    curr_env["id"] = str(ASSESSMENT_2)
    curr_env["findings"] = [blank_fp, matched]

    diff = diff_reviews(
        _review_model(REVIEW, assessments=[base_env]),
        _review_model(REVIEW_2, assessments=[curr_env]),
    )

    assert diff.complete is False
    assert diff.has_gaps is True
    assert diff.introduced == ()
    assert diff.resolved == ()
    assert [item.fingerprint for item in diff.persisting] == ["fp-stable"]
    assert [(item.finding.id, item.reason) for item in diff.uncorrelated_baseline] == [
        (FINDING, "MISSING_FINGERPRINT"),
        (FINDING_3, "DUPLICATE_FINGERPRINT"),
        (FINDING_4, "DUPLICATE_FINGERPRINT"),
    ]
    assert [(item.finding.id, item.reason) for item in diff.uncorrelated_current] == [
        (FINDING_2, "MISSING_FINGERPRINT")
    ]


def test_diff_reviews_reports_incomplete_and_missing_scopes_without_false_resolution() -> None:
    base_prod = assessment()
    base_prod["environment_display_name"] = "prod"
    base_prod["findings"] = [_finding_dict(FINDING, fingerprint="fp-prod")]

    base_staging = assessment()
    base_staging["id"] = str(ASSESSMENT_3)
    base_staging["environment_display_name"] = "staging"
    base_staging["findings"] = [_finding_dict(FINDING_2, fingerprint="fp-staging")]

    curr_prod = assessment(status="COMPLETED")
    curr_prod["id"] = str(ASSESSMENT_2)
    curr_prod["environment_display_name"] = "prod"
    curr_prod["checks"] = {"families": [], "receipt_recorded": False, "status": "UNAVAILABLE"}

    diff = diff_reviews(
        _review_model(REVIEW, assessments=[base_prod, base_staging]),
        _review_model(REVIEW_2, assessments=[curr_prod]),
    )

    assert diff.complete is False
    assert diff.resolved == ()
    assert diff.introduced == ()
    assert [(gap.scope_name, gap.kind) for gap in diff.scope_gaps] == [
        ("prod", "INCOMPLETE_CURRENT"),
        ("staging", "MISSING_IN_CURRENT"),
    ]


def test_diff_reviews_flags_duplicate_environments_and_audit_reviews() -> None:
    env_a = assessment()
    env_a["environment_display_name"] = "prod"
    env_a["findings"] = [_finding_dict(FINDING, fingerprint="fp-1")]

    env_b = assessment()
    env_b["id"] = str(ASSESSMENT_2)
    env_b["environment_display_name"] = "prod"

    dup_diff = diff_reviews(
        _review_model(REVIEW, assessments=[env_a, env_b]),
        _review_model(REVIEW_2, assessments=[env_a]),
    )
    assert dup_diff.resolved == ()
    assert any(
        gap.scope_name == "prod" and gap.kind == "DUPLICATE_SCOPE" for gap in dup_diff.scope_gaps
    )

    audit_diff = diff_reviews(
        _review_model(REVIEW, audit_mode="INFRASTRUCTURE_AWARE"),
        _review_model(REVIEW_2),
    )
    assert audit_diff.complete is False
    assert [(gap.scope_name, gap.kind) for gap in audit_diff.scope_gaps] == [
        ("audit", "AUDIT_UNCOMPARABLE")
    ]


def test_diff_reviews_supports_code_lane_and_review_outcomes() -> None:
    base_code = code_assessment()
    base_code["findings"] = [_finding_dict(FINDING, fingerprint="fp-code-old")]
    curr_code = code_assessment()
    curr_code["id"] = str(CODE_ASSESSMENT)
    curr_code["findings"] = [_finding_dict(FINDING_2, fingerprint="fp-code-new")]

    base_detail = _review_model(REVIEW, assessments=[], assessment_count=0, code=base_code)
    curr_detail = _review_model(REVIEW_2, assessments=[], assessment_count=0, code=curr_code)

    url = f"https://proofline.sh/organizations/{ORG}/reviews/{REVIEW}"
    diff = diff_reviews(
        ReviewOutcome("COMPLETED", url, base_detail),
        ReviewOutcome("COMPLETED", url, curr_detail),
    )

    assert diff.complete is True
    assert [(item.scope_kind, item.finding.finding_fingerprint) for item in diff.introduced] == [
        ("code", "fp-code-new")
    ]
    assert [(item.scope_kind, item.finding.finding_fingerprint) for item in diff.resolved] == [
        ("code", "fp-code-old")
    ]

    timed_out = ReviewOutcome("TIMED_OUT", url, None, reason="Timed out waiting for completion.")
    gap_diff = diff_reviews(base_detail, timed_out)
    assert gap_diff.complete is False
    assert [(gap.scope_name, gap.kind) for gap in gap_diff.scope_gaps] == [
        ("review", "MISSING_REVIEW")
    ]
