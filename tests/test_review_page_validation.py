from __future__ import annotations

from typing import Any

import pytest

from proofline import ProoflineError

from .fixtures import ORG
from .http_server import Reply, Server
from .test_http import MODES, page, session


async def next_review(client: Any) -> Any:
    iterator = client.iter_reviews(ORG)
    if hasattr(iterator, "__aiter__"):
        return await anext(iterator)
    return next(iterator)


@MODES
@pytest.mark.parametrize(
    "cursor,truncated,error_type",
    [
        (None, True, "invalid-pagination"),
        ("", True, "invalid-pagination"),
        ("unexpected", False, "invalid-response"),
    ],
)
async def test_invalid_first_page_is_rejected_before_yield(
    mode: str, cursor: str | None, truncated: bool, error_type: str
) -> None:
    with Server(
        lambda request, index: Reply(body=page(cursor=cursor, truncated=truncated))
    ) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ProoflineError) as caught:
                await next_review(client)
            assert caught.value.type == f"urn:proofline:sdk:{error_type}"
        assert len(server.requests) == 1


@MODES
async def test_repeated_cursor_page_is_rejected_before_yield(mode: str) -> None:
    with Server(lambda request, index: Reply(body=page(cursor="same", truncated=True))) as server:
        async with session(mode, server.url) as client:
            iterator = client.iter_reviews(ORG)
            if mode == "sync":
                next(iterator)
                with pytest.raises(ProoflineError) as caught:
                    next(iterator)
            else:
                await anext(iterator)
                with pytest.raises(ProoflineError) as caught:
                    await anext(iterator)
            assert caught.value.type == "urn:proofline:sdk:invalid-pagination"
        assert len(server.requests) == 2
