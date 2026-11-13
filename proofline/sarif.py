"""Closed SARIF 2.1.0 projection of one retained pull-request review.

This matches the CLI's `findings --sarif` projection. It keeps finding identity,
severity, and verified locations at the reviewed head. It does not copy World
evidence values or the raw API document.
"""

from __future__ import annotations

import unicodedata
from typing import Any
from uuid import UUID

from ._generated.models.customer_assessment import CustomerAssessment
from ._generated.models.customer_check import CustomerCheck
from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_evidence_ref import CustomerEvidenceRef
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.types import Unset
from ._transport import VERSION

_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)
# domains-v5, the public environment catalog.
_DOMAINS: tuple[str, ...] = (
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
# code-categories-v2, the deterministic CODE categories, and committed_secret,
# which recorded findings still carry.
_CODE_DOMAINS: tuple[str, ...] = (
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
)
_COMPLETE_CHECKS = frozenset(("READY", "BLOCKED", "NOT_APPLICABLE"))
_COMPLETE_LIFECYCLES = frozenset(("GATING", "SHADOW", "QUARANTINED", "RETIRED"))
_KNOWN_ASSESSMENTS = frozenset(("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "FAILED"))
_WITHHELD_MARKER = "[withheld: environment value]"
_HEX = frozenset("0123456789abcdefABCDEF")
_FORBIDDEN_PATH_CHARACTERS = frozenset(
    "\\:\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
)
_URI_HEX = "0123456789ABCDEF"


class SarifExportError(Exception):
    """The review cannot be projected to SARIF."""


class _Location:
    def __init__(
        self, status: str, path: str | None = None, start: int | None = None, end: int | None = None
    ) -> None:
        self.status = status
        self.path = path
        self.start = start
        self.end = end


def review_sarif(
    review: CustomerReviewDetail,
    organization_id: UUID,
    *,
    review_id: UUID,
    review_url: str,
) -> dict[str, Any]:
    """Project one retained pull-request review to a SARIF 2.1.0 document.

    ``review_id`` is the review the caller requested. A different record is
    refused, as are a non-pull-request subject, a head that is not a full
    commit SHA, an unrecognized severity, and an unrecognized risk domain.
    An incomplete or unfinished review is still projected: its invocation is
    unsuccessful and names each gap. ``SUPERSEDED`` is an incomplete result,
    matching the CLI projection.
    """

    if not isinstance(review, CustomerReviewDetail):
        raise TypeError("review must be a CustomerReviewDetail.")
    if not isinstance(organization_id, UUID) or not isinstance(review_id, UUID):
        raise TypeError("organization_id and review_id must be UUIDs.")
    if not isinstance(review_url, str) or not review_url:
        raise ValueError("review_url must be the review's address.")
    if not isinstance(review.id, UUID):
        raise _invalid()
    if review.id != review_id:
        raise SarifExportError(
            f"requested review {review_id}, but the server returned review {review.id}; "
            "SARIF export refused"
        )
    if not isinstance(review.kind, str):
        raise _invalid()
    if review.kind != "PULL_REQUEST":
        raise SarifExportError(
            f"review {review.id} has kind {_one_line(review.kind)}; "
            "SARIF export requires a retained pull-request review"
        )
    head = _recorded_text(review.head_commit_sha)
    if head is None or not _hex_sha(head):
        raise SarifExportError(
            f"review {review.id} does not record a full commit SHA; "
            "SARIF export requires an immutable pull-request head"
        )
    if not isinstance(review.status, str):
        raise _invalid()
    head = head.lower()
    if type(review.assessment_count) is not int or not isinstance(review.assessments, list):
        raise _invalid()
    state = _terminal(review)
    code = _usable_code(review)
    results: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []
    code_properties: dict[str, Any] | None = None
    if code is not None:
        if not isinstance(code.id, UUID):
            raise _invalid()
        for finding in code.findings:
            results.append(_finding_result(finding, code, head, code=True))
        reason = _code_gap(code)
        reasons = [reason] if reason is not None else []
        for item in reasons:
            notifications.append(_notification(f"Code-only: {item}", item, code.id))
        code_properties = {
            "id": str(code.id),
            "status": _plain_text(code.status),
            "baseCommitSha": code.base_commit_sha,
            "headCommitSha": code.head_commit_sha,
            "gapReasons": reasons,
        }
    assessments: list[dict[str, Any]] = []
    for assessment in review.assessments:
        if not isinstance(assessment, CustomerAssessment):
            raise _invalid()
        if not isinstance(assessment.id, UUID) or not isinstance(
            assessment.environment_display_name, str
        ):
            raise _invalid()
        if not isinstance(assessment.status, str):
            raise _invalid()
        for finding in assessment.findings:
            results.append(_finding_result(finding, assessment, head, code=False))
        reasons = _assessment_gap_reasons(assessment)
        for reason in reasons:
            notifications.append(
                _notification(
                    f"{assessment.environment_display_name}: {reason}", reason, assessment.id
                )
            )
        assessments.append(
            {
                "id": str(assessment.id),
                "environment": assessment.environment_display_name,
                "status": assessment.status,
                "gapReasons": reasons,
            }
        )
    if state != "COMPLETED":
        reason = _review_reason(state)
        notifications.append(_notification(f"Review {review.id}: {reason}", reason, None))
    if _code_unavailable(review):
        notifications.append(
            _notification(
                "Code-only: CODE_ASSESSMENT_UNAVAILABLE", "CODE_ASSESSMENT_UNAVAILABLE", None
            )
        )
    rules = [{"id": domain} for domain in _DOMAINS]
    if code is not None:
        rules.extend({"id": domain} for domain in _CODE_DOMAINS)
    properties: dict[str, Any] = {
        "reviewId": str(review.id),
        "organizationId": str(organization_id),
        "reviewUrl": review_url,
        "headCommitSha": head,
        "repository": _recorded_text(review.repository_full_name),
        "pullRequestNumber": _recorded_int(review.pull_request_number),
        "runNumber": _recorded_int(review.run_number),
        "reviewStatus": review.status,
        "outcome": state,
        "assessmentCount": review.assessment_count,
        "assessments": assessments,
    }
    if code_properties is not None:
        properties["codeAssessment"] = code_properties
    return {
        "$schema": _SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {"name": "Proofline", "version": VERSION, "rules": rules},
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


def _notification(message: str, reason: str, assessment_id: UUID | None) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    if assessment_id is not None:
        properties["assessmentId"] = str(assessment_id)
    properties["reasonCode"] = reason
    return {
        "level": "error",
        "message": {"text": _sarif_text(message)},
        "properties": properties,
    }


def _finding_result(
    finding: CustomerFinding,
    source: CustomerAssessment | CustomerCodeAssessment,
    head: str,
    *,
    code: bool,
) -> dict[str, Any]:
    if not isinstance(finding, CustomerFinding) or not isinstance(finding.id, UUID):
        raise _invalid()
    if not isinstance(finding.severity, str) or not isinstance(finding.risk_domain, str):
        raise _invalid()
    if not isinstance(finding.claim, str) or not isinstance(finding.impact, str):
        raise _invalid()
    if not isinstance(finding.lifecycle_state, str) or not isinstance(finding.evidence_refs, list):
        raise _invalid()
    if finding.severity == "SERIOUS":
        level = "error"
    elif finding.severity == "WARNING":
        level = "warning"
    else:
        raise SarifExportError(
            f"finding {finding.id} has unsupported severity {_one_line(finding.severity)}; "
            "SARIF export refused"
        )
    domains = _CODE_DOMAINS if code else _DOMAINS
    try:
        domain_index = domains.index(finding.risk_domain)
    except ValueError:
        raise SarifExportError(
            f"finding {finding.id} has unsupported risk domain {_one_line(finding.risk_domain)}; "
            "SARIF export refused"
        ) from None
    locations: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int]] = set()
    evidence: list[dict[str, Any]] = []
    for reference in finding.evidence_refs:
        if not isinstance(reference, CustomerEvidenceRef):
            raise _invalid()
        located = _code_location(reference, head)
        if (
            located.status == "LOCATED"
            and located.path is not None
            and located.start is not None
            and located.end is not None
            and (located.path, located.start, located.end) not in seen
        ):
            seen.add((located.path, located.start, located.end))
            locations.append(
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": _path_uri(located.path),
                            "uriBaseId": "%SRCROOT%",
                        },
                        "region": {"startLine": located.start, "endLine": located.end},
                    }
                }
            )
        evidence.append(_evidence_properties(reference, located.status))
    message = f"{finding.claim}\n\n{finding.impact}"
    if code:
        message = f"Code-only finding\n\n{message}"
    result: dict[str, Any] = {
        "ruleId": domains[domain_index],
        "ruleIndex": (len(_DOMAINS) if code else 0) + domain_index,
        "level": level,
        "message": {"text": _sarif_text(message)},
        "locations": locations,
    }
    fingerprint = _recorded_text(finding.finding_fingerprint)
    if fingerprint is not None:
        result["partialFingerprints"] = {"prooflineFinding/v1": fingerprint}
    if len(locations) > 1:
        result["relatedLocations"] = locations[1:]
        result["locations"] = locations[:1]
    environment = (
        source.environment_display_name if isinstance(source, CustomerAssessment) else None
    )
    properties: dict[str, Any] = {
        "findingId": str(finding.id),
        "assessmentId": str(source.id),
        "lane": "CODE" if code else "ENV",
    }
    if environment is not None:
        properties["environment"] = environment
    properties["lifecycleState"] = finding.lifecycle_state
    properties["locationStatus"] = "LOCATED" if locations else "NO_VERIFIED_REVIEWED_LOCATION"
    remediation = _recorded_text(finding.remediation)
    if remediation is not None:
        properties["remediation"] = remediation
    properties["evidenceReferences"] = evidence
    result["properties"] = properties
    return result


