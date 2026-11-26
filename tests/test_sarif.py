from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest

from proofline import ProoflineError, review_sarif
from proofline._generated.models.customer_review_detail import CustomerReviewDetail
from proofline._transport import VERSION
from proofline.outcomes import AssessmentGap, ReviewOutcome
from proofline.sarif import CODE_DOMAINS, DOMAINS, SCHEMA
from tests.fixtures import ASSESSMENT, ORG, REVIEW, review

HEAD = "0123456789abcdef0123456789abcdef01234567"
BASE = "89abcdef0123456789abcdef0123456789abcdef"


def make_ref(path: str = "src/main.py", start: int = 10, end: int = 20) -> dict[str, Any]:
    return {
        "kind": "repository_file",
        "label": "verified file read",
        "provenance_status": "VERIFIED_REPOSITORY_READ",
        "commit_sha": HEAD,
        "repository_path": path,
        "start_line": start,
        "end_line": end,
    }


def make_finding(
    fid: str = "0190f3a0-0000-7000-8000-000000000101",
    domain: str = "logic",
    severity: str = "SERIOUS",
    refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": fid,
        "risk_domain": domain,
        "severity": severity,
        "claim": "Potential division by zero",
        "impact": "Can crash server process on empty input",
        "lifecycle_state": "NEW",
        "evidence_refs": refs if refs is not None else [make_ref()],
        "finding_fingerprint": "fp123456789",
        "comment_reactions": [],
        "rule_refs": [],
        "symbols": [],
    }


def test_review_sarif_basic_projection() -> None:
    doc = review("COMPLETED")
    doc.update({
        "head_commit_sha": HEAD,
        "base_commit_sha": BASE,
        "assessment_count": 0,
        "assessments": [],
        "repository_full_name": "org/repo",
        "pull_request_number": 12,
        "run_number": 1,
        "code_assessment": {
            "id": "0190f3a0-0000-7000-8000-000000000055",
            "status": "COMPLETED",
            "base_commit_sha": BASE,
            "head_commit_sha": HEAD,
            "findings": [make_finding()],
            "incompleteness_kind": None,
        },
    })
    review_model = CustomerReviewDetail.from_dict(doc)
    outcome = ReviewOutcome(
        status="COMPLETED",
        review_url=f"https://proofline.sh/reviews/{REVIEW}",
        review=review_model,
    )

    log = review_sarif(outcome, ORG)
    assert log["$schema"] == SCHEMA
    assert log["version"] == "2.1.0"

    runs = log["runs"]
    assert len(runs) == 1
    run = runs[0]

    assert run["tool"]["driver"]["name"] == "Proofline"
    assert run["tool"]["driver"]["version"] == VERSION
    rule_ids = [r["id"] for r in run["tool"]["driver"]["rules"]]
    assert rule_ids == list(DOMAINS) + list(CODE_DOMAINS)

    assert run["invocations"][0]["executionSuccessful"] is True
    assert run["invocations"][0]["toolExecutionNotifications"] == []

    results = run["results"]
    assert len(results) == 1
    result = results[0]
    assert result["ruleId"] == "logic"
    assert result["level"] == "error"
    assert result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/main.py"
    assert result["locations"][0]["physicalLocation"]["region"]["startLine"] == 10
    assert result["locations"][0]["physicalLocation"]["region"]["endLine"] == 20
    assert result["partialFingerprints"] == {"prooflineFinding/v1": "fp123456789"}

    props = run["properties"]
    assert props["reviewId"] == str(REVIEW)
    assert props["organizationId"] == str(ORG)
    assert props["headCommitSha"] == HEAD
    assert props["repository"] == "org/repo"
    assert props["pullRequestNumber"] == 12
    assert props["runNumber"] == 1
    assert props["outcome"] == "COMPLETED"


def test_review_sarif_handles_env_assessments_and_gaps() -> None:
    env_finding = make_finding(
        fid="0190f3a0-0000-7000-8000-000000000102",
        domain="network_reachability",
        severity="WARNING",
    )
    doc = review("INCOMPLETE")
    doc.update({
        "head_commit_sha": HEAD,
        "base_commit_sha": BASE,
        "assessment_count": 1,
        "assessments": [
            {
                "id": str(ASSESSMENT),
                "status": "COMPLETED",
                "environment_display_name": "production",
                "findings": [env_finding],
                "domains": [],
                "checks": {"families": [], "receipt_recorded": True, "status": "READY"},
            }
        ],
        "code_assessment": None,
    })
    review_model = CustomerReviewDetail.from_dict(doc)
    outcome = ReviewOutcome(
        status="INCOMPLETE",
        review_url=f"https://proofline.sh/reviews/{REVIEW}",
        review=review_model,
        gaps=(
            AssessmentGap(
                assessment_id=ASSESSMENT,
                status="INCOMPLETE",
                reason_codes=("WORLD_UNAVAILABLE",),
            ),
        ),
    )

    log = review_sarif(outcome, ORG)
    run = log["runs"][0]
    assert run["invocations"][0]["executionSuccessful"] is False

    notifications = run["invocations"][0]["toolExecutionNotifications"]
    reasons = [n["properties"]["reasonCode"] for n in notifications]
    assert "WORLD_UNAVAILABLE" in reasons
    assert "REVIEW_RESULT_INCOMPLETE" in reasons

    result = run["results"][0]
    assert result["ruleId"] == "network_reachability"
    assert result["level"] == "warning"
    assert result["properties"]["lane"] == "ENV"
    assert result["properties"]["environment"] == "production"


def test_review_sarif_validation_rejections() -> None:
    doc = review("COMPLETED")
    doc["head_commit_sha"] = HEAD
    doc["kind"] = "COMMIT"
    review_model = CustomerReviewDetail.from_dict(doc)
    outcome = ReviewOutcome(status="COMPLETED", review_url="", review=review_model)
    with pytest.raises(ProoflineError) as raised:
        review_sarif(outcome, ORG)
    assert raised.value.type == "urn:proofline:sdk:sarif-refused"

    # Invalid head commit
    doc["kind"] = "PR"
    doc["head_commit_sha"] = "not-a-sha"
    review_model = CustomerReviewDetail.from_dict(doc)
    outcome = ReviewOutcome(status="COMPLETED", review_url="", review=review_model)
    with pytest.raises(ProoflineError) as raised:
        review_sarif(outcome, ORG)
    assert raised.value.type == "urn:proofline:sdk:sarif-refused"

    # Missing review
    empty_outcome = ReviewOutcome(status="COMPLETED", review_url="", review=None)
    with pytest.raises(TypeError):
        review_sarif(empty_outcome, ORG)

    # Missing org id
    doc["head_commit_sha"] = HEAD
    valid_review = CustomerReviewDetail.from_dict(doc)
    valid_outcome = ReviewOutcome(status="COMPLETED", review_url="", review=valid_review)
    with pytest.raises(TypeError):
        review_sarif(valid_outcome, "")
