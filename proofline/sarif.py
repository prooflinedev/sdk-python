"""Export a retained pull-request review outcome to SARIF 2.1.0 format."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote
from uuid import UUID

from ._generated.models.customer_assessment_detail import CustomerAssessmentDetail
from ._generated.models.customer_code_assessment import CustomerCodeAssessment
from ._generated.models.customer_evidence_ref import CustomerEvidenceRef
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.types import Unset
from ._transport import VERSION, ProoflineError
from .outcomes import ReviewOutcome

SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)

# The public environment risk-domain catalog, in the CLI's rule order.
DOMAINS = (
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

# The CODE categories, listed after the environment domains when a usable CODE record exists.
CODE_DOMAINS = (
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
    "maintainability",
    "test_marker",
    "removed_assertion",
    "debug_residue",
    "committed_secret",
)

_COMMIT_REGEX = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.IGNORECASE)
_UINT32_MAX = 0xFFFF_FFFF
_WITHHELD_MARKER = "[withheld: environment value]"


def _refused(detail: str) -> ProoflineError:
    return ProoflineError(0, "urn:proofline:sdk:sarif-refused", detail)


def _control(code: int) -> bool:
    return code < 0x20 or (0x7F <= code <= 0x9F)


def _one_line(value: object) -> str:
    text = ""
    for char in str(value):
        code = ord(char)
        if char in ("\n", "\t"):
            text += " "
        elif _control(code):
            text += "\ufffd"
        else:
            text += char
    return text


def _literal(raw: str) -> dict[str, str]:
    escaped = ""
    for char in raw:
        if char == "{":
            escaped += "{{"
        elif char == "}":
            escaped += "}}"
        elif char in ("\\", "[", "]"):
            escaped += f"\\{char}"
        else:
            escaped += char
    return {"text": escaped}


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and not isinstance(value, Unset) else None


def _line(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= _UINT32_MAX:
        return value
    return None


def _valid_path(path: str) -> bool:
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    for char in path:
        code = ord(char)
        if (
            _control(code)
            or char in ("\\", ":")
            or code in (0x200E, 0x200F)
            or (0x202A <= code <= 0x202E)
            or (0x2066 <= code <= 0x2069)
        ):
            return False
    return True


def _path_uri(path: str) -> str:
    return quote(path, safe="A-Za-z0-9-._~/")


def _code_location(
    reference: CustomerEvidenceRef, head: str
) -> str | dict[str, Any]:
    comp_repo = getattr(reference, "companion_repository", None)
    if reference.kind == "companion_repository_file" or (
        comp_repo is not None and not isinstance(comp_repo, Unset)
    ):
        return "COMPANION_REPOSITORY"
    if reference.kind != "repository_file":
        return "NON_CODE_REFERENCE"
    if reference.provenance_status != "VERIFIED_REPOSITORY_READ":
        return "UNVERIFIED_PROVENANCE"

    commit = _text(getattr(reference, "commit_sha", None))
    if commit is None:
        return "COMMIT_UNAVAILABLE"
    if not _COMMIT_REGEX.match(commit):
        return "INVALID_COMMIT"
    if commit.lower() != head:
        return "DIFFERENT_COMMIT"

    path = _text(getattr(reference, "repository_path", None))
    if path is None or not _valid_path(path):
        return "INVALID_PATH"

    start = _line(getattr(reference, "start_line", None))
    if start is None or start == 0:
        return "INVALID_REGION"

    end_val = getattr(reference, "end_line", None)
    end = start if end_val is None or isinstance(end_val, Unset) else _line(end_val)
    if end is None or end < start:
        return "INVALID_REGION"

    return {"path": path, "start": start, "end": end}


def _finding_result(
    finding: CustomerFinding,
    source: dict[str, str | None],
    head: str,
) -> dict[str, Any]:
    finding_id = getattr(finding, "id", None)
    claim = getattr(finding, "claim", None)
    impact = getattr(finding, "impact", None)
    lifecycle_state = getattr(finding, "lifecycle_state", None)
    evidence_refs = getattr(finding, "evidence_refs", None)

    if (
        not isinstance(finding_id, (str, UUID))
        or not isinstance(claim, str)
        or not isinstance(impact, str)
        or not isinstance(lifecycle_state, str)
        or not isinstance(evidence_refs, list)
    ):
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-response",
            "a finding has no typed identity, text or evidence",
        )

    severity = getattr(finding, "severity", None)
    if severity == "SERIOUS":
        level = "error"
    elif severity == "WARNING":
        level = "warning"
    else:
        raise _refused(
            f"finding {_one_line(finding_id)} has unsupported severity {_one_line(severity)}; "
            "SARIF export refused"
        )

    code = source["environment"] is None
    domains = CODE_DOMAINS if code else DOMAINS
    risk_domain = getattr(finding, "risk_domain", None)
    if not isinstance(risk_domain, str) or risk_domain not in domains:
        raise _refused(
            f"finding {_one_line(finding_id)} has unsupported risk domain {_one_line(risk_domain)}; "
            "SARIF export refused"
        )

    domain_index = domains.index(risk_domain)
    rule_index = (len(DOMAINS) if code else 0) + domain_index

    locations: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int]] = set()
    evidence_references: list[dict[str, Any]] = []

    for reference in evidence_refs:
        located = _code_location(reference, head)
        if isinstance(located, dict):
            key = (located["path"], located["start"], located["end"])
            if key not in seen:
                seen.add(key)
                locations.append({
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": _path_uri(located["path"]),
                            "uriBaseId": "%SRCROOT%",
                        },
                        "region": {"startLine": located["start"], "endLine": located["end"]},
                    }
                })
        evidence_references.append({
            "kind": str(getattr(reference, "kind", "")),
            "provenanceStatus": _text(getattr(reference, "provenance_status", None)),
            "commitSha": _text(getattr(reference, "commit_sha", None)),
            "companionRepository": _text(getattr(reference, "companion_repository", None)),
            "repositoryPath": _text(getattr(reference, "repository_path", None)),
            "startLine": _line(getattr(reference, "start_line", None)),
            "endLine": _line(getattr(reference, "end_line", None)),
            "locationStatus": "LOCATED" if isinstance(located, dict) else located,
        })

    primary_locations = locations[:1]
    related = locations[1:]
    remediation = _text(getattr(finding, "remediation", None))
    fingerprint = _text(getattr(finding, "finding_fingerprint", None))

    props: dict[str, Any] = {
        "findingId": str(finding_id),
        "assessmentId": str(source["assessmentId"]),
        "lane": "CODE" if code else "ENV",
        "lifecycleState": str(lifecycle_state),
        "locationStatus": "LOCATED" if primary_locations else "NO_VERIFIED_REVIEWED_LOCATION",
        "evidenceReferences": evidence_references,
    }
    if source["environment"] is not None:
        props["environment"] = source["environment"]
    if remediation is not None:
        props["remediation"] = remediation

    prefix = "Code-only finding\n\n" if code else ""
    msg = f"{prefix}{claim}\n\n{impact}"

    result: dict[str, Any] = {
        "ruleId": risk_domain,
        "ruleIndex": rule_index,
        "level": level,
        "message": _literal(msg),
        "locations": primary_locations,
        "properties": props,
    }
    if fingerprint is not None:
        result["partialFingerprints"] = {"prooflineFinding/v1": fingerprint}
    if related:
        result["relatedLocations"] = related

    return result


def _recorded_code(review: CustomerReviewDetail) -> CustomerCodeAssessment | None:
    code = getattr(review, "code_assessment", None)
    if code is None or isinstance(code, Unset):
        return None
    if (
        not isinstance(getattr(code, "id", None), (str, UUID))
        or not _text(getattr(code, "base_commit_sha", None))
        or not _text(getattr(code, "head_commit_sha", None))
        or not isinstance(getattr(code, "findings", None), list)
        or getattr(code, "status", None)
        not in ("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "EXCLUDED")
    ):
        return None
    kind = getattr(code, "incompleteness_kind", None)
    if kind is not None and not isinstance(kind, (str, Unset)):
        return None

    review_head = _text(getattr(review, "head_commit_sha", None))
    review_base = _text(getattr(review, "base_commit_sha", None))
    code_head = _text(getattr(code, "head_commit_sha", None))
    code_base = _text(getattr(code, "base_commit_sha", None))

    if review_head and code_head and review_head.lower() != code_head.lower():
        return None
    if review_base and code_base and review_base.lower() != code_base.lower():
        return None

    findings = getattr(code, "findings", [])
    if any(getattr(f, "risk_domain", None) == _WITHHELD_MARKER for f in findings):
        return None

    return code


def _code_gap(code: CustomerCodeAssessment) -> str | None:
    kind = getattr(code, "incompleteness_kind", None)
    if kind is not None and not isinstance(kind, Unset):
        return str(kind)
    return None if getattr(code, "status", None) == "COMPLETED" else "CODE_ASSESSMENT_STATE_UNAVAILABLE"


def review_sarif(outcome: ReviewOutcome, organization_id: str | UUID) -> dict[str, Any]:
    """Project a retained pull-request ReviewOutcome to SARIF 2.1.0."""
    if not isinstance(organization_id, (str, UUID)) or not str(organization_id):
        raise TypeError("organizationId must be a nonempty string")
    org_id_str = str(organization_id)

    review = outcome.review
    if review is None:
        raise TypeError("the outcome retains no review to export")

    kind = getattr(review, "kind", None)
    if kind not in ("PULL_REQUEST", "PR"):
        raise _refused(
            f"review {_one_line(review.id)} has kind {_one_line(kind)}; "
            "SARIF export requires a retained pull-request review"
        )

    head_commit = getattr(review, "head_commit_sha", None)
    if not isinstance(head_commit, str) or not _COMMIT_REGEX.match(head_commit):
        raise _refused(
            f"review {_one_line(review.id)} does not record a full commit SHA; "
            "SARIF export requires an immutable pull-request head"
        )
    head = head_commit.lower()

    code = _recorded_code(review)
    results: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []

    def notify(subject: str, reason_code: str, assessment_id: str | None = None) -> None:
        props: dict[str, Any] = {"reasonCode": reason_code}
        if assessment_id is not None:
            props["assessmentId"] = assessment_id
        notifications.append({
            "level": "error",
            "message": _literal(f"{subject}: {reason_code}"),
            "properties": props,
        })

    code_assessment_prop: dict[str, Any] | None = None
    if code is not None:
        code_findings = getattr(code, "findings", None)
        if not isinstance(code_findings, list):
            raise ProoflineError(
                0,
                "urn:proofline:sdk:invalid-response",
                "an assessment has no finding list",
            )
        for finding in code_findings:
            results.append(
                _finding_result(
                    finding,
                    {"assessmentId": str(code.id), "environment": None},
                    head,
                )
            )
        gap = _code_gap(code)
        if gap is not None:
            notify("Code-only", gap, str(code.id))
        code_assessment_prop = {
            "id": str(code.id),
            "status": str(code.status),
            "baseCommitSha": str(code.base_commit_sha),
            "headCommitSha": str(code.head_commit_sha),
            "gapReasons": [] if gap is None else [gap],
        }

    assessments_prop: list[dict[str, Any]] = []
    review_assessments = getattr(review, "assessments", [])
    if not isinstance(review_assessments, list):
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-response",
            "an assessment has no finding list",
        )
    for assessment in review_assessments:
        env_display = getattr(assessment, "environment_display_name", "")
        findings = getattr(assessment, "findings", None)
        if not isinstance(findings, list):
            raise ProoflineError(
                0,
                "urn:proofline:sdk:invalid-response",
                "an assessment has no finding list",
            )
        for finding in findings:
            results.append(
                _finding_result(
                    finding,
                    {"assessmentId": str(assessment.id), "environment": env_display},
                    head,
                )
            )

        gap_reasons = sorted({
            code
            for g in outcome.gaps
            if g.assessment_id is not None and str(g.assessment_id) == str(assessment.id)
            for code in g.reason_codes
        })
        for reason in gap_reasons:
            notify(env_display, reason, str(assessment.id))

        assessments_prop.append({
            "id": str(assessment.id),
            "environment": env_display,
            "status": str(assessment.status),
            "gapReasons": gap_reasons,
        })

    if outcome.status != "COMPLETED":
        status_map = {
            "TIMED_OUT": "REVIEW_IN_PROGRESS",
            "FAILED": "REVIEW_FAILED",
            "STOPPED": "REVIEW_STOPPED",
        }
        notify(f"Review {review.id}", status_map.get(outcome.status, "REVIEW_RESULT_INCOMPLETE"))

    if code is None and (
        getattr(review, "code_assessment", None) is not None
        or (getattr(review, "assessment_count", 0) == 0 and len(review_assessments) == 0)
    ):
        notify("Code-only", "CODE_ASSESSMENT_UNAVAILABLE")

    rules = [{"id": domain} for domain in DOMAINS]
    if code is not None:
        rules.extend({"id": domain} for domain in CODE_DOMAINS)

    repo_full_name = getattr(review, "repository_full_name", None)
    if isinstance(repo_full_name, Unset):
        repo_full_name = None
    pr_num = getattr(review, "pull_request_number", None)
    if isinstance(pr_num, Unset):
        pr_num = None
    run_num = getattr(review, "run_number", None)
    if isinstance(run_num, Unset):
        run_num = None

    run_properties: dict[str, Any] = {
        "reviewId": str(review.id),
        "organizationId": org_id_str,
        "reviewUrl": outcome.review_url,
        "headCommitSha": head,
        "repository": repo_full_name,
        "pullRequestNumber": pr_num,
        "runNumber": run_num,
        "reviewStatus": str(review.status),
        "outcome": None if outcome.status == "TIMED_OUT" else outcome.status,
        "assessmentCount": int(getattr(review, "assessment_count", 0)),
        "assessments": assessments_prop,
    }
    if code_assessment_prop is not None:
        run_properties["codeAssessment"] = code_assessment_prop

    return {
        "$schema": SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Proofline",
                        "version": VERSION,
                        "rules": rules,
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": outcome.status == "COMPLETED"
                        and len(notifications) == 0,
                        "toolExecutionNotifications": notifications,
                    }
                ],
                "results": results,
                "properties": run_properties,
            }
        ],
    }
