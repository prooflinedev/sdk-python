"""Fix context and pushed-head verification. Tool refusals retain isError."""

from __future__ import annotations

from typing import Any

from ._mcp import AsyncMcpTools, KnowledgeResult, McpTools


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
