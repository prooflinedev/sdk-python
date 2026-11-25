"""Project a retained pull-request review into the Proofline CLI's SARIF format.

The projection follows https://github.com/prooflinedev/cli/blob/main/src/sarif.rs.
"""

from __future__ import annotations

import re
from typing import Any, TypeVar
from urllib.parse import quote
from uuid import UUID

from ._generated.models import CustomerEvidenceRef, CustomerFinding
from ._generated.types import Unset
from ._transport import VERSION
from .outcomes import ReviewOutcome, _code_assessment, _code_gap
from .outcomes import outcome as recorded_outcome

_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)
# Rule indexes follow the CLI's public domain catalogs.
_ENV_DOMAINS = (
    "artifact_identity",
    "deployment_workflow",
    "runtime_configuration",
    "network_reachability",
    "iam_permissions",
    "datastore_compatibility",
    "resource_capacity",
    "rollout_topology",
    "runtime_architecture",
    "environment_binding",
    "dependency_reachability",
    "data_integrity",
    "external_side_effects",
    "application_security",
    "scalability",
    "availability_resilience",
    "observability",
    "source_coverage",
)
_CODE_DOMAINS = (
    "logic",
    "edge_case",
    "error_handling",
    "state_transition",
    "concurrency",
    "resource_lifecycle",
    "credential_exposure",
    "authorization",
    "injection",
    "test_quality",
    "api_contract",
    "prompt_instruction",
    "doc_drift",
    "ci_workflow",
    "performance",
    "maintainability",
    "test_marker",
    "removed_assertion",
    "debug_residue",
    "committed_secret",
)
_FULL_SHA = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})")
_INVALID_PATH_CHAR = re.compile(r"[\x00-\x1f\x7f-\x9f\\:\u200e\u200f\u202a-\u202e\u2066-\u2069]")
_MESSAGE_ESCAPES = str.maketrans({"{": "{{", "}": "}}", "\\": "\\\\", "[": "\\[", "]": "\\]"})
_HEAD_GAPS = {"HEAD_COMMIT_MISMATCH", "HEAD_COMMIT_UNAVAILABLE"}
_LEVELS = {"SERIOUS": "error", "WARNING": "warning"}


T = TypeVar("T")


def _value(value: T | Unset) -> T | None:
    return None if isinstance(value, Unset) else value


def _location(ref: CustomerEvidenceRef, head: str) -> tuple[str, tuple[str, int, int] | None]:
    if ref.kind == "companion_repository_file" or isinstance(ref.companion_repository, str):
        return "COMPANION_REPOSITORY", None
    if ref.kind != "repository_file":
        return "NON_CODE_REFERENCE", None
    if ref.provenance_status != "VERIFIED_REPOSITORY_READ":
        return "UNVERIFIED_PROVENANCE", None
    commit = ref.commit_sha
    if not isinstance(commit, str):
        return "COMMIT_UNAVAILABLE", None
    if not _FULL_SHA.fullmatch(commit):
        return "INVALID_COMMIT", None
    if commit.lower() != head:
        return "DIFFERENT_COMMIT", None
    path = ref.repository_path
    if (
        not isinstance(path, str)
        or _INVALID_PATH_CHAR.search(path)
        or any(part in ("", ".", "..") for part in path.split("/"))
    ):
        return "INVALID_PATH", None
    start = ref.start_line
    if type(start) is not int:
        return "INVALID_REGION", None
    end = _value(ref.end_line)
    if end is None:
        end = start
    if type(end) is not int or not 1 <= start <= end <= 2**32 - 1:
        return "INVALID_REGION", None
    return "LOCATED", (path, start, end)


def _message(text: str) -> dict[str, str]:
    return {"text": text.translate(_MESSAGE_ESCAPES)}


def _finding_result(
    finding: CustomerFinding, assessment_id: UUID, environment: str | None, head: str
) -> dict[str, Any]:
    level = _LEVELS.get(finding.severity)
    if level is None:
        raise ValueError(f"Finding {finding.id} has an unsupported SARIF severity.")
    code = environment is None
    domains = _CODE_DOMAINS if code else _ENV_DOMAINS
    if finding.risk_domain not in domains:
        raise ValueError(f"Finding {finding.id} has an unsupported SARIF risk domain.")
    rule_index = domains.index(finding.risk_domain) + (len(_ENV_DOMAINS) if code else 0)
    locations = []
    seen = set()
    references = []
    for ref in finding.evidence_refs:
        status, location = _location(ref, head)
        references.append(
            {
                "kind": ref.kind,
                "provenanceStatus": ref.provenance_status,
                "commitSha": _value(ref.commit_sha),
                "companionRepository": _value(ref.companion_repository),
                "repositoryPath": _value(ref.repository_path),
                "startLine": _value(ref.start_line),
                "endLine": _value(ref.end_line),
                "locationStatus": status,
            }
        )
        if location is None or location in seen:
            continue
        seen.add(location)
        path, start, end = location
        locations.append(
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": quote(path, safe="/"), "uriBaseId": "%SRCROOT%"},
                    "region": {"startLine": start, "endLine": end},
                },
            }
        )

    properties = {
        "findingId": str(finding.id),
        "assessmentId": str(assessment_id),
        "lane": "CODE" if code else "ENV",
        "lifecycleState": finding.lifecycle_state,
        "locationStatus": "LOCATED" if locations else "NO_VERIFIED_REVIEWED_LOCATION",
        "evidenceReferences": references,
    }
    if environment is not None:
        properties["environment"] = environment
    if isinstance(finding.remediation, str):
        properties["remediation"] = finding.remediation

    message = f"{finding.claim}\n\n{finding.impact}"
    result = {
        "ruleId": finding.risk_domain,
        "ruleIndex": rule_index,
        "level": level,
        "message": _message(f"Code-only finding\n\n{message}" if code else message),
        "locations": locations[:1],
        "properties": properties,
    }
    if isinstance(finding.finding_fingerprint, str):
        result["partialFingerprints"] = {"prooflineFinding/v1": finding.finding_fingerprint}
    if len(locations) > 1:
        result["relatedLocations"] = locations[1:]
    return result


