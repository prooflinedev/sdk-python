"""Fix context and pushed-head verification. Tool refusals retain isError."""

from __future__ import annotations

from typing import Any

from ._generated.models.local_reverification_outcome import LocalReverificationOutcome
from ._mcp import AsyncMcpTools, KnowledgeResult, McpTools

# The public contract's only in-progress re-verification value. The other
# LocalReverificationOutcome values are recorded results.
_PENDING = LocalReverificationOutcome.PENDING.value
_TERMINAL_OUTCOMES = frozenset(
    member.value for member in LocalReverificationOutcome if member.value != _PENDING
)


def _reverification_payload(result: KnowledgeResult) -> dict[str, Any]:
    content = result.get("structuredContent")
    if not isinstance(content, dict):
        return {}
    data = content.get("data")
    if content.get("ok") is True and isinstance(data, dict):
        return data
    return content


def _collect_finding_outcomes(value: object, found: list[str]) -> None:
    if isinstance(value, list):
        for item in value:
            _collect_finding_outcomes(item, found)
        return
    if not isinstance(value, dict):
        return
    if "finding_id" in value:
        outcome = value.get("outcome")
        # A listed finding with no outcome has not recorded a result yet.
        found.append(outcome if isinstance(outcome, str) else _PENDING)
    for child in value.values():
        _collect_finding_outcomes(child, found)


def _reverification_in_progress(result: KnowledgeResult) -> bool:
    """True while this get_reverification read is still running.

    LocalReverificationOutcome describes PENDING as the review still running,
    and RESOLVED_VERIFIED, STILL_PRESENT and NOT_VERIFIED as recorded results.
    A string outside that enum is not a recorded result. An isError result is
    not in progress; the caller returns it.
    """

    if result.get("isError"):
        return False
    payload = _reverification_payload(result)
    outcomes: list[str] = []
    if "finding_id" not in payload:
        outcome = payload.get("outcome")
        if isinstance(outcome, str):
            outcomes.append(outcome)
    _collect_finding_outcomes(payload, outcomes)
    if any(outcome not in _TERMINAL_OUTCOMES for outcome in outcomes):
        return True
    if payload.get("status") == _PENDING:
        return True
    if outcomes or isinstance(payload.get("status"), str):
        return False
    return True


class FixesClient(McpTools):
    def list_open_findings(
        self, repository: str, pull_request_number: int, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return self._call(
            "list_open_findings",
            {"repository": repository, "pull_request_number": pull_request_number},
            organization_id=organization_id,
        )

    def get_fix_context(
        self, finding_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return self._call(
            "get_fix_context", {"finding_id": finding_id}, organization_id=organization_id
        )

    def request_reverification(
        self,
        review_id: str,
        finding_ids: list[str],
        commit_sha: str,
        *,
        note: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        args: dict[str, Any] = {
            "review_id": review_id,
            "finding_ids": finding_ids,
            "commit_sha": commit_sha,
        }
        if note is not None:
            args["note"] = note
        return self._call("request_reverification", args, organization_id=organization_id)

    def get_reverification(
        self, request_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return self._call(
            "get_reverification", {"request_id": request_id}, organization_id=organization_id
        )


class AsyncFixesClient(AsyncMcpTools):
    async def list_open_findings(
        self, repository: str, pull_request_number: int, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "list_open_findings",
            {"repository": repository, "pull_request_number": pull_request_number},
            organization_id=organization_id,
        )

    async def get_fix_context(
        self, finding_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "get_fix_context", {"finding_id": finding_id}, organization_id=organization_id
        )

    async def request_reverification(
        self,
        review_id: str,
        finding_ids: list[str],
        commit_sha: str,
        *,
        note: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        args: dict[str, Any] = {
            "review_id": review_id,
            "finding_ids": finding_ids,
            "commit_sha": commit_sha,
        }
        if note is not None:
            args["note"] = note
        return await self._call("request_reverification", args, organization_id=organization_id)

    async def get_reverification(
        self, request_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "get_reverification", {"request_id": request_id}, organization_id=organization_id
        )
