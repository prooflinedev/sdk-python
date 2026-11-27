from __future__ import annotations

import inspect
import json
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

import pytest
from pydantic import SecretStr

from proofline import (
    AsyncProoflineClient,
    CitedFile,
    ProoflineClient,
    ProoflineError,
    new_request_id,
)

from .fixtures import ORG, REPOSITORY, REVIEW, TOKEN
from .http_server import Reply, Request, Server

MODES = pytest.mark.parametrize("mode", ["sync", "async"])
CHANGE = "00000000-0000-7000-8000-000000000009"


@asynccontextmanager
async def session(mode: str, url: str) -> AsyncIterator[Any]:
    if mode == "sync":
        with ProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            yield client
    else:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url) as async_client:
            yield async_client


def tool_server(results: list[dict[str, Any]], observed: list[dict[str, Any]]) -> Server:
    """Answer the MCP handshake, then each tool call with the next result."""

    def respond(request: Request, index: int) -> Reply:
        assert request.path == "/mcp"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = json.loads(request.body)
        if body["method"] == "initialize":
            return Reply(
                body={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}
            )
        assert request.headers["MCP-Protocol-Version"] == "2025-11-25"
        if body["method"] == "notifications/initialized":
            return Reply(status=202, body=b"")
        observed.append(body["params"])
        result = results.pop(0)
        if "status" in result:
            return Reply(status=result["status"], body={"detail": "unavailable"})
        return Reply(body={"jsonrpc": "2.0", "id": 2, "result": result})

    return Server(respond)


def answer(data: dict[str, Any], *, refused: bool = False) -> dict[str, Any]:
    body = {"ok": not refused, ("error" if refused else "data"): data}
    return {
        "isError": refused,
        "structuredContent": body,
        "content": [{"type": "text", "text": json.dumps(body)}],
    }


