"""Tests for ``gate_review`` — the CI gating rule.

These tests port the CLI's ``ci_verdict`` test table and the TypeScript
SDK's ``gateReview`` tests. They build ``ReviewOutcome`` objects directly
from synthetic review data and measure them against WARNING and SERIOUS
thresholds.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest

from proofline import gate_review
from proofline.outcomes import ReviewOutcome, outcome

ORG = UUID("00000000-0000-4000-8000-000000000001")
REVIEW_ID = UUID("00000000-0000-4000-8000-000000000003")
ASSESSMENT_ID = UUID("00000000-0000-4000-8000-000000000004")
CODE_ID = UUID("00000000-0000-4000-8000-000000000006")
URL = "https://proofline.sh/orgs/by-id/" + str(ORG) + "/reviews/" + str(REVIEW_ID)


def _counts(open_findings: int = 0, serious_findings: int = 0) -> dict[str, Any]:
    return {
        "accepted_risks": 0,
        "not_assessed": [],
        "open_findings": open_findings,
        "serious_findings": serious_findings,
    }


def _assessment(status: str = "COMPLETED") -> dict[str, Any]:
    return {
        "id": str(ASSESSMENT_ID),
        "environment_display_name": "production",
        "status": status,
        "domains": [],
        "findings": [],
        "checks": {"families": [], "receipt_recorded": True, "status": "READY"},
    }


def _review(
    status: str = "COMPLETED",
    extra: dict[str, Any] | None = None,
    assessments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if assessments is None:
        assessments = [_assessment()]
    base: dict[str, Any] = {
        "id": str(REVIEW_ID),
        "public_key": "rev_" + str(REVIEW_ID).replace("-", ""),
        "kind": "PULL_REQUEST",
        "status": status,
        "assessment_count": len(assessments),
        "environment_display_names": ["production"],
        "finding_count": 0,
        "trigger_origin": "MANUAL",
        "publication": "WITHHELD",
        "created_at": "2026-09-30T12:00:00Z",
        "stoppable": False,
        "related_reviews": [],
        "subjects": [],
        "assessments": assessments,
        "actions": {
            "promote_findings": False,
            "publish": False,
            "rerun": False,
            "stop": False,
            "validate_findings": False,
        },
        "head_commit_sha": "a" * 40,
        "base_commit_sha": "b" * 40,
    }
    if extra:
        base.update(extra)
    return base


def _code_assessment(
    findings: list[dict[str, Any]],
    status: str = "COMPLETED",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": str(CODE_ID),
        "status": status,
        "head_commit_sha": "a" * 40,
        "base_commit_sha": "b" * 40,
        "incompleteness_kind": None,
        "findings": findings,
    }
    if extra:
        base.update(extra)
    return base


def _code_finding(severity: str, lifecycle_state: str = "NEW") -> dict[str, Any]:
    return {
        "id": str(CODE_ID),
        "severity": severity,
        "risk_domain": "code",
        "claim": "claim",
        "impact": "impact",
        "lifecycle_state": lifecycle_state,
        "evidence_refs": [],
        "rule_refs": [],
        "symbols": [],
        "comment_reactions": [],
    }


def _outcome(body: dict[str, Any]) -> ReviewOutcome:
    """Build a real ReviewOutcome from synthetic review JSON."""
    from proofline._generated.models.customer_review_detail import CustomerReviewDetail

    review = CustomerReviewDetail.from_dict(body)
    result = outcome(review, URL, review_id=REVIEW_ID)
    assert result is not None
    return result


# --- Completeness decides before the open-finding counts ---


def test_completeness_decides_before_open_finding_counts() -> None:
    serious = {"open_items": _counts(1, 1)}
    completed = _outcome(_review("COMPLETED", serious))
    assert completed.status == "COMPLETED"
    assert gate_review(completed, fail_on="SERIOUS") == "REACHED"

    incomplete = _outcome(_review("COMPLETED", serious, [_assessment("INCOMPLETE")]))
    assert incomplete.status == "INCOMPLETE"
    assert gate_review(incomplete, fail_on="SERIOUS") == "NOT_COMPLETE"

    for status in ("INCOMPLETE", "FAILED", "STOPPED"):
        result = _outcome(_review(status, serious))
        assert gate_review(result, fail_on="SERIOUS") == "NOT_COMPLETE", status

    # A gap decides before the missing counts do.
    gap = _outcome(_review("COMPLETED", {"open_items": None}, [_assessment("INCOMPLETE")]))
    assert gate_review(gap, fail_on="WARNING") == "NOT_COMPLETE"


def test_timed_out_is_unavailable() -> None:
    timed_out = ReviewOutcome("TIMED_OUT", URL, review=None)
    assert gate_review(timed_out, fail_on="WARNING") == "UNAVAILABLE"


def test_no_review_is_unavailable() -> None:
    no_review = ReviewOutcome("COMPLETED", URL, review=None)
    assert gate_review(no_review, fail_on="WARNING") == "UNAVAILABLE"


# --- A completed review is measured by the server's open-finding counts ---


@pytest.mark.parametrize(
    ("open_items", "fail_on", "expected"),
    [
        (_counts(1, 1), "WARNING", "REACHED"),
        (_counts(1, 1), "SERIOUS", "REACHED"),
        (_counts(1, 0), "WARNING", "REACHED"),
        (_counts(1, 0), "SERIOUS", "NOT_REACHED"),
        (_counts(0, 0), "WARNING", "NOT_REACHED"),
        (_counts(0, 0), "SERIOUS", "NOT_REACHED"),
        # A threshold that cannot be measured is never NOT_REACHED.
        (None, "WARNING", "UNAVAILABLE"),
        ({"open_findings": 0}, "WARNING", "UNAVAILABLE"),
        (_counts("0", 0), "WARNING", "UNAVAILABLE"),  # type: ignore[arg-type]
        (_counts(0, -1), "SERIOUS", "UNAVAILABLE"),
        (_counts(0.5, 0), "WARNING", "UNAVAILABLE"),  # type: ignore[arg-type]
        (_counts(True, 0), "WARNING", "UNAVAILABLE"),  # type: ignore[arg-type]
    ],
)
def test_completed_review_measured_by_open_finding_counts(
    open_items: Any, fail_on: str, expected: str
) -> None:
    body = _review("COMPLETED", {"open_items": open_items})
    result = _outcome(body)
    assert result.status == "COMPLETED"
    assert gate_review(result, fail_on=fail_on) == expected  # type: ignore[arg-type]


# --- Complete CODE findings of the review's own commits reach by lifecycle and severity ---


@pytest.mark.parametrize(
    ("severity", "lifecycle", "fail_on", "expected"),
    [
        ("SERIOUS", "NEW", "SERIOUS", "REACHED"),
        ("SERIOUS", "UNCHANGED", "WARNING", "REACHED"),
        ("WARNING", "NEW", "WARNING", "REACHED"),
        ("WARNING", "NEW", "SERIOUS", "NOT_REACHED"),
        ("SERIOUS", "RESOLVED", "SERIOUS", "NOT_REACHED"),
        # A severity a newer server sends is never read as below a threshold.
        ("CRITICAL", "NEW", "SERIOUS", "REACHED"),
        ("NOTE", "NEW", "SERIOUS", "REACHED"),
    ],
)
def test_code_findings_reach_by_lifecycle_and_severity(
    severity: str, lifecycle: str, fail_on: str, expected: str
) -> None:
    code = _code_assessment([_code_finding(severity, lifecycle)])
    case = f"{severity} {lifecycle} {fail_on}"
    # Code-only review.
    code_only = _outcome(
        _review("COMPLETED", {"code_assessment": code, "open_items": _counts()}, [])
    )
    assert code_only.status == "COMPLETED", case
    assert gate_review(code_only, fail_on=fail_on) == expected, case
    # Beside complete environments, as the CLI measures it.
    beside = _outcome(_review("COMPLETED", {"code_assessment": code, "open_items": _counts()}))
    assert gate_review(beside, fail_on=fail_on) == expected, case


# --- Partial or foreign CODE records supply no findings ---


def test_partial_or_foreign_code_records_supply_no_findings() -> None:
    serious = [_code_finding("SERIOUS")]
    for code in [
        _code_assessment(serious, "INCOMPLETE", {"incompleteness_kind": "MODEL_BUDGET_EXHAUSTED"}),
        _code_assessment(serious, "COMPLETED", {"incompleteness_kind": "EVIDENCE_UNAVAILABLE"}),
        _code_assessment(serious, "RUNNING"),
        _code_assessment(serious, "COMPLETED", {"head_commit_sha": "c" * 40}),
        _code_assessment(serious, "COMPLETED", {"base_commit_sha": "c" * 40}),
    ]:
        result = _outcome(_review("COMPLETED", {"code_assessment": code, "open_items": _counts()}))
        assert result.status == "COMPLETED"
        assert gate_review(result, fail_on="WARNING") == "NOT_REACHED"
    # A code-only review with such a record is not complete.
    code_only = _outcome(
        _review(
            "COMPLETED",
            {"code_assessment": _code_assessment(serious, "RUNNING"), "open_items": _counts()},
            [],
        )
    )
    assert gate_review(code_only, fail_on="WARNING") == "NOT_COMPLETE"


# --- An invalid threshold throws instead of measuring ---


@pytest.mark.parametrize("fail_on", ["warning", "CRITICAL", "INFO", "", "serious"])
def test_invalid_threshold_raises_value_error(fail_on: str) -> None:
    result = _outcome(_review("COMPLETED", {"open_items": _counts()}))
    with pytest.raises(ValueError):
        gate_review(result, fail_on=fail_on)  # type: ignore[arg-type]
