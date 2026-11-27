"""Deterministic unit and HTTP tests for generic and client auto-pagination."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Generator, Iterator
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import pytest
from pydantic import SecretStr

import proofline
from proofline import (
    AsyncProoflineClient,
    PageResponse,
    ProoflineClient,
    ProoflineError,
    ReviewFilters,
    async_collect_all,
    async_paginate,
    collect_all,
    paginate,
)

from .fixtures import ORG, REPOSITORY, TOKEN, page, summary
from .http_server import Reply, Request, Server

Client = ProoflineClient | AsyncProoflineClient
MODES = pytest.mark.parametrize("mode", ["sync", "async"])
REVIEW_1 = UUID("00000000-0000-4000-8000-000000000101")
REVIEW_2 = UUID("00000000-0000-4000-8000-000000000102")
REVIEW_3 = UUID("00000000-0000-4000-8000-000000000103")
REVIEW_4 = UUID("00000000-0000-4000-8000-000000000104")


def review_item(review_id: UUID, status: str = "COMPLETED") -> dict[str, Any]:
    item = summary(status)
    item["id"] = str(review_id)
    return item


def review_page(
    review_ids: list[UUID],
    *,
    cursor: str | None = None,
    truncated: bool = False,
) -> dict[str, Any]:
    body = page(cursor=cursor, truncated=truncated)
    body["items"] = [review_item(review_id) for review_id in review_ids]
    return body


@asynccontextmanager
async def session(mode: str, url: str) -> AsyncIterator[Client]:
    if mode == "sync":
        with ProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            yield client
    else:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url) as async_client:
            yield async_client


async def call(client: Client, name: str, *args: Any, **kwargs: Any) -> Any:
    result = getattr(client, name)(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def drain(iterator: Iterator[Any] | AsyncIterator[Any]) -> list[Any]:
    if isinstance(iterator, AsyncIterator):
        return await async_collect_all(iterator)
    return collect_all(iterator)


# ---------------------------------------------------------------------------
# Public exports & PageResponse
# ---------------------------------------------------------------------------


def test_public_pagination_exports_and_sorted_all() -> None:
    expected = {
        "PageResponse",
        "paginate",
        "async_paginate",
        "collect_all",
        "async_collect_all",
    }
    assert expected.issubset(set(proofline.__all__))
    assert proofline.__all__ == sorted(proofline.__all__)
    for name in expected:
        assert hasattr(proofline, name)

    response = PageResponse(items=[1, 2])
    assert response.items == [1, 2]
    assert response.next_cursor is None
    with pytest.raises(AttributeError):
        setattr(response, "next_cursor", "mutated")
    assert collect_all(iter(())) == []


# ---------------------------------------------------------------------------
# Sync paginate() & collect_all()
# ---------------------------------------------------------------------------


def test_sync_paginate_single_page() -> None:
    cursors: list[str | None] = []

    def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return PageResponse(items=["a", "b"], next_cursor=None)

    assert collect_all(paginate(fetch)) == ["a", "b"]
    assert cursors == [None]


def test_sync_paginate_multi_page_is_strictly_lazy() -> None:
    pages = {
        None: PageResponse(items=["a", "b"], next_cursor="c1"),
        "c1": PageResponse(items=["c", "d"], next_cursor="c2"),
        "c2": PageResponse(items=["e"], next_cursor=None),
    }
    cursors: list[str | None] = []

    def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return pages[cursor]

    iterator = paginate(fetch)
    assert cursors == []

    assert next(iterator) == "a"
    assert cursors == [None]
    assert next(iterator) == "b"
    assert cursors == [None]

    assert next(iterator) == "c"
    assert cursors == [None, "c1"]
    assert next(iterator) == "d"
    assert cursors == [None, "c1"]

    assert next(iterator) == "e"
    assert cursors == [None, "c1", "c2"]

    with pytest.raises(StopIteration):
        next(iterator)
    assert cursors == [None, "c1", "c2"]


def test_sync_paginate_early_break_and_close_stop_fetching() -> None:
    calls = 0

    def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        calls += 1
        return PageResponse(items=[1, 2, 3], next_cursor=f"c{calls}")

    collected: list[int] = []
    for item in paginate(fetch):
        collected.append(item)
        if len(collected) == 2:
            break
    assert collected == [1, 2]
    assert calls == 1

    calls = 0
    iterator = paginate(fetch)
    assert isinstance(iterator, Generator)
    assert next(iterator) == 1
    iterator.close()
    assert calls == 1
    with pytest.raises(StopIteration):
        next(iterator)
    assert calls == 1


def test_sync_paginate_empty_intermediate_page_and_max_pages() -> None:
    pages = {
        None: PageResponse(items=[], next_cursor="c1"),
        "c1": PageResponse(items=["itemA"], next_cursor=None),
    }
    cursors: list[str | None] = []

    def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return pages[cursor]

    assert collect_all(paginate(fetch)) == ["itemA"]
    assert cursors == [None, "c1"]

    empty_calls = 0

    def always_empty(cursor: str | None) -> PageResponse[str]:
        nonlocal empty_calls
        empty_calls += 1
        return PageResponse(items=[], next_cursor=f"c{empty_calls}")

    assert collect_all(paginate(always_empty, max_pages=2)) == []
    assert empty_calls == 2


@pytest.mark.parametrize(
    ("cursor_sequence", "expected_calls"),
    [
        (["c1", "c1"], 2),
        (["c1", "c2", "c1"], 3),
        ([""], 1),
    ],
    ids=["repeated", "cycle", "empty"],
)
def test_sync_paginate_invalid_or_repeated_cursor_raises(
    cursor_sequence: list[str], expected_calls: int
) -> None:
    calls = 0

    def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        next_cursor = cursor_sequence[calls]
        calls += 1
        return PageResponse(items=[calls], next_cursor=next_cursor)

    seen: list[int] = []
    with pytest.raises(ProoflineError) as raised:
        for item in paginate(fetch):
            seen.append(item)
    assert raised.value.status == 0
    assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
    assert calls == expected_calls
    assert seen == list(range(1, expected_calls + 1))


def test_sync_paginate_max_items_and_max_pages_bounds() -> None:
    calls = 0

    def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        page_index = calls
        calls += 1
        base = page_index * 3
        return PageResponse(
            items=[base + 1, base + 2, base + 3],
            next_cursor=f"c{calls}" if calls < 5 else None,
        )

    assert collect_all(paginate(fetch, max_items=4)) == [1, 2, 3, 4]
    assert calls == 2

    calls = 0
    assert collect_all(paginate(fetch, max_items=3)) == [1, 2, 3]
    assert calls == 1

    calls = 0
    assert collect_all(paginate(fetch, max_pages=2)) == [1, 2, 3, 4, 5, 6]
    assert calls == 2

    calls = 0
    assert collect_all(paginate(fetch, max_items=5, max_pages=2)) == [1, 2, 3, 4, 5]
    assert calls == 2


@pytest.mark.parametrize("bad_value", [0, -1, -100, True, False, 1.5, "2"])
def test_sync_paginate_validates_bounds_eagerly_before_fetch(bad_value: Any) -> None:
    calls = 0

    def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        calls += 1
        return PageResponse(items=[1], next_cursor=None)

    with pytest.raises(ValueError, match="max_items"):
        paginate(fetch, max_items=bad_value)
    with pytest.raises(ValueError, match="max_pages"):
        paginate(fetch, max_pages=bad_value)
    assert calls == 0


def test_sync_paginate_propagates_error_on_page_two() -> None:
    def fetch(cursor: str | None) -> PageResponse[str]:
        if cursor is None:
            return PageResponse(items=["p1-a", "p1-b"], next_cursor="c1")
        raise ProoflineError(500, "urn:proofline:test:server-error", "Internal failure.")

    yielded: list[str] = []
    with pytest.raises(ProoflineError) as raised:
        for item in paginate(fetch):
            yielded.append(item)
    assert yielded == ["p1-a", "p1-b"]
    assert raised.value.status == 500


# ---------------------------------------------------------------------------
# Async async_paginate() & async_collect_all()
# ---------------------------------------------------------------------------


async def test_async_paginate_single_page() -> None:
    cursors: list[str | None] = []

    async def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return PageResponse(items=["a", "b"], next_cursor=None)

    assert await async_collect_all(async_paginate(fetch)) == ["a", "b"]
    assert cursors == [None]


async def test_async_paginate_multi_page_is_strictly_lazy() -> None:
    pages = {
        None: PageResponse(items=["a", "b"], next_cursor="c1"),
        "c1": PageResponse(items=["c", "d"], next_cursor="c2"),
        "c2": PageResponse(items=["e"], next_cursor=None),
    }
    cursors: list[str | None] = []

    async def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return pages[cursor]

    iterator = async_paginate(fetch)
    assert cursors == []

    assert await anext(iterator) == "a"
    assert cursors == [None]
    assert await anext(iterator) == "b"
    assert cursors == [None]

    assert await anext(iterator) == "c"
    assert cursors == [None, "c1"]
    assert await anext(iterator) == "d"
    assert cursors == [None, "c1"]

    assert await anext(iterator) == "e"
    assert cursors == [None, "c1", "c2"]

    with pytest.raises(StopAsyncIteration):
        await anext(iterator)
    assert cursors == [None, "c1", "c2"]


async def test_async_paginate_early_break_and_aclose_stop_fetching() -> None:
    calls = 0

    async def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        calls += 1
        return PageResponse(items=[1, 2, 3], next_cursor=f"c{calls}")

    collected: list[int] = []
    async for item in async_paginate(fetch):
        collected.append(item)
        if len(collected) == 2:
            break
    assert collected == [1, 2]
    assert calls == 1

    calls = 0
    iterator = async_paginate(fetch)
    assert isinstance(iterator, AsyncGenerator)
    assert await anext(iterator) == 1
    await iterator.aclose()
    assert calls == 1
    with pytest.raises(StopAsyncIteration):
        await anext(iterator)
    assert calls == 1


async def test_async_paginate_empty_intermediate_page_and_max_pages() -> None:
    pages = {
        None: PageResponse(items=[], next_cursor="c1"),
        "c1": PageResponse(items=["itemA"], next_cursor=None),
    }
    cursors: list[str | None] = []

    async def fetch(cursor: str | None) -> PageResponse[str]:
        cursors.append(cursor)
        return pages[cursor]

    assert await async_collect_all(async_paginate(fetch)) == ["itemA"]
    assert cursors == [None, "c1"]

    empty_calls = 0

    async def always_empty(cursor: str | None) -> PageResponse[str]:
        nonlocal empty_calls
        empty_calls += 1
        return PageResponse(items=[], next_cursor=f"c{empty_calls}")

    assert await async_collect_all(async_paginate(always_empty, max_pages=2)) == []
    assert empty_calls == 2


@pytest.mark.parametrize(
    ("cursor_sequence", "expected_calls"),
    [
        (["c1", "c1"], 2),
        (["c1", "c2", "c1"], 3),
        ([""], 1),
    ],
    ids=["repeated", "cycle", "empty"],
)
async def test_async_paginate_invalid_or_repeated_cursor_raises(
    cursor_sequence: list[str], expected_calls: int
) -> None:
    calls = 0

    async def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        next_cursor = cursor_sequence[calls]
        calls += 1
        return PageResponse(items=[calls], next_cursor=next_cursor)

    seen: list[int] = []
    with pytest.raises(ProoflineError) as raised:
        async for item in async_paginate(fetch):
            seen.append(item)
    assert raised.value.status == 0
    assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
    assert calls == expected_calls
    assert seen == list(range(1, expected_calls + 1))


async def test_async_paginate_max_items_and_max_pages_bounds() -> None:
    calls = 0

    async def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        page_index = calls
        calls += 1
        base = page_index * 3
        return PageResponse(
            items=[base + 1, base + 2, base + 3],
            next_cursor=f"c{calls}" if calls < 5 else None,
        )

    assert await async_collect_all(async_paginate(fetch, max_items=4)) == [1, 2, 3, 4]
    assert calls == 2

    calls = 0
    assert await async_collect_all(async_paginate(fetch, max_items=3)) == [1, 2, 3]
    assert calls == 1

    calls = 0
    assert await async_collect_all(async_paginate(fetch, max_pages=2)) == [1, 2, 3, 4, 5, 6]
    assert calls == 2


@pytest.mark.parametrize("bad_value", [0, -1, -100, True, False, 1.5, "2"])
def test_async_paginate_validates_bounds_eagerly_before_fetch(bad_value: Any) -> None:
    calls = 0

    async def fetch(cursor: str | None) -> PageResponse[int]:
        nonlocal calls
        calls += 1
        return PageResponse(items=[1], next_cursor=None)

    with pytest.raises(ValueError, match="max_items"):
        async_paginate(fetch, max_items=bad_value)
    with pytest.raises(ValueError, match="max_pages"):
        async_paginate(fetch, max_pages=bad_value)
    assert calls == 0


async def test_async_paginate_propagates_error_on_page_two() -> None:
    async def fetch(cursor: str | None) -> PageResponse[str]:
        if cursor is None:
            return PageResponse(items=["p1-a", "p1-b"], next_cursor="c1")
        raise ProoflineError(500, "urn:proofline:test:server-error", "Internal failure.")

    yielded: list[str] = []
    with pytest.raises(ProoflineError) as raised:
        async for item in async_paginate(fetch):
            yielded.append(item)
    assert yielded == ["p1-a", "p1-b"]
    assert raised.value.status == 500


async def test_async_paginate_propagates_task_cancellation() -> None:
    page2_started = asyncio.Event()
    never_set = asyncio.Event()
    calls = 0
    yielded: list[str] = []

    async def fetch(cursor: str | None) -> PageResponse[str]:
        nonlocal calls
        calls += 1
        if cursor is None:
            return PageResponse(items=["p1-a"], next_cursor="c1")
        page2_started.set()
        await never_set.wait()
        return PageResponse(items=["unreachable"], next_cursor=None)

    async def runner() -> None:
        async for item in async_paginate(fetch):
            yielded.append(item)

    task = asyncio.create_task(runner())
    await page2_started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert yielded == ["p1-a"]
    assert calls == 2


async def test_async_collect_all_empty() -> None:
    async def empty() -> AsyncIterator[int]:
        if False:
            yield 0

    assert await async_collect_all(empty()) == []


# ---------------------------------------------------------------------------
# Client wrappers: ProoflineClient & AsyncProoflineClient over loopback HTTP
# ---------------------------------------------------------------------------


@MODES
async def test_iter_pull_request_reviews_preserves_filters_and_stops_lazily(mode: str) -> None:
    pages = [
        review_page([REVIEW_1, REVIEW_2], cursor="pr-c1", truncated=True),
        review_page([], cursor="pr-c2", truncated=True),
        review_page([REVIEW_3], cursor=None, truncated=False),
    ]

    def respond(request: Request, index: int) -> Reply:
        parsed = urlsplit(request.path)
        assert parsed.path == f"/api/v1/organizations/{ORG}/reviews/pr/owner%2Frepo/42"
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        query = parse_qs(parsed.query)
        assert query["repository"] == [str(REPOSITORY)]
        assert query["status"] == ["COMPLETED"]
        assert query["limit"] == ["2"]
        if index == 0:
            assert "cursor" not in query
        elif index == 1:
            assert query["cursor"] == ["pr-c1"]
        else:
            assert query["cursor"] == ["pr-c2"]
        return Reply(body=pages[index])

    caller_filters: ReviewFilters = {"repository": REPOSITORY, "status": "COMPLETED"}
    with Server(respond) as server:
        async with session(mode, server.url) as client:
            items = await drain(
                client.iter_pull_request_reviews(
                    ORG,
                    "owner/repo",
                    42,
                    page_size=2,
                    filters=caller_filters,
                )
            )
            assert [item.id for item in items] == [REVIEW_1, REVIEW_2, REVIEW_3]
            assert caller_filters == {"repository": REPOSITORY, "status": "COMPLETED"}
        assert len(server.requests) == 3

    # Early break fetches only page 1.
    with Server(respond) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_pull_request_reviews(
                ORG, "owner/repo", 42, page_size=2, filters=caller_filters
            )
            collected: list[UUID] = []
            if isinstance(iterator, AsyncIterator):
                async for review in iterator:
                    collected.append(review.id)
                    break
            else:
                for review in iterator:
                    collected.append(review.id)
                    break
            assert collected == [REVIEW_1]
        assert len(server.requests) == 1


@MODES
async def test_iter_pull_request_reviews_bounds_and_errors(mode: str) -> None:
    pages = [
        review_page([REVIEW_1, REVIEW_2], cursor="c1", truncated=True),
        review_page([REVIEW_3, REVIEW_4], cursor="c2", truncated=True),
        review_page([REVIEW_1], cursor=None, truncated=False),
    ]

    with Server(lambda request, index: Reply(body=pages[index])) as server:
        async with session(mode, server.url) as client:
            limited_items = await drain(
                client.iter_pull_request_reviews(ORG, "owner/repo", 42, max_items=3)
            )
            assert [item.id for item in limited_items] == [REVIEW_1, REVIEW_2, REVIEW_3]
        assert len(server.requests) == 2

    with Server(lambda request, index: Reply(body=pages[index])) as server:
        async with session(mode, server.url) as client:
            limited_pages = await drain(
                client.iter_pull_request_reviews(ORG, "owner/repo", 42, max_pages=1)
            )
            assert [item.id for item in limited_pages] == [REVIEW_1, REVIEW_2]
        assert len(server.requests) == 1

    # Invalid bounds raise eagerly before any HTTP call.
    invalid_kwargs: tuple[dict[str, Any], ...] = (
        {"page_size": 0},
        {"page_size": 101},
        {"page_size": True},
        {"max_items": 0},
        {"max_items": True},
        {"max_pages": -1},
    )
    with Server(lambda request, index: Reply(body=pages[0])) as server:
        async with session(mode, server.url) as client:
            for kwargs in invalid_kwargs:
                with pytest.raises(ValueError):
                    client.iter_pull_request_reviews(ORG, "owner/repo", 42, **kwargs)
        assert not server.requests

    # Repeated, missing, or resume-echoed continuation cursors raise invalid-pagination.
    def make_truncated_reply(cursor_value: str | None) -> Callable[[Request, int], Reply]:
        def respond(request: Request, index: int) -> Reply:
            return Reply(body=review_page([REVIEW_1], cursor=cursor_value, truncated=True))

        return respond

    invalid_cursor_cases: tuple[tuple[str | None, ReviewFilters | None], ...] = (
        ("repeat", None),
        (None, None),
        ("initial", {"cursor": "initial"}),
    )
    for bad_cursor, initial_filters in invalid_cursor_cases:
        with Server(make_truncated_reply(bad_cursor)) as server:
            async with session(mode, server.url) as client:
                with pytest.raises(ProoflineError) as raised:
                    await drain(
                        client.iter_pull_request_reviews(
                            ORG,
                            "owner/repo",
                            42,
                            filters=initial_filters,
                        )
                    )
                assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
            assert len(server.requests) <= 2

    # Non-truncated page with a cursor is an invalid response.
    with Server(
        lambda request, index: Reply(
            body=review_page([REVIEW_1], cursor="unexpected", truncated=False)
        )
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await drain(client.iter_pull_request_reviews(ORG, "owner/repo", 42))
            assert raised.value.type == "urn:proofline:sdk:invalid-response"

    # HTTP error on page 2 yields page 1 items first, then propagates ProoflineError.
    def fail_on_page_2(request: Request, index: int) -> Reply:
        if index == 0:
            return Reply(body=review_page([REVIEW_1], cursor="c1", truncated=True))
        return Reply(status=404, body={"detail": "missing page"})

    with Server(fail_on_page_2) as server:
        async with session(mode, server.url) as client:
            yielded: list[UUID] = []
            iterator = client.iter_pull_request_reviews(ORG, "owner/repo", 42)
            with pytest.raises(ProoflineError) as raised:
                if isinstance(iterator, AsyncIterator):
                    async for review in iterator:
                        yielded.append(review.id)
                else:
                    for review in iterator:
                        yielded.append(review.id)
            assert yielded == [REVIEW_1]
            assert raised.value.status == 404


@MODES
async def test_list_all_reviews_and_list_all_pull_request_reviews(mode: str) -> None:
    review_pages = [
        review_page([REVIEW_1, REVIEW_2], cursor="r1", truncated=True),
        review_page([REVIEW_3, REVIEW_4], cursor="r2", truncated=True),
        review_page([REVIEW_1], cursor=None, truncated=False),
    ]

    def respond_org(request: Request, index: int) -> Reply:
        parsed = urlsplit(request.path)
        assert parsed.path == f"/api/v1/organizations/{ORG}/reviews"
        query = parse_qs(parsed.query)
        assert query["status"] == ["COMPLETED"]
        assert query["limit"] == ["2"]
        return Reply(body=review_pages[index])

    org_filters: ReviewFilters = {"status": "COMPLETED"}
    with Server(respond_org) as server:
        async with session(mode, server.url) as client:
            all_reviews = await call(
                client,
                "list_all_reviews",
                ORG,
                page_size=2,
                filters=org_filters,
            )
            assert [item.id for item in all_reviews] == [
                REVIEW_1,
                REVIEW_2,
                REVIEW_3,
                REVIEW_4,
                REVIEW_1,
            ]
            assert org_filters == {"status": "COMPLETED"}
        assert len(server.requests) == 3

    with Server(respond_org) as server:
        async with session(mode, server.url) as client:
            bounded_reviews = await call(
                client,
                "list_all_reviews",
                ORG,
                page_size=2,
                max_items=3,
                filters=org_filters,
            )
            assert [item.id for item in bounded_reviews] == [REVIEW_1, REVIEW_2, REVIEW_3]
        assert len(server.requests) == 2

    with Server(respond_org) as server:
        async with session(mode, server.url) as client:
            bounded_pages = await call(
                client,
                "list_all_reviews",
                ORG,
                page_size=2,
                max_pages=1,
                filters=org_filters,
            )
            assert [item.id for item in bounded_pages] == [REVIEW_1, REVIEW_2]
        assert len(server.requests) == 1

    # Invalid bounds raise ValueError without making HTTP requests.
    with Server(respond_org) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ValueError):
                await call(client, "list_all_reviews", ORG, max_items=0)
            with pytest.raises(ValueError):
                await call(
                    client,
                    "list_all_pull_request_reviews",
                    ORG,
                    "owner/repo",
                    42,
                    max_pages=0,
                )
        assert not server.requests

    # Repeated cursor in list_all_reviews raises invalid-pagination.
    with Server(
        lambda request, index: Reply(body=review_page([REVIEW_1], cursor="dup", truncated=True))
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as raised:
                await call(client, "list_all_reviews", ORG)
            assert raised.value.type == "urn:proofline:sdk:invalid-pagination"
        assert len(server.requests) == 2

    # list_all_pull_request_reviews collects across PR review pages with bounds.
    def respond_pr(request: Request, index: int) -> Reply:
        parsed = urlsplit(request.path)
        assert parsed.path == f"/api/v1/organizations/{ORG}/reviews/pr/owner%2Frepo/42"
        query = parse_qs(parsed.query)
        assert query["limit"] == ["2"]
        return Reply(body=review_pages[index])

    with Server(respond_pr) as server:
        async with session(mode, server.url) as client:
            pr_reviews = await call(
                client,
                "list_all_pull_request_reviews",
                ORG,
                "owner/repo",
                42,
                page_size=2,
                max_items=3,
            )
            assert [item.id for item in pr_reviews] == [REVIEW_1, REVIEW_2, REVIEW_3]
        assert len(server.requests) == 2
