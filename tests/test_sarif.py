"""SARIF projection of a retained pull-request review."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import pytest

from proofline import (
    CustomerReviewDetail,
    ProoflineClient,
    SarifExportError,
    review_sarif,
)
from proofline import __version__ as SDK_VERSION

from .fixtures import ORG, REVIEW, review
from .http_server import Reply, Request, Server

HEAD = "a" * 40
BASE = "b" * 40
OTHER = "9876543210abcdef0123456789abcdef01234567"
CLAIM = "The order receipt is applied twice."
IMPACT = "The customer can be charged twice."
CANARY = "world-evidence-canary"
TOKEN = "pln_test_sdk_credential_canary"
URL = f"https://proofline.sh/orgs/by-id/{ORG}/reviews/{REVIEW}"


def finding(
    number: int,
    severity: str = "WARNING",
    refs: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": str(UUID(int=0x0190F3A0000070008000000000000100 + number)),
        "severity": severity,
        "risk_domain": "data_integrity",
        "claim": CLAIM,
        "impact": IMPACT,
        "symbols": [],
        "lifecycle_state": "ACTIVE",
        "evidence_refs": [] if refs is None else refs,
        "rule_refs": [],
        "comment_reactions": [],
        "remediation": "Make the order receipt idempotent.",
        "evidence_values": CANARY,
    }
    body.update(extra)
    return body


def code_ref(path: str, start: int, end: int | None = None, **extra: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "kind": "repository_file",
        "label": CANARY,
        "provenance_status": "VERIFIED_REPOSITORY_READ",
        "commit_sha": HEAD,
        "repository_path": path,
        "start_line": start,
        "url": f"https://elsewhere.example/{CANARY}",
    }
    if end is not None:
        body["end_line"] = end
    body.update(extra)
    return body


def pull_request(findings: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    document = review()
    document["kind"] = "PULL_REQUEST"
    document["head_commit_sha"] = HEAD
    document["repository_full_name"] = "acme/web"
    document["pull_request_number"] = 42
    document["run_number"] = 7
    document["operator_diagnostics"] = CANARY
    document["assessments"] = [
        {
            "id": document["assessments"][0]["id"],
            "environment_display_name": "production",
            "status": "COMPLETED",
            "domains": [],
            "findings": findings,
            "checks": {"families": [], "receipt_recorded": True, "status": "READY"},
            "world_evidence_values": CANARY,
        }
    ]
    document.update(extra)
    return document


def project(document: dict[str, Any], *, review_id: UUID = REVIEW) -> dict[str, Any]:
    return review_sarif(
        CustomerReviewDetail.from_dict(document),
        ORG,
        review_id=review_id,
        review_url=URL,
    )


def notice_codes(run: dict[str, Any]) -> list[str]:
    notes = run["invocations"][0]["toolExecutionNotifications"]
    return [note["properties"]["reasonCode"] for note in notes]


def run_of(document: dict[str, Any]) -> dict[str, Any]:
    report = project(document)
    assert report["version"] == "2.1.0"
    assert report["$schema"].endswith("sarif-schema-2.1.0.json")
    assert CANARY not in json.dumps(report)
    assert TOKEN not in json.dumps(report)
    runs = report["runs"]
    assert len(runs) == 1
    for result in runs[0]["results"]:
        rules = runs[0]["tool"]["driver"]["rules"]
        assert rules[result["ruleIndex"]]["id"] == result["ruleId"]
        assert "guid" not in result
        assert "fingerprints" not in result
        assert "correlationGuid" not in result
        assert "markdown" not in result["message"]
        assert "arguments" not in result["message"]
    return runs[0]


def test_completed_review_keeps_identity_locations_and_fingerprint() -> None:
    markup = "charge {twice} \\[note]"
    references = [
        code_ref("src/orders #100%.rs", 10, 14),
        code_ref("src/orders #100%.rs", 10, 14),
        code_ref("src/\u00e9.rs", 20),
        code_ref("src/orders.rs", 1, 2, commit_sha=OTHER),
        code_ref("src/orders.rs", 1, 2, commit_sha="main"),
        code_ref("src/orders.rs", 1, 2, commit_sha=None),
        code_ref("src/orders.rs", 1, 2, provenance_status="UNVERIFIED"),
        code_ref(
            "src/orders.rs",
            1,
            2,
            kind="companion_repository_file",
            companion_repository="acme/contracts",
        ),
        code_ref("src/orders.rs", 1, 2, companion_repository="acme/contracts"),
    ]
    for path in (
        "",
        "/etc/passwd",
        "../src/orders.rs",
        "src/../orders.rs",
        "src/./orders.rs",
        "src//orders.rs",
        "src\\orders.rs",
        "C:/orders.rs",
        "https://elsewhere.example/orders.rs",
        "src/\u001b[2J.rs",
        "src/\u202eorders.rs",
    ):
        references.append(code_ref(path, 1, 2))
    references.extend(
        (
            code_ref("src/orders.rs", 0, 2),
            code_ref("src/orders.rs", 2, 1),
            code_ref("src/orders.rs", 1, 2, start_line=None),
            {
                "kind": "world_entity",
                "label": CANARY,
                "provenance_status": "PINNED_WORLD_ENTITY",
                "world_entity_id": CANARY,
                "values": CANARY,
            },
        )
    )
    retained = finding(
        1,
        "SERIOUS",
        references,
        claim=markup,
        finding_fingerprint="fingerprint-v1",
    )
    older = finding(2, "WARNING", [], remediation=None)
    run = run_of(pull_request([retained, older]))
    assert run["tool"]["driver"]["name"] == "Proofline"
    assert run["tool"]["driver"]["version"] == SDK_VERSION
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]][11] == "data_integrity"
    assert len(run["tool"]["driver"]["rules"]) == 18
    assert run["invocations"][0]["executionSuccessful"] is True
    assert run["invocations"][0]["toolExecutionNotifications"] == []
    properties = run["properties"]
    assert properties["reviewId"] == str(REVIEW)
    assert properties["organizationId"] == str(ORG)
    assert properties["reviewUrl"] == URL
    assert properties["headCommitSha"] == HEAD
    assert properties["repository"] == "acme/web"
    assert properties["pullRequestNumber"] == 42
    assert properties["runNumber"] == 7
    assert properties["reviewStatus"] == "COMPLETED"
    assert properties["outcome"] == "COMPLETED"
    assert properties["assessmentCount"] == 1
    assert "codeAssessment" not in properties
    assert len(run["results"]) == 2
    serious = run["results"][0]
    assert serious["level"] == "error"
    assert serious["ruleId"] == "data_integrity"
    assert serious["ruleIndex"] == 11
    assert serious["message"]["text"] == "charge {{twice}} \\\\\\[note\\]\n\n" + IMPACT
    assert serious["partialFingerprints"] == {"prooflineFinding/v1": "fingerprint-v1"}
    assert serious["properties"]["findingId"] == retained["id"]
    assert serious["properties"]["environment"] == "production"
    assert serious["properties"]["lane"] == "ENV"
    assert serious["properties"]["lifecycleState"] == "ACTIVE"
    assert serious["properties"]["remediation"] == "Make the order receipt idempotent."
    assert serious["properties"]["locationStatus"] == "LOCATED"
    locations = serious["locations"]
    assert len(locations) == 1
    artifact = locations[0]["physicalLocation"]["artifactLocation"]
    assert artifact["uri"] == "src/orders%20%23100%25.rs"
    assert artifact["uriBaseId"] == "%SRCROOT%"
    assert locations[0]["physicalLocation"]["region"] == {"startLine": 10, "endLine": 14}
    related = serious["relatedLocations"]
    assert len(related) == 1
    assert related[0]["physicalLocation"]["artifactLocation"]["uri"] == "src/%C3%A9.rs"
    assert related[0]["physicalLocation"]["region"] == {"startLine": 20, "endLine": 20}
    refs = serious["properties"]["evidenceReferences"]
    assert [ref["locationStatus"] for ref in refs] == [
        "LOCATED",
        "LOCATED",
        "LOCATED",
        "DIFFERENT_COMMIT",
        "INVALID_COMMIT",
        "COMMIT_UNAVAILABLE",
        "UNVERIFIED_PROVENANCE",
        "COMPANION_REPOSITORY",
        "COMPANION_REPOSITORY",
        *["INVALID_PATH"] * 11,
        *["INVALID_REGION"] * 3,
        "NON_CODE_REFERENCE",
    ]
    assert refs[5]["commitSha"] is None
    assert refs[7]["companionRepository"] == "acme/contracts"
    assert refs[2]["endLine"] is None
    assert "label" not in refs[23]
    warning = run["results"][1]
    assert warning["level"] == "warning"
    assert warning["locations"] == []
    assert "relatedLocations" not in warning
    assert "partialFingerprints" not in warning
    assert "remediation" not in warning["properties"]
    assert warning["properties"]["locationStatus"] == "NO_VERIFIED_REVIEWED_LOCATION"
    again = project(pull_request([retained, older]))
    assert again == project(pull_request([retained, older]))


def test_uppercase_head_matches_its_evidence_and_is_stored_lowercase() -> None:
    head = "A" * 40
    document = pull_request(
        [finding(1, "WARNING", [code_ref("src/orders.rs", 3, 3, commit_sha=HEAD)])],
        head_commit_sha=head,
    )
    run = run_of(document)
    assert run["properties"]["headCommitSha"] == HEAD
    assert run["results"][0]["properties"]["locationStatus"] == "LOCATED"
    long_head = "ab" * 32
    document = pull_request([finding(1)], head_commit_sha=long_head.upper())
    assert run_of(document)["properties"]["headCommitSha"] == long_head


def test_code_findings_keep_their_lane_and_do_not_replace_environments() -> None:
    recorded = finding(1, "SERIOUS", [code_ref("src/orders.rs", 10, 14)], risk_domain="logic")
    code = {
        "id": "00000000-0000-4000-8000-000000000006",
        "status": "COMPLETED",
        "base_commit_sha": BASE,
        "head_commit_sha": HEAD,
        "incompleteness_kind": None,
        "findings": [recorded],
        "compatible_addition": CANARY,
    }
    code_only = pull_request(
        [], assessment_count=0, assessments=[], base_commit_sha=BASE, code_assessment=code
    )
    run = run_of(code_only)
    rules = [rule["id"] for rule in run["tool"]["driver"]["rules"]]
    assert rules[11] == "data_integrity"
    assert rules[18:] == [
        "logic",
        "edge_case",
        "error_handling",
        "state_transition",
        "concurrency",
        "resource_lifecycle",
        "credential_exposure",
        "test_marker",
        "removed_assertion",
        "debug_residue",
        "committed_secret",
    ]
    assert run["invocations"][0]["executionSuccessful"] is True
    assert run["properties"]["outcome"] == "COMPLETED"
    assert run["properties"]["codeAssessment"]["status"] == "COMPLETED"
    assert run["properties"]["codeAssessment"]["gapReasons"] == []
    result = run["results"][0]
    assert result["ruleId"] == "logic"
    assert result["ruleIndex"] == 18
    assert result["properties"]["lane"] == "CODE"
    assert "environment" not in result["properties"]
    assert result["message"]["text"] == f"Code-only finding\n\n{CLAIM}\n\n{IMPACT}"
    assert result["properties"]["locationStatus"] == "LOCATED"

    beside = pull_request(
        [finding(2, "WARNING", [], risk_domain="observability")],
        base_commit_sha=BASE,
        code_assessment=code,
    )
    run = run_of(beside)
    assert [item["properties"]["lane"] for item in run["results"]] == ["CODE", "ENV"]
    assert run["results"][1]["ruleIndex"] == 16
    assert run["invocations"][0]["executionSuccessful"] is True

    partial = dict(code)
    partial["status"] = "INCOMPLETE"
    partial["incompleteness_kind"] = "MODEL_BUDGET_EXHAUSTED"
    run = run_of(pull_request([finding(2)], base_commit_sha=BASE, code_assessment=partial))
    assert run["properties"]["outcome"] == "COMPLETED"
    assert run["invocations"][0]["executionSuccessful"] is False
    assert run["results"][0]["properties"]["lane"] == "CODE"
    notices = run["invocations"][0]["toolExecutionNotifications"]
    assert notices[0]["properties"]["reasonCode"] == "MODEL_BUDGET_EXHAUSTED"
    assert notices[0]["message"]["text"] == "Code-only: MODEL_BUDGET_EXHAUSTED"
    assert "codeAssessment" in run["properties"]

    withheld = dict(code)
    withheld["findings"] = [finding(1, risk_domain="[withheld: environment value]")]
    withheld["status"] = "COMPLETED"
    withheld["incompleteness_kind"] = None
    run = run_of(pull_request([finding(2)], base_commit_sha=BASE, code_assessment=withheld))
    assert [item["properties"]["lane"] for item in run["results"]] == ["ENV"]
    assert "codeAssessment" not in run["properties"]
    assert run["invocations"][0]["executionSuccessful"] is False
    assert run["invocations"][0]["toolExecutionNotifications"][-1]["properties"]["reasonCode"] == (
        "CODE_ASSESSMENT_UNAVAILABLE"
    )

    moved = dict(code)
    moved["head_commit_sha"] = OTHER
    run = run_of(
        pull_request(
            [], assessment_count=0, assessments=[], base_commit_sha=BASE, code_assessment=moved
        )
    )
    assert run["results"] == []
    assert notice_codes(run) == ["REVIEW_RESULT_INCOMPLETE", "CODE_ASSESSMENT_UNAVAILABLE"]


def test_gaps_are_named_and_a_partial_review_still_projects_findings() -> None:
    recorded = finding(1, "WARNING", [code_ref("src/orders.rs", 5)])
    checks = {
        "families": [
            {"name": "migrations", "outcome": "UNRESOLVED", "lifecycle": "GATING", "files": []}
        ],
        "receipt_recorded": False,
        "status": "READY",
    }
    for status, reason in (
        ("COMPLETED", "REVIEW_RESULT_INCOMPLETE"),
        ("PENDING", "REVIEW_IN_PROGRESS"),
        ("RUNNING", "REVIEW_IN_PROGRESS"),
        ("FAILED", "REVIEW_FAILED"),
        ("STOPPED", "REVIEW_STOPPED"),
        ("UNRECOGNIZED", "REVIEW_RESULT_INCOMPLETE"),
        ("SUPERSEDED", "REVIEW_RESULT_INCOMPLETE"),
    ):
        document = pull_request([recorded], status=status)
        document["assessments"][0]["status"] = "INCOMPLETE"
        document["assessments"][0]["incompleteness_kind"] = "WORLD_UNAVAILABLE"
        document["assessments"][0]["reason_codes"] = [
            "WORLD_UNAVAILABLE",
            "WORLD_UNAVAILABLE",
            "LITERAL_REASON",
        ]
        document["assessments"][0]["release_evidence_gap"] = "RELEASE_EVIDENCE_ABSENT"
        document["assessments"][0]["checks"] = checks
        document["assessments"][0]["environment_display_name"] = "prod {name}"
        run = run_of(document)
        assert run["properties"]["reviewStatus"] == status
        assert run["properties"]["outcome"] == {
            "PENDING": None,
            "RUNNING": None,
            "FAILED": "FAILED",
            "STOPPED": "STOPPED",
        }.get(status, "INCOMPLETE")
        assert run["invocations"][0]["executionSuccessful"] is False
        assert run["results"][0]["properties"]["findingId"] == recorded["id"]
        assert run["results"][0]["properties"]["locationStatus"] == "LOCATED"
        notices = run["invocations"][0]["toolExecutionNotifications"]
        assert [notice["properties"]["reasonCode"] for notice in notices] == [
            "CHECK_RECEIPT_ABSENT",
            "LITERAL_REASON",
            "RELEASE_EVIDENCE_ABSENT",
            "WORLD_UNAVAILABLE",
            reason,
        ]
        literal = next(
            notice for notice in notices if notice["properties"]["reasonCode"] == "LITERAL_REASON"
        )
        assert literal["message"]["text"] == "prod {{name}}: LITERAL_REASON"
        assert literal["level"] == "error"
        assert "markdown" not in literal["message"]
        assert run["properties"]["assessments"][0]["gapReasons"] == [
            "CHECK_RECEIPT_ABSENT",
            "LITERAL_REASON",
            "RELEASE_EVIDENCE_ABSENT",
            "WORLD_UNAVAILABLE",
        ]

    pending = pull_request([])
    pending["assessments"][0]["status"] = "PENDING"
    assert run_of(pending)["properties"]["assessments"][0]["gapReasons"] == [
        "ASSESSMENT_RESULT_UNAVAILABLE"
    ]
    stopped = pull_request([])
    stopped["assessments"][0]["status"] = "STOPPED"
    assert run_of(stopped)["properties"]["assessments"][0]["gapReasons"] == [
        "UNKNOWN_ASSESSMENT_STATUS"
    ]

    unresolved = pull_request([recorded])
    unresolved["assessments"][0]["checks"] = {
        "families": [
            {"name": "migrations", "outcome": "UNRESOLVED", "lifecycle": "GATING", "files": []}
        ],
        "receipt_recorded": True,
        "status": "READY",
    }
    run = run_of(unresolved)
    assert run["properties"]["assessments"][0]["gapReasons"] == ["CHECKS_UNRESOLVED"]
    assert run["properties"]["outcome"] == "INCOMPLETE"

    missing = pull_request([])
    missing["assessment_count"] = 2
    empty = pull_request([], assessment_count=0, assessments=[])
    for document in (missing, empty):
        run = run_of(document)
        assert run["invocations"][0]["executionSuccessful"] is False
        assert notice_codes(run)[0] == "REVIEW_RESULT_INCOMPLETE"
    assert notice_codes(run_of(empty))[1] == "CODE_ASSESSMENT_UNAVAILABLE"
    assert len(run_of(missing)["invocations"][0]["toolExecutionNotifications"]) == 1


def test_refuses_unpinned_or_unrecognized_records_without_a_document() -> None:
    wrong = pull_request([])
    with pytest.raises(SarifExportError, match="server returned review"):
        project(wrong, review_id=UUID("00000000-0000-4000-8000-000000000004"))
    for head in (None, "main", f" {HEAD}"):
        with pytest.raises(SarifExportError, match="full commit SHA"):
            project(pull_request([], head_commit_sha=head))
    with pytest.raises(SarifExportError, match="retained pull-request review"):
        project(pull_request([], kind="DEPLOYMENT"))
    with pytest.raises(SarifExportError, match="unsupported severity"):
        project(pull_request([finding(1, "CRITICAL")]))
    injected = finding(1, "BAD\x1b[2J", claim=CANARY)
    with pytest.raises(SarifExportError, match="unsupported severity") as raised:
        project(pull_request([injected]))
    assert "\x1b" not in str(raised.value)
    assert CANARY not in str(raised.value)
    assert "BAD\ufffd[2J" in str(raised.value)
    with pytest.raises(SarifExportError, match="unsupported risk domain"):
        project(pull_request([finding(1, risk_domain="unrecognized_domain")]))
    code = {
        "id": "00000000-0000-4000-8000-000000000006",
        "status": "COMPLETED",
        "base_commit_sha": BASE,
        "head_commit_sha": HEAD,
        "findings": [finding(1, risk_domain="unrecognized_domain")],
    }
    with pytest.raises(SarifExportError, match="unsupported risk domain"):
        project(
            pull_request(
                [], assessment_count=0, assessments=[], base_commit_sha=BASE, code_assessment=code
            )
        )


def test_caller_arguments_are_rejected_before_a_document_is_built() -> None:
    parsed = CustomerReviewDetail.from_dict(pull_request([]))
    with pytest.raises(TypeError):
        review_sarif(parsed, "org", review_id=REVIEW, review_url=URL)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        review_sarif(parsed, ORG, review_id=REVIEW, review_url="")


def test_get_review_projects_the_parsed_record() -> None:
    document = pull_request([finding(1, "SERIOUS", [code_ref("src/orders.rs", 8, 9)])])

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "GET"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert request.path.split("?", 1)[0] == f"/api/v1/organizations/{ORG}/reviews/{REVIEW}"
        return Reply(body=document)

    with Server(respond) as server:
        with ProoflineClient(TOKEN, base_url=server.url) as client:
            parsed = client.get_review(ORG, REVIEW)
    report = review_sarif(parsed, ORG, review_id=REVIEW, review_url=URL)
    result = report["runs"][0]["results"][0]
    assert result["level"] == "error"
    assert result["locations"][0]["physicalLocation"]["region"] == {"startLine": 8, "endLine": 9}
    assert CANARY not in json.dumps(report)