def _evidence_properties(reference: CustomerEvidenceRef, status: str) -> dict[str, Any]:
    return {
        "kind": reference.kind,
        "provenanceStatus": reference.provenance_status
        if isinstance(reference.provenance_status, str)
        else None,
        "commitSha": _recorded_text(reference.commit_sha),
        "companionRepository": _recorded_text(reference.companion_repository),
        "repositoryPath": _recorded_text(reference.repository_path),
        "startLine": reference.start_line if type(reference.start_line) is int else None,
        "endLine": reference.end_line if type(reference.end_line) is int else None,
        "locationStatus": status,
    }


def _code_location(reference: CustomerEvidenceRef, head: str) -> _Location:
    if not isinstance(reference.kind, str) or not isinstance(reference.provenance_status, str):
        raise _invalid()
    if (
        reference.kind == "companion_repository_file"
        or _recorded_text(reference.companion_repository) is not None
    ):
        return _Location("COMPANION_REPOSITORY")
    if reference.kind != "repository_file":
        return _Location("NON_CODE_REFERENCE")
    if reference.provenance_status != "VERIFIED_REPOSITORY_READ":
        return _Location("UNVERIFIED_PROVENANCE")
    commit = _recorded_text(reference.commit_sha)
    if commit is None:
        return _Location("COMMIT_UNAVAILABLE")
    if not _hex_sha(commit):
        return _Location("INVALID_COMMIT")
    if commit.lower() != head.lower():
        return _Location("DIFFERENT_COMMIT")
    path = _recorded_text(reference.repository_path)
    if path is None or not _valid_path(path):
        return _Location("INVALID_PATH")
    start = reference.start_line
    if type(start) is not int or start <= 0:
        return _Location("INVALID_REGION")
    end = reference.end_line
    if isinstance(end, Unset) or end is None:
        end_line = start
    elif type(end) is not int or end < start:
        return _Location("INVALID_REGION")
    else:
        end_line = end
    return _Location("LOCATED", path, start, end_line)


