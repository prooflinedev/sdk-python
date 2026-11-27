"""Setup reads and configuration changes through the scoped MCP server.

A proposal applies nothing; an ordinary change applies only through apply_change,
and a sensitive one only through browser approval. Tool refusals retain isError.
"""

from __future__ import annotations

import os
import time
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict
from uuid import UUID

from ._mcp import AsyncMcpTools, KnowledgeResult, McpTools


class CitedFile(TypedDict):
    """A repository file, read at a full commit SHA, behind an inferred value."""

    repository_id: str
    commit_sha: str
    path: str


def new_request_id() -> str:
    """Return a fresh time-ordered UUID (version 7) for one propose_change call."""
    value = (time.time_ns() // 1_000_000 & (1 << 48) - 1) << 80
    value |= int.from_bytes(os.urandom(10), "big")
    value = value & ~(0xF << 76) | 0x7 << 76
    value = value & ~(0x3 << 62) | 0x2 << 62
    return str(UUID(int=value))


def _optional(**values: Any) -> dict[str, Any]:
    return {name: value for name, value in values.items() if value is not None}


def _describe(operation: str, parameters: Mapping[str, str] | None) -> dict[str, Any]:
    return {"operation": operation, "parameters": dict(parameters or {})}


def _proposal(
    operation: str,
    parameters: Mapping[str, str] | None,
    input: Any,
    expected_revision: str | None,
    cited_files: Sequence[CitedFile] | None,
    request_id: str | None,
) -> dict[str, Any]:
    args: dict[str, Any] = {"operation": operation, "parameters": dict(parameters or {})}
    if input is not None:
        args["input"] = input
    if expected_revision is not None:
        args["expected_revision"] = expected_revision
    if cited_files is not None:
        args["cited_files"] = [dict(cited) for cited in cited_files]
    args["request_id"] = new_request_id() if request_id is None else request_id
    return args


class ConfigurationClient(McpTools):
    def get_configuration(
        self,
        *,
        environment_id: str | None = None,
        repository: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return self._call(
            "get_configuration",
            _optional(environment_id=environment_id, repository=repository),
            organization_id=organization_id,
        )

    def list_operations(
        self,
        *,
        area: str | None = None,
        subject: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return self._call(
            "list_operations",
            _optional(area=area, subject=subject),
            organization_id=organization_id,
        )

    def describe_operation(
        self,
        operation: str,
        parameters: Mapping[str, str] | None = None,
        *,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return self._call(
            "describe_operation",
            _describe(operation, parameters),
            organization_id=organization_id,
        )

    def propose_change(
        self,
        operation: str,
        *,
        parameters: Mapping[str, str] | None = None,
        input: Any = None,
        expected_revision: str | None = None,
        cited_files: Sequence[CitedFile] | None = None,
        request_id: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return self._call(
            "propose_change",
            _proposal(operation, parameters, input, expected_revision, cited_files, request_id),
            organization_id=organization_id,
        )

    def apply_change(
        self, change_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return self._call("apply_change", {"change_id": change_id}, organization_id=organization_id)


class AsyncConfigurationClient(AsyncMcpTools):
    async def get_configuration(
        self,
        *,
        environment_id: str | None = None,
        repository: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return await self._call(
            "get_configuration",
            _optional(environment_id=environment_id, repository=repository),
            organization_id=organization_id,
        )

    async def list_operations(
        self,
        *,
        area: str | None = None,
        subject: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return await self._call(
            "list_operations",
            _optional(area=area, subject=subject),
            organization_id=organization_id,
        )

    async def describe_operation(
        self,
        operation: str,
        parameters: Mapping[str, str] | None = None,
        *,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return await self._call(
            "describe_operation",
            _describe(operation, parameters),
            organization_id=organization_id,
        )

    async def propose_change(
        self,
        operation: str,
        *,
        parameters: Mapping[str, str] | None = None,
        input: Any = None,
        expected_revision: str | None = None,
        cited_files: Sequence[CitedFile] | None = None,
        request_id: str | None = None,
        organization_id: str | None = None,
    ) -> KnowledgeResult:
        return await self._call(
            "propose_change",
            _proposal(operation, parameters, input, expected_revision, cited_files, request_id),
            organization_id=organization_id,
        )

    async def apply_change(
        self, change_id: str, *, organization_id: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "apply_change", {"change_id": change_id}, organization_id=organization_id
        )


class SetupClient(McpTools):
    def get_setup_status(self, *, organization_id: str | None = None) -> KnowledgeResult:
        return self._call("get_setup_status", {}, organization_id=organization_id)

    def list_setup_candidates(
        self, *, query: str | None = None, organization_id: str | None = None
    ) -> KnowledgeResult:
        return self._call(
            "list_setup_candidates", _optional(query=query), organization_id=organization_id
        )


class AsyncSetupClient(AsyncMcpTools):
    async def get_setup_status(self, *, organization_id: str | None = None) -> KnowledgeResult:
        return await self._call("get_setup_status", {}, organization_id=organization_id)

    async def list_setup_candidates(
        self, *, query: str | None = None, organization_id: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "list_setup_candidates", _optional(query=query), organization_id=organization_id
        )
