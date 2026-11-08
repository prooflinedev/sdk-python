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


def agent_session(status: str = "RUNNING", *, done: bool = False) -> dict[str, Any]:
    return {
        "id": str(REVIEW),
        "finding_id": str(FINDING),
        "review_id": str(ASSESSMENT),
        "connection_id": str(REPOSITORY),
        "vendor": "CURSOR_CLOUD_AGENTS",
        "target": {
            "repository_id": str(REPOSITORY),
            "repository_full_name": "repo/name",
            "github_repository_id": 42,
            "pull_request_number": 7,
            "head_sha": "a" * 40,
        },
        "attempt": 1,
        "status": status,
        "done": done,
        "cause": None,
        "vendor_status": None,
        "vendor_url": "https://vendor.example/session",
        "pull_request_url": None,
        "observed_head_sha": None,
        "untrusted_vendor_summary": None,
        "requested_by_user_id": str(ORG),
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