def _assessment_gap_reasons(assessment: CustomerAssessment) -> list[str]:
    checks = assessment.checks
    if (
        not isinstance(checks.families, list)
        or type(checks.receipt_recorded) is not bool
        or not isinstance(checks.status, str)
    ):
        raise _invalid()
    check_gap = not checks.receipt_recorded or checks.status not in _COMPLETE_CHECKS
    for family in checks.families:
        if (
            not isinstance(family, CustomerCheck)
            or not isinstance(family.outcome, str)
            or not isinstance(family.lifecycle, str)
        ):
            raise _invalid()
        if family.outcome not in _COMPLETE_CHECKS or family.lifecycle not in _COMPLETE_LIFECYCLES:
            check_gap = True
    recorded = assessment.reason_codes
    if isinstance(recorded, Unset) or recorded is None:
        reasons: list[str] = []
    elif isinstance(recorded, list) and all(isinstance(reason, str) for reason in recorded):
        reasons = list(recorded)
    else:
        raise _invalid()
    kind = _recorded_text(assessment.incompleteness_kind)
    evidence = _recorded_text(assessment.release_evidence_gap)
    if (
        assessment.status == "COMPLETED"
        and not check_gap
        and not reasons
        and kind is None
        and evidence is None
    ):
        return []
    why = list(reasons)
    if kind is not None:
        why.append(kind)
    if evidence is not None:
        why.append(evidence)
    if check_gap:
        why.append("CHECK_RECEIPT_ABSENT" if not checks.receipt_recorded else "CHECKS_UNRESOLVED")
    if not why:
        why.append(
            "ASSESSMENT_RESULT_UNAVAILABLE"
            if assessment.status in _KNOWN_ASSESSMENTS
            else "UNKNOWN_ASSESSMENT_STATUS"
        )
    return sorted(set(why))