async def invoke(client: Any, group: str, name: str, *args: Any, **kwargs: Any) -> Any:
    result = getattr(getattr(client, group), name)(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


@MODES
async def test_reads_forward_only_the_given_selectors(mode: str) -> None:
    cases: list[tuple[str, str, tuple[Any, ...], dict[str, Any], dict[str, Any]]] = [
        ("config", "get_configuration", (), {}, {}),
        (
            "config",
            "get_configuration",
            (),
            {"environment_id": str(REVIEW)},
            {"environment_id": str(REVIEW)},
        ),
        (
            "config",
            "get_configuration",
            (),
            {"repository": "owner/name"},
            {"repository": "owner/name"},
        ),
        ("config", "list_operations", (), {}, {}),
        (
            "config",
            "list_operations",
            (),
            {"area": "REPOSITORY_REVIEW_SETTINGS", "subject": "repository"},
            {"area": "REPOSITORY_REVIEW_SETTINGS", "subject": "repository"},
        ),
        (
            "config",
            "describe_operation",
            ("organization.settings.update",),
            {},
            {"operation": "organization.settings.update", "parameters": {}},
        ),
        (
            "config",
            "describe_operation",
            ("repository.wiki_settings.update", {"repo_id": "slug", "label": "a=b"}),
            {},
            {
                "operation": "repository.wiki_settings.update",
                "parameters": {"repo_id": "slug", "label": "a=b"},
            },
        ),
        ("config", "apply_change", (CHANGE,), {}, {"change_id": CHANGE}),
        ("setup", "get_setup_status", (), {}, {}),
        ("setup", "list_setup_candidates", (), {}, {}),
        ("setup", "list_setup_candidates", (), {"query": "api"}, {"query": "api"}),
    ]
    results = [answer({"case": index}) for index in range(len(cases) * 2)]
    observed: list[dict[str, Any]] = []
    with tool_server(results, observed) as server:
        async with session(mode, server.url) as client:
            index = 0
            for group, name, args, kwargs, expected in cases:
                for target in (None, str(ORG)):
                    targeted = {} if target is None else {"organization_id": target}
                    result = await invoke(client, group, name, *args, **kwargs, **targeted)
                    assert result["structuredContent"]["data"] == {"case": index}
                    assert observed[-1] == {
                        "name": name,
                        "arguments": {**expected, **targeted},
                    }
                    index += 1
        # Each call is one handshake and one tool request, never a retry.
        assert len(server.requests) == len(observed) * 3


@MODES
async def test_propose_sends_the_change_with_a_fresh_request_id(mode: str) -> None:
    cited: CitedFile = {
        "repository_id": str(REPOSITORY),
        "commit_sha": "b" * 40,
        "path": "infra/main.tf",
    }
    held = answer(
        {
            "applied": False,
            "change_id": CHANGE,
            "diff": {"current": {"enabled": False}, "proposed": {"enabled": True}},
        }
    )
    observed: list[dict[str, Any]] = []
    with tool_server([held, held, held, held], observed) as server:
        async with session(mode, server.url) as client:
            for _ in range(2):
                result = await invoke(
                    client,
                    "config",
                    "propose_change",
                    "environment.review_focus.update",
                    parameters={"env_id": str(REPOSITORY)},
                    input={"focus": "production"},
                    expected_revision="a" * 64,
                    cited_files=[cited],
                )
                assert result == held
            # A retry of the identical call keeps the caller's request ID.
            await invoke(
                client, "config", "propose_change", "organization.settings.update",
                request_id=CHANGE, organization_id=str(ORG),
            )  # fmt: skip
            # An operation without a body sends no input.
            await invoke(client, "config", "propose_change", "repository.wiki_settings.reset")

    generated = [UUID(params["arguments"].pop("request_id")) for params in observed[:2]]
    assert [identity.version for identity in generated] == [7, 7]
    assert generated[0] != generated[1]
    for params in observed[:2]:
        assert params == {
            "name": "propose_change",
            "arguments": {
                "operation": "environment.review_focus.update",
                "parameters": {"env_id": str(REPOSITORY)},
                "input": {"focus": "production"},
                "expected_revision": "a" * 64,
                "cited_files": [cited],
            },
        }
    assert observed[2]["arguments"] == {
        "operation": "organization.settings.update",
        "parameters": {},
        "request_id": CHANGE,
        "organization_id": str(ORG),
    }
    assert set(observed[3]["arguments"]) == {"operation", "parameters", "request_id"}


@MODES
async def test_refusals_and_held_changes_are_returned_and_never_retried(mode: str) -> None:
    refusal = answer(
        {"code": "NOT_AUTHORIZED", "message": "Missing org:configure", "retryable": False},
        refused=True,
    )
    sensitive = answer(
        {
            "applied": False,
            "reason": "An administrator must approve this change in the browser.",
            "approval_url": f"https://proofline.sh/orgs/by-id/{ORG}/configuration-changes/{CHANGE}",
        }
    )
    observed: list[dict[str, Any]] = []
    with tool_server([refusal, sensitive, {"status": 503}], observed) as server:
        async with session(mode, server.url) as client:
            result = await invoke(client, "config", "propose_change", "org.settings.update")
            assert result["isError"] is True
            assert result["structuredContent"]["error"]["code"] == "NOT_AUTHORIZED"
            held = await invoke(client, "config", "apply_change", CHANGE)
            assert held["structuredContent"]["data"]["applied"] is False
            with pytest.raises(ProoflineError):
                await invoke(client, "config", "apply_change", CHANGE)
    assert [params["name"] for params in observed] == [
        "propose_change",
        "apply_change",
        "apply_change",
    ]


def test_new_request_id_is_a_time_ordered_rfc_9562_uuid() -> None:
    before = time.time_ns() // 1_000_000
    identities = [UUID(new_request_id()) for _ in range(200)]
    after = time.time_ns() // 1_000_000
    assert len(set(identities)) == 200
    for identity in identities:
        assert identity.version == 7
        assert identity.variant == "specified in RFC 4122"
        assert before <= identity.int >> 80 <= after
