"""The MCP request size limit fails with the SDK's typed error."""

import httpx2
import pytest

from proofline._mcp import _body
from proofline._transport import ProoflineError
from proofline.knowledge import AsyncKnowledgeClient, KnowledgeClient


def test_oversized_body_raises_proofline_error() -> None:
    with pytest.raises(ProoflineError) as caught:
        _body("tools/call", {"name": "ask_codebase", "arguments": {"question": "q" * 9000}}, 2)

    assert caught.value.status == 0
    assert caught.value.type == "urn:proofline:sdk:mcp"


def test_normal_body_is_within_the_limit() -> None:
    data = _body("tools/call", {"name": "ask_codebase", "arguments": {"question": "why?"}}, 2)

    assert len(data) <= 8192


def test_long_question_raises_before_any_request() -> None:
    client = KnowledgeClient(httpx2.Client(base_url="https://proofline.invalid"))

    with pytest.raises(ProoflineError) as caught:
        client.ask_codebase("owner/name", "q" * 9000)

    assert caught.value.type == "urn:proofline:sdk:mcp"


async def test_long_question_raises_before_any_request_async() -> None:
    client = AsyncKnowledgeClient(httpx2.AsyncClient(base_url="https://proofline.invalid"))

    with pytest.raises(ProoflineError) as caught:
        await client.ask_codebase("owner/name", "q" * 9000)

    assert caught.value.type == "urn:proofline:sdk:mcp"
