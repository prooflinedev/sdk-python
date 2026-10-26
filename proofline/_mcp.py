"""Typed knowledge calls over Proofline's stateless MCP endpoint. No tool-call retries."""

from __future__ import annotations

import json
from typing import Any, NotRequired, TypedDict, cast

import httpx

from ._transport import ProoflineError

PROTOCOL = "2025-11-25"


class TextContent(TypedDict):
    type: str
    text: str


class KnowledgeResult(TypedDict):
    content: list[TextContent]
    structuredContent: NotRequired[dict[str, Any]]
    isError: NotRequired[bool]


def _refused() -> ProoflineError:
    return ProoflineError(0, "urn:proofline:sdk:mcp", "Invalid or refused MCP response.")


def _body(method: str, params: dict[str, Any] | None, identity: int | None) -> bytes:
    value: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if identity is not None:
        value["id"] = identity
    if params is not None:
        value["params"] = params
    data = json.dumps(value).encode("utf-8")
    if len(data) > 8192:
        raise ValueError("MCP request exceeds 8192 bytes.")
    return data


def _decode(response: httpx.Response, identity: int | None) -> dict[str, Any]:
    if (
        response.status_code != (202 if identity is None else 200)
        or "mcp-session-id" in response.headers
    ):
        raise _refused()
    if identity is None:
        if response.content:
            raise _refused()
        return {}
    if response.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise _refused()
    try:
        value = response.json()
    except ValueError:
        raise _refused() from None
    if (
        not isinstance(value, dict)
        or value.get("jsonrpc") != "2.0"
        or value.get("id") != identity
        or "error" in value
        or not isinstance(value.get("result"), dict)
    ):
        raise _refused()
    return cast(dict[str, Any], value["result"])


def _result(value: dict[str, Any]) -> KnowledgeResult:
    content = value.get("content")
    if not isinstance(content, list) or any(
        not isinstance(item, dict)
        or item.get("type") != "text"
        or not isinstance(item.get("text"), str)
        for item in content
    ):
        raise _refused()
    if "isError" in value and not isinstance(value["isError"], bool):
        raise _refused()
    if "structuredContent" in value and not isinstance(value["structuredContent"], dict):
        raise _refused()
    return cast(KnowledgeResult, value)


def _repository(repository: str, commit: str | None) -> dict[str, Any]:
    args = {"repository": repository}
    if commit is not None:
        args["commit"] = commit
    return args


class McpTools:
    """Knowledge operations preserve MCP result wrappers and isError refusals."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def _call(self, name: str, args: dict[str, Any]) -> KnowledgeResult:
        call = _body("tools/call", {"name": name, "arguments": args}, 2)
        frames = [
            (
                _body(
                    "initialize",
                    {
                        "protocolVersion": PROTOCOL,
                        "capabilities": {},
                        "clientInfo": {"name": "proofline-python", "version": "1"},
                    },
                    1,
                ),
                1,
            ),
            (_body("notifications/initialized", None, None), None),
            (call, 2),
        ]
        result: dict[str, Any] = {}
        for data, identity in frames:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Origin": str(self._http.base_url).rstrip("/"),
            }
            if identity != 1:
                headers["MCP-Protocol-Version"] = PROTOCOL
            try:
                response = self._http.post("/mcp", content=data, headers=headers)
            except httpx.HTTPError:
                raise ProoflineError(
                    0, "urn:proofline:sdk:transport", "MCP transport failed."
                ) from None
            result = _decode(response, identity)
            if identity == 1 and result.get("protocolVersion") != PROTOCOL:
                raise _refused()
        return _result(result)


class AsyncMcpTools:
    """Knowledge operations preserve MCP result wrappers and isError refusals."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def _call(self, name: str, args: dict[str, Any]) -> KnowledgeResult:
        call = _body("tools/call", {"name": name, "arguments": args}, 2)
        frames = [
            (
                _body(
                    "initialize",
                    {
                        "protocolVersion": PROTOCOL,
                        "capabilities": {},
                        "clientInfo": {"name": "proofline-python", "version": "1"},
                    },
                    1,
                ),
                1,
            ),
            (_body("notifications/initialized", None, None), None),
            (call, 2),
        ]
        result: dict[str, Any] = {}
        for data, identity in frames:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Origin": str(self._http.base_url).rstrip("/"),
            }
            if identity != 1:
                headers["MCP-Protocol-Version"] = PROTOCOL
            try:
                response = await self._http.post("/mcp", content=data, headers=headers)
            except httpx.HTTPError:
                raise ProoflineError(
                    0, "urn:proofline:sdk:transport", "MCP transport failed."
                ) from None
            result = _decode(response, identity)
            if identity == 1 and result.get("protocolVersion") != PROTOCOL:
                raise _refused()
        return _result(result)