def _notification(subject: str, reason: str, assessment_id: UUID | None = None) -> dict[str, Any]:
    properties = {"reasonCode": reason}
    if assessment_id is not None:
        properties["assessmentId"] = str(assessment_id)
    return {
        "level": "error",
        "message": _message(f"{subject}: {reason}"),
        "properties": properties,
    }


def review_sarif(outcome: ReviewOutcome, organization_id: UUID | str) -> dict[str, Any]:
    """Export a retained pull-request review as a JSON-serializable SARIF 2.1.0 report.

    Raises ValueError if the outcome has no pull-request review with a full,
    matching head SHA, or a finding uses an unsupported severity or risk domain.
    """
    review = outcome.review
    if review is None or review.kind != "PULL_REQUEST":
        raise ValueError("SARIF export requires a retained pull-request review.")
    head = review.head_commit_sha
    if (
        not isinstance(head, str)
        or not _FULL_SHA.fullmatch(head)
        or any(_HEAD_GAPS.intersection(gap.reason_codes) for gap in outcome.gaps)
    ):
        raise ValueError("SARIF export requires a full SHA for the reviewed pull-request head.")
    head = head.lower()

    # Reuse the SDK's assessment checks even for outcomes constructed directly.
    recorded = recorded_outcome(review, outcome.review_url)
    checked = recorded or recorded_outcome(review, outcome.review_url, "TIMED_OUT")
    assert checked is not None
    state = recorded.status if recorded else None
    if outcome.status == "TIMED_OUT" and state == "COMPLETED":
        state = "INCOMPLETE"
    elif outcome.status not in ("COMPLETED", "TIMED_OUT"):
        state = outcome.status

    results: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []
    assessments: list[dict[str, Any]] = []
    rules: tuple[str, ...] = _ENV_DOMAINS
    properties: dict[str, Any] = {
        "reviewId": str(review.id),
        "organizationId": str(UUID(str(organization_id))),
        "reviewUrl": outcome.review_url,
        "headCommitSha": head,
        "repository": _value(review.repository_full_name),
        "pullRequestNumber": _value(review.pull_request_number),
        "runNumber": _value(review.run_number),
        "reviewStatus": review.status,
        "outcome": state,
        "assessmentCount": review.assessment_count,
        "assessments": assessments,
    }
    code = _code_assessment(review)
    if code is not None:
        rules = (*rules, *_CODE_DOMAINS)
        results.extend(_finding_result(finding, code.id, None, head) for finding in code.findings)
        gap = _code_gap(code)
        reasons = list(gap.reason_codes) if gap else []
        notifications.extend(_notification("Code-only", reason, code.id) for reason in reasons)
        properties["codeAssessment"] = {
            "id": str(code.id),
            "status": code.status,
            "baseCommitSha": code.base_commit_sha,
            "headCommitSha": code.head_commit_sha,
            "gapReasons": reasons,
        }

    for assessment in review.assessments:
        environment = assessment.environment_display_name
        results.extend(
            _finding_result(finding, assessment.id, environment, head)
            for finding in assessment.findings
        )
        reasons = sorted(
            {
                reason
                for gap in checked.gaps
                if gap.assessment_id == assessment.id
                for reason in gap.reason_codes
            }
        )
        notifications.extend(
            _notification(environment, reason, assessment.id) for reason in reasons
        )
        assessments.append(
            {
                "id": str(assessment.id),
                "environment": environment,
                "status": assessment.status,
                "gapReasons": reasons,
            }
        )

    if state != "COMPLETED":
        reason = {
            None: "REVIEW_IN_PROGRESS",
            "FAILED": "REVIEW_FAILED",
            "STOPPED": "REVIEW_STOPPED",
        }.get(state, "REVIEW_RESULT_INCOMPLETE")
        notifications.append(_notification(f"Review {review.id}", reason))
    if code is None and (
        _value(review.code_assessment) is not None
        or (review.assessment_count == 0 and not review.assessments)
    ):
        notifications.append(_notification("Code-only", "CODE_ASSESSMENT_UNAVAILABLE"))

    return {
        "$schema": _SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Proofline",
                        "version": VERSION,
                        "rules": [{"id": rule} for rule in rules],
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": state == "COMPLETED" and not notifications,
                        "toolExecutionNotifications": notifications,
                    }
                ],
                "results": results,
                "properties": properties,
            }
        ],
    }
