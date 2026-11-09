"""The severity gate matches `proofline ci review --fail-on`."""

from __future__ import annotations

import inspect
from typing import Any

import pytest
from pydantic import SecretStr

from proofline import AsyncProoflineClient, CustomerReviewDetail, ProoflineClient
from proofline.outcomes import ReviewOutcome, outcome

from .fixtures import ORG, REVIEW, TOKEN, assessment, code_assessment, finding, review
from .http_server import Reply, Server

URL = "https://proofline.sh/orgs/by-id/org/reviews/review"


def counts(open_findings: Any = 0, serious_findings: Any = 0) -> dict[str, Any]:
    return {
        "open_findings": open_findings,
        "serious_findings": serious_findings,
        "accepted_risks": 0,
        "not_assessed": [],
    }


def code_finding(severity: str, lifecycle: str = "NEW") -> dict[str, Any]:
    return {**finding(), "severity": severity, "lifecycle_state": lifecycle}


def read(body: dict[str, Any], forced: Any = None) -> ReviewOutcome:
    result = outcome(CustomerReviewDetail.from_dict(body), URL, forced)
    assert result is not None
    return result


def env_review(open_items: Any, status: str = "COMPLETED", **extra: Any) -> dict[str, Any]:
    return {**review(status), "open_items": open_items, **extra}


def code_only(code: dict[str, Any], open_items: Any = None, **extra: Any) -> dict[str, Any]:
    if open_items is None:
        open_items = counts()
    return {
        **review(),
        "assessment_count": 0,
        "assessments": [],
        "code_assessment": code,
        "open_items": open_items,
        **extra,
    }


def test_completeness_decides_before_the_open_finding_counts() -> None:
    serious = counts(1, 1)
    incomplete = {**review(), "assessments": [assessment("INCOMPLETE")], "open_items": serious}
    assert read(env_review(serious)).gate("SERIOUS") == "REACHED"
    assert read(incomplete).status == "INCOMPLETE"
    assert read(incomplete).gate("SERIOUS") == "NOT_COMPLETE"
    assert read(env_review(serious, "FAILED")).gate("SERIOUS") == "NOT_COMPLETE"
    assert read(env_review(serious, "STOPPED")).gate("SERIOUS") == "NOT_COMPLETE"
    assert read(env_review(serious), "TIMED_OUT").gate("SERIOUS") == "UNAVAILABLE"
    assert ReviewOutcome("TIMED_OUT", URL).gate("WARNING") == "UNAVAILABLE"
    # A gap decides before the missing counts do.
    incomplete["open_items"] = None
    assert read(incomplete).gate("SERIOUS") == "NOT_COMPLETE"


@pytest.mark.parametrize(
    ("open_items", "fail_on", "result"),
    [
        (counts(1, 1), "WARNING", "REACHED"),
        (counts(1, 0), "WARNING", "REACHED"),
        (counts(1, 0), "SERIOUS", "NOT_REACHED"),
        (counts(0, 0), "WARNING", "NOT_REACHED"),
        (counts(0, 0), "SERIOUS", "NOT_REACHED"),
        # A threshold that cannot be measured is never NOT_REACHED.
        (None, "WARNING", "UNAVAILABLE"),
        (None, "SERIOUS", "UNAVAILABLE"),
        ({"open_findings": 0}, "WARNING", "UNAVAILABLE"),
        (counts("0", 0), "WARNING", "UNAVAILABLE"),
        (counts(0, -1), "SERIOUS", "UNAVAILABLE"),
        (counts(False, 0), "WARNING", "UNAVAILABLE"),
    ],
)
def test_a_completed_review_is_measured_by_the_server_open_finding_counts(
    open_items: Any, fail_on: Any, result: str
) -> None:
    assert read(env_review(open_items)).gate(fail_on) == result


def test_missing_open_items_field_is_unavailable() -> None:
    body = review()
    assert "open_items" not in body
    assert read(body).status == "COMPLETED"
    assert read(body).gate("WARNING") == "UNAVAILABLE"


@pytest.mark.parametrize(
    ("severity", "lifecycle", "fail_on", "result"),
    [
        ("SERIOUS", "NEW", "SERIOUS", "REACHED"),
        ("SERIOUS", "REINTRODUCED", "SERIOUS", "REACHED"),
        ("SERIOUS", "UNCHANGED", "WARNING", "REACHED"),
        ("WARNING", "NEW", "WARNING", "REACHED"),
        ("WARNING", "NEW", "SERIOUS", "NOT_REACHED"),
        ("SERIOUS", "RESOLVED", "SERIOUS", "NOT_REACHED"),
        # A severity a newer server sends is never read as below a threshold.
        ("CRITICAL", "NEW", "SERIOUS", "REACHED"),
    ],
)
def test_complete_code_findings_reach_by_lifecycle_and_severity(
    severity: str, lifecycle: str, fail_on: Any, result: str
) -> None:
    code = {**code_assessment(), "findings": [code_finding(severity, lifecycle)]}
    assert read(env_review(counts(), code_assessment=code)).gate(fail_on) == result
    assert read(code_only(code)).gate(fail_on) == result


@pytest.mark.parametrize(
    "code",
    [
        {**code_assessment("INCOMPLETE")},
        {**code_assessment(), "incompleteness_kind": "MODEL_BUDGET_EXHAUSTED"},
        {**code_assessment(), "head_commit_sha": "c" * 40},
        {**code_assessment(), "base_commit_sha": "c" * 40},
        {
            **code_assessment(),
            "findings": [
                {**code_finding("WARNING"), "risk_domain": "[withheld: environment value]"}
            ],
        },
    ],
)
def test_unusable_code_records_supply_no_findings_and_never_complete_a_code_only_review(
    code: dict[str, Any],
) -> None:
    code = {**code, "findings": [*code["findings"], code_finding("SERIOUS")]}
    recorded = {"head_commit_sha": "A" * 40, "base_commit_sha": "B" * 40}
    # Complete environments complete a review even beside an unusable CODE record.
    beside = env_review(counts(), code_assessment=code, **recorded)
    assert read(beside).status == "COMPLETED"
    assert read(beside).gate("SERIOUS") == "NOT_REACHED"
    assert read(code_only(code, **recorded)).gate("SERIOUS") == "NOT_COMPLETE"


def test_code_commits_are_compared_only_where_the_review_recorded_them() -> None:
    code = {**code_assessment(), "findings": [code_finding("SERIOUS")]}
    assert read(code_only(code)).gate("SERIOUS") == "REACHED"
    assert read(code_only(code, head_commit_sha="A" * 40)).gate("SERIOUS") == "REACHED"
    assert read(code_only(code, head_commit_sha=None)).gate("SERIOUS") == "REACHED"


def test_unknown_threshold_is_refused() -> None:
    threshold: Any = "HIGH"
    with pytest.raises(ValueError):
        read(env_review(counts())).gate(threshold)


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_wait_for_review_result_measures_the_threshold(mode: str) -> None:
    body = env_review(counts(2, 1))
    with Server(lambda request, index: Reply(body=body)) as server:
        if mode == "sync":
            with ProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                result = client.wait_for_review(ORG, REVIEW, timeout=5)
        else:
            async with AsyncProoflineClient(SecretStr(TOKEN), base_url=server.url) as client:
                waited = client.wait_for_review(ORG, REVIEW, timeout=5)
                assert inspect.isawaitable(waited)
                result = await waited
    assert result.status == "COMPLETED"
    assert result.gate("SERIOUS") == "REACHED"
    assert result.gate(fail_on="WARNING") == "REACHED"
    assert len(server.requests) == 1
