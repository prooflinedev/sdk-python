import json

import pytest

from proofline import CustomerReviewDetail, ReviewOutcome, review_sarif
from proofline.outcomes import outcome
from tests.fixtures import ORG, assessment, code_assessment, finding, review

HEAD = "a" * 40
URL = "https://proofline.sh/reviews/example"


def test_sarif_projects_both_lanes_and_only_verified_reviewed_locations() -> None:
    citation = {
        "kind": "repository_file",
        "label": "private citation label",
        "provenance_status": "VERIFIED_REPOSITORY_READ",
        "commit_sha": HEAD.upper(),
        "repository_path": "src/a #%.py",
        "start_line": 3,
    }
    env = assessment()
    env["findings"] = [
        {
            **finding(),
            "severity": "SERIOUS",
            "risk_domain": "data_integrity",
            "claim": "[claim] {0}",
            "finding_fingerprint": "retained",
            "evidence_refs": [
                citation,
                citation,
                {**citation, "repository_path": "src/b.py", "end_line": 8},
                {**citation, "commit_sha": "b" * 40},
                {**citation, "repository_path": "../outside.py"},
                {**citation, "end_line": 2},
                {**citation, "companion_repository": "owner/other"},
                {**citation, "provenance_status": "LEGACY_UNSTRUCTURED"},
            ],
        }
    ]
    code = code_assessment("INCOMPLETE")
    code["incompleteness_kind"] = "MODEL_BUDGET_EXHAUSTED"
    code["findings"] = [{**finding(), "severity": "WARNING", "risk_domain": "logic"}]
    detail = CustomerReviewDetail.from_dict(
        {
            **review(),
            "kind": "PULL_REQUEST",
            "head_commit_sha": HEAD.upper(),
            "assessments": [env],
            "code_assessment": code,
        }
    )
    result = outcome(detail, URL)
    assert result is not None and result.status == "COMPLETED"
    report = review_sarif(result, ORG)
    assert report["version"] == "2.1.0"
    assert "private citation label" not in json.dumps(report)
    run = report["runs"][0]
    assert run["properties"]["organizationId"] == str(ORG)
    assert run["properties"]["headCommitSha"] == HEAD
    code_result, env_result = run["results"]
    assert code_result["locations"] == []
    assert code_result["properties"]["locationStatus"] == "NO_VERIFIED_REVIEWED_LOCATION"
    assert "partialFingerprints" not in code_result
    assert env_result["partialFingerprints"] == {"prooflineFinding/v1": "retained"}
    assert env_result["message"]["text"].startswith(r"\[claim\] {{0}}")
    for item in run["results"]:
        assert run["tool"]["driver"]["rules"][item["ruleIndex"]]["id"] == item["ruleId"]
    assert env_result["locations"] == [
        {
            "physicalLocation": {
                "artifactLocation": {"uri": "src/a%20%23%25.py", "uriBaseId": "%SRCROOT%"},
                "region": {"startLine": 3, "endLine": 3},
            },
        }
    ]
    assert len(env_result["relatedLocations"]) == 1
    assert [ref["locationStatus"] for ref in env_result["properties"]["evidenceReferences"]] == [
        "LOCATED",
        "LOCATED",
        "LOCATED",
        "DIFFERENT_COMMIT",
        "INVALID_PATH",
        "INVALID_REGION",
        "COMPANION_REPOSITORY",
        "UNVERIFIED_PROVENANCE",
    ]
    assert run["invocations"] == [
        {
            "executionSuccessful": False,
            "toolExecutionNotifications": [
                {
                    "level": "error",
                    "message": {"text": "Code-only: MODEL_BUDGET_EXHAUSTED"},
                    "properties": {
                        "reasonCode": "MODEL_BUDGET_EXHAUSTED",
                        "assessmentId": code["id"],
                    },
                }
            ],
        }
    ]


def test_sarif_reports_timeout_and_receipt_gap() -> None:
    env = assessment()
    env["checks"]["receipt_recorded"] = False
    detail = CustomerReviewDetail.from_dict(
        {**review("RUNNING"), "kind": "PULL_REQUEST", "head_commit_sha": HEAD, "assessments": [env]}
    )
    result = outcome(detail, URL, "TIMED_OUT")
    assert result is not None
    run = review_sarif(result, str(ORG))["runs"][0]
    assert run["properties"]["outcome"] is None
    invocation = run["invocations"][0]
    assert invocation["executionSuccessful"] is False
    assert [notice["properties"] for notice in invocation["toolExecutionNotifications"]] == [
        {"reasonCode": "CHECK_RECEIPT_ABSENT", "assessmentId": env["id"]},
        {"reasonCode": "REVIEW_IN_PROGRESS"},
    ]


def test_sarif_requires_a_retained_pr_at_the_expected_full_head() -> None:
    with pytest.raises(ValueError, match="retained pull-request"):
        review_sarif(ReviewOutcome("TIMED_OUT", URL), ORG)
    detail = CustomerReviewDetail.from_dict({**review(), "head_commit_sha": HEAD})
    with pytest.raises(ValueError, match="retained pull-request"):
        review_sarif(ReviewOutcome("COMPLETED", URL, detail), ORG)
    detail.kind = "PULL_REQUEST"
    result = outcome(detail, URL, head_commit_sha="b" * 40)
    assert result is not None
    with pytest.raises(ValueError, match="full SHA"):
        review_sarif(result, ORG)
    detail.head_commit_sha = HEAD[:7]
    with pytest.raises(ValueError, match="full SHA"):
        review_sarif(ReviewOutcome("COMPLETED", URL, detail), ORG)


def test_sarif_marks_a_complete_run_successful_and_excludes_unavailable_code() -> None:
    raw = {**review(), "kind": "PULL_REQUEST", "head_commit_sha": HEAD}
    detail = CustomerReviewDetail.from_dict(raw)
    result = outcome(detail, URL)
    assert result is not None
    run = review_sarif(result, ORG)["runs"][0]
    assert run["invocations"] == [
        {"executionSuccessful": True, "toolExecutionNotifications": []},
    ]

    code = code_assessment()
    code["head_commit_sha"] = "b" * 40
    code["findings"] = [{**finding(), "severity": "WARNING", "risk_domain": "logic"}]
    detail = CustomerReviewDetail.from_dict({**raw, "code_assessment": code})
    result = outcome(detail, URL)
    assert result is not None and result.status == "COMPLETED"
    run = review_sarif(result, ORG)["runs"][0]
    assert run["results"] == []
    assert "codeAssessment" not in run["properties"]
    invocation = run["invocations"][0]
    assert invocation["executionSuccessful"] is False
    assert invocation["toolExecutionNotifications"][0]["properties"] == {
        "reasonCode": "CODE_ASSESSMENT_UNAVAILABLE",
    }
