"""Synthetic wire fixtures use the required public-document fields."""

from __future__ import annotations

from typing import Any
from uuid import UUID

ORG = UUID("00000000-0000-4000-8000-000000000001")
REPOSITORY = UUID("00000000-0000-4000-8000-000000000002")
REVIEW = UUID("00000000-0000-4000-8000-000000000003")
ASSESSMENT = UUID("00000000-0000-4000-8000-000000000004")
CODE_ASSESSMENT = UUID("00000000-0000-4000-8000-000000000006")
FINDING = UUID("00000000-0000-4000-8000-000000000005")
TOKEN = "pln_test_sdk_credential_canary"
PRIVATE = "synthetic-finding-body-canary"
DEPLOY_ENVIRONMENT = UUID("00000000-0000-4000-8000-000000000007")
OTHER_DEPLOY_ENVIRONMENT = UUID("00000000-0000-4000-8000-000000000008")
DEPLOYMENT_REVIEW = UUID("00000000-0000-4000-8000-000000000009")
FAILED_COMMIT = "f" * 40
MIDDLE_COMMITS = ("e" * 40, "d" * 40)
HEALTHY_COMMIT = "c" * 40
CHECKPOINTS = ("LANDING", "MINUTES_20", "HOUR_1", "DAY_1")


def finding() -> dict[str, Any]:
    return {
        "id": str(FINDING),
        "severity": "HIGH",
        "risk_domain": "SECURITY",
        "claim": PRIVATE,
        "impact": "A synthetic consequence.",
        "symbols": [],
        "lifecycle_state": "OPEN",
        "evidence_refs": [],
        "rule_refs": [
            {
                "key": "no-sync-io-in-handlers",
                "revisions": [{"scope": "ORGANIZATION", "source": "CONSOLE", "revision": 1}],
            }
        ],
        "comment_reactions": [],
    }


def assessment(status: str = "COMPLETED") -> dict[str, Any]:
    return {
        "id": str(ASSESSMENT),
        "environment_display_name": "Synthetic environment",
        "status": status,
        "domains": [],
        "findings": [],
        "checks": {"families": [], "receipt_recorded": True, "status": "READY"},
    }


def code_assessment(status: str = "COMPLETED") -> dict[str, Any]:
    return {
        "id": str(CODE_ASSESSMENT),
        "status": status,
        "head_commit_sha": "a" * 40,
        "base_commit_sha": "b" * 40,
        "findings": [],
        "incompleteness_kind": None,
    }


def summary(status: str = "COMPLETED") -> dict[str, Any]:
    return {
        "id": str(REVIEW),
        "public_key": "synthetic-review",
        "kind": "PR",
        "status": status,
        "assessment_count": 1,
        "environment_display_names": ["Synthetic environment"],
        "finding_count": 0,
        "trigger_origin": "MANUAL",
        "publication": "WITHHELD",
        "created_at": "2026-01-01T00:00:00Z",
    }


def review(status: str = "COMPLETED") -> dict[str, Any]:
    return {
        **summary(status),
        "assessments": [assessment()],
        "stoppable": False,
        "related_reviews": [],
        "subjects": [],
        "actions": {
            "promote_findings": False,
            "publish": False,
            "rerun": False,
            "stop": False,
            "validate_findings": False,
        },
    }


def page(*, cursor: str | None = None, truncated: bool = False) -> dict[str, Any]:
    return {
        "items": [summary()],
        "filters": {"repositories": [], "environments": [], "authors": []},
        "truncated": truncated,
        "next_cursor": cursor,
    }


def deploy(
    state: str,
    *,
    regressed: bool = False,
    rolled_back: bool = False,
    environment: UUID = DEPLOY_ENVIRONMENT,
    task: str | None = "deploy",
    results: tuple[str | None, ...] = ("HEALTHY", "HEALTHY", "HEALTHY", "HEALTHY"),
) -> dict[str, Any]:
    return {
        "environment_id": str(environment),
        "state": state,
        "regressed": regressed,
        "rolled_back": rolled_back,
        "gaps": [],
        "checkpoints": [
            {"checkpoint": name, "due_at": "2026-11-01T00:00:00Z", "result": result, "gaps": []}
            for name, result in zip(CHECKPOINTS, results)
        ],
        "deployment_task": task,
        "github_environment": "synthetic-environment",
        "deploy_url": "https://proofline.example/deploys/synthetic",
    }


def verifications(*deploys: dict[str, Any]) -> dict[str, Any]:
    return {"recorded": bool(deploys), "deploys": list(deploys)}


def commit_page(*items: dict[str, Any], truncated: bool = False) -> dict[str, Any]:
    return {
        "items": list(items),
        "filters": {"repositories": [], "environments": [], "authors": []},
        "truncated": truncated,
        "next_cursor": "synthetic-cursor" if truncated else None,
    }