def _code_gap(code: CustomerCodeAssessment) -> str | None:
    kind = _recorded_text(code.incompleteness_kind)
    if kind:
        return kind
    if _plain_text(code.status) == "COMPLETED":
        return None
    return "CODE_ASSESSMENT_STATE_UNAVAILABLE"


def _usable_code(review: CustomerReviewDetail) -> CustomerCodeAssessment | None:
    code = review.code_assessment
    if not isinstance(code, CustomerCodeAssessment):
        return None
    if (
        not isinstance(code.head_commit_sha, str)
        or not isinstance(code.base_commit_sha, str)
        or not isinstance(code.findings, list)
    ):
        return None

    def same(recorded: object, actual: str) -> bool:
        text = _recorded_text(recorded)
        return text is None or text.lower() == actual.lower()

    if not same(review.head_commit_sha, code.head_commit_sha) or not same(
        review.base_commit_sha, code.base_commit_sha
    ):
        return None
    if any(
        isinstance(finding, CustomerFinding) and finding.risk_domain == _WITHHELD_MARKER
        for finding in code.findings
    ):
        return None
    return code


def _code_unavailable(review: CustomerReviewDetail) -> bool:
    if _usable_code(review) is not None:
        return False
    recorded = review.code_assessment
    if recorded is not None and not isinstance(recorded, Unset):
        return True
    return review.assessment_count == 0 and not review.assessments


def _terminal(review: CustomerReviewDetail) -> str | None:
    if not isinstance(review.status, str):
        raise _invalid()
    if review.status in ("PENDING", "RUNNING"):
        return None
    if review.status == "FAILED":
        return "FAILED"
    if review.status == "STOPPED":
        return "STOPPED"
    if review.status == "COMPLETED" and review.assessment_count == len(review.assessments):
        if not review.assessments:
            code = _usable_code(review)
            complete = code is not None and _code_gap(code) is None
        else:
            complete = all(
                not _assessment_gap_reasons(assessment) for assessment in review.assessments
            )
        return "COMPLETED" if complete else "INCOMPLETE"
    return "INCOMPLETE"


def _review_reason(state: str | None) -> str:
    if state is None:
        return "REVIEW_IN_PROGRESS"
    if state == "FAILED":
        return "REVIEW_FAILED"
    if state == "STOPPED":
        return "REVIEW_STOPPED"
    return "REVIEW_RESULT_INCOMPLETE"


def _recorded_text(value: object) -> str | None:
    if isinstance(value, Unset) or value is None:
        return None
    if isinstance(value, str):
        return value
    raise _invalid()


def _recorded_int(value: object) -> int | None:
    if isinstance(value, Unset) or value is None:
        return None
    if type(value) is int:
        return value
    raise _invalid()


def _plain_text(value: object) -> str:
    if isinstance(value, str):
        return str(value)
    raise _invalid()


def _hex_sha(value: str) -> bool:
    return len(value) in (40, 64) and all(character in _HEX for character in value)


def _valid_path(path: str) -> bool:
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    return not any(
        unicodedata.category(character) == "Cc" or character in _FORBIDDEN_PATH_CHARACTERS
        for character in path
    )


def _path_uri(path: str) -> str:
    encoded: list[str] = []
    for byte in path.encode("utf-8"):
        if byte in b"-._~/" or 48 <= byte <= 57 or 65 <= byte <= 90 or 97 <= byte <= 122:
            encoded.append(chr(byte))
        else:
            encoded.append(f"%{_URI_HEX[byte >> 4]}{_URI_HEX[byte & 15]}")
    return "".join(encoded)


def _sarif_text(raw: str) -> str:
    # SARIF message text interprets braces and embedded links. Escape once.
    text: list[str] = []
    for character in raw:
        if character == "{":
            text.append("{{")
        elif character == "}":
            text.append("}}")
        elif character in "\\[]":
            text.append("\\")
            text.append(character)
        else:
            text.append(character)
    return "".join(text)


def _one_line(value: str) -> str:
    cleaned = "".join(
        character if character in "\n\t" or unicodedata.category(character) != "Cc" else "\ufffd"
        for character in value
    )
    return cleaned.replace("\n", " ").replace("\t", " ")


def _invalid() -> SarifExportError:
    return SarifExportError("The review has invalid identity or finding metadata.")
