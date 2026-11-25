from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from proofline import ProoflineError, ReviewFilters

from .fixtures import ORG, REPOSITORY, REVIEW, TOKEN, page
from .http_server import Reply, Request, Server
from .test_http import MODES, STRUCTURED_QUERY, Client, session


async def collect(client: Client, **kwargs: Any) -> list[Any]:
    iterator = client.iter_pull_request_reviews(ORG, "repo/name", 42, **kwargs)
    if hasattr(iterator, "__aiter__"):
        return [item async for item in iterator]
    return list(iterator)


@MODES
async def test_pr_history_preserves_scope_filters_and_caller_mapping(mode: str) -> None:
    filters: ReviewFilters = {
        "repository": REPOSITORY,
        "status": "COMPLETED",
        "query": STRUCTURED_QUERY,
        "search": "text & space",
        "cursor": "initial",
        "limit": 9,
    }
    original = dict(filters)

    def respond(request: Request, index: int) -> Reply:
        assert (
            urlsplit(request.path).path == f"/api/v1/organizations/{ORG}/reviews/pr/repo%2Fname/42"
        )
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        query = parse_qs(urlsplit(request.path).query)
        assert query == {
            "repository": [str(REPOSITORY)],
            "status": ["COMPLETED"],
            "query": [STRUCTURED_QUERY],
            "search": ["text & space"],
            "limit": ["2"],
            "cursor": ["initial" if index == 0 else "opaque+/cursor"],
        }
        return Reply(
            body=page(cursor="opaque+/cursor" if index == 0 else None, truncated=index == 0)
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            items = await collect(client, page_size=2, filters=filters)
            assert [item.id for item in items] == [REVIEW, REVIEW]
        assert len(server.requests) == 2
    assert filters == original


@MODES
@pytest.mark.parametrize("cursor", [None, "initial"])
async def test_pr_history_invalid_continuation(mode: str, cursor: str | None) -> None:
    with Server(lambda request, index: Reply(body=page(cursor=cursor, truncated=True))) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await collect(client, filters={"cursor": "initial"})
            assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
        assert len(server.requests) == 1


@MODES
async def test_pr_history_page_bound(mode: str) -> None:
    with Server(
        lambda request, index: Reply(body=page(cursor=str(index), truncated=True))
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await collect(client, max_pages=2)
            assert raised.value.type == "urn:proofline:sdk:pagination-limit"
        assert len(server.requests) == 2


@MODES
async def test_pr_history_item_bound(mode: str) -> None:
    two = page()
    two["items"].append(dict(two["items"][0]))
    with Server(lambda request, index: Reply(body=two)) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await collect(client, max_items=1)
            assert raised.value.type == "urn:proofline:sdk:pagination-limit"
        assert len(server.requests) == 1


@MODES
@pytest.mark.parametrize("bounds", [{"page_size": 0}, {"max_pages": 0}, {"max_items": 0}])
async def test_pr_history_rejects_bounds_before_request(mode: str, bounds: dict[str, int]) -> None:
    with Server(lambda request, index: Reply(body=page())) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ValueError):
                await collect(client, **bounds)
        assert not server.requests
