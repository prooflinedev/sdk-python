"""Transport-agnostic cursor pagination helpers for synchronous and asynchronous iterators."""

from __future__ import annotations

from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Iterator,
    Sequence,
)
from dataclasses import dataclass
from typing import Generic, TypeVar

from ._transport import ProoflineError

T = TypeVar("T")


@dataclass(frozen=True)
class PageResponse(Generic[T]):
    """A single cursor-paginated page returned by a page-fetching callback.

    Attributes:
        items: Items returned on the current page.
        next_cursor: Opaque continuation cursor for the next page, or ``None`` when exhausted.

    Example:
        >>> PageResponse(items=["rev-1", "rev-2"], next_cursor="cursor-2")
        PageResponse(items=['rev-1', 'rev-2'], next_cursor='cursor-2')
    """

    items: Sequence[T]
    next_cursor: str | None = None


def _validate_bound(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def _invalid_cursor_error() -> ProoflineError:
    return ProoflineError(
        0,
        "urn:proofline:sdk:invalid-pagination",
        "The page response has an empty or repeated continuation cursor.",
    )


def paginate(
    fetch_page: Callable[[str | None], PageResponse[T]],
    *,
    max_items: int | None = None,
    max_pages: int | None = None,
) -> Iterator[T]:
    """Lazily yield items across cursor-paginated pages.

    Pages are fetched strictly on demand: page ``N + 1`` is never requested until
    every item from page ``N`` has been consumed. Breaking out of the loop or closing
    the iterator stops further page fetches immediately.

    Args:
        fetch_page: Callable accepting the current cursor (``None`` for page 1) and
            returning a :class:`PageResponse`.
        max_items: Optional positive upper bound on yielded items. Iteration stops
            gracefully once this count is reached.
        max_pages: Optional positive upper bound on fetched pages. Iteration stops
            gracefully after this many pages have been fetched.

    Raises:
        ValueError: Eagerly when ``max_items`` or ``max_pages`` is not a positive integer.
        ProoflineError: With type ``urn:proofline:sdk:invalid-pagination`` when a page
            returns an empty or previously seen continuation cursor.

    Example:
        >>> def fetch(cursor: str | None) -> PageResponse[int]:
        ...     if cursor is None:
        ...         return PageResponse(items=[1, 2], next_cursor="p2")
        ...     return PageResponse(items=[3], next_cursor=None)
        >>> list(paginate(fetch, max_items=2))
        [1, 2]
    """
    _validate_bound("max_items", max_items)
    _validate_bound("max_pages", max_pages)

    def _iterate() -> Iterator[T]:
        cursor: str | None = None
        seen_cursors: set[str] = set()
        pages_fetched = 0
        items_yielded = 0

        while True:
            page = fetch_page(cursor)
            pages_fetched += 1

            for item in page.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return

            if max_pages is not None and pages_fetched >= max_pages:
                return

            next_cursor = page.next_cursor
            if next_cursor is None:
                return

            if not isinstance(next_cursor, str) or not next_cursor or next_cursor in seen_cursors:
                raise _invalid_cursor_error()

            seen_cursors.add(next_cursor)
            cursor = next_cursor

    return _iterate()


def async_paginate(
    fetch_page: Callable[[str | None], Awaitable[PageResponse[T]]],
    *,
    max_items: int | None = None,
    max_pages: int | None = None,
) -> AsyncIterator[T]:
    """Lazily yield items asynchronously across cursor-paginated pages.

    Pages are awaited strictly on demand: page ``N + 1`` is never requested until
    every item from page ``N`` has been consumed. Breaking out of ``async for`` or
    closing the iterator with ``aclose()`` stops further page fetches immediately.
    Task cancellation (``asyncio.CancelledError``) propagates without suppression.

    Args:
        fetch_page: Async callable accepting the current cursor (``None`` for page 1)
            and resolving to a :class:`PageResponse`.
        max_items: Optional positive upper bound on yielded items. Iteration stops
            gracefully once this count is reached.
        max_pages: Optional positive upper bound on fetched pages. Iteration stops
            gracefully after this many pages have been fetched.

    Raises:
        ValueError: Eagerly when ``max_items`` or ``max_pages`` is not a positive integer.
        ProoflineError: With type ``urn:proofline:sdk:invalid-pagination`` when a page
            returns an empty or previously seen continuation cursor.

    Example:
        ```python
        async def fetch(cursor: str | None) -> PageResponse[int]:
            if cursor is None:
                return PageResponse(items=[1, 2], next_cursor="p2")
            return PageResponse(items=[3], next_cursor=None)

        async for item in async_paginate(fetch, max_items=2):
            print(item)
        ```
    """
    _validate_bound("max_items", max_items)
    _validate_bound("max_pages", max_pages)

    async def _iterate() -> AsyncIterator[T]:
        cursor: str | None = None
        seen_cursors: set[str] = set()
        pages_fetched = 0
        items_yielded = 0

        while True:
            page = await fetch_page(cursor)
            pages_fetched += 1

            for item in page.items:
                yield item
                items_yielded += 1
                if max_items is not None and items_yielded >= max_items:
                    return

            if max_pages is not None and pages_fetched >= max_pages:
                return

            next_cursor = page.next_cursor
            if next_cursor is None:
                return

            if not isinstance(next_cursor, str) or not next_cursor or next_cursor in seen_cursors:
                raise _invalid_cursor_error()

            seen_cursors.add(next_cursor)
            cursor = next_cursor

    return _iterate()


def collect_all(items: Iterable[T]) -> list[T]:
    """Eagerly materialize a synchronous iterable into a list.

    Example:
        >>> collect_all(paginate(lambda _: PageResponse(items=[1, 2], next_cursor=None)))
        [1, 2]
    """
    return list(items)


async def async_collect_all(items: AsyncIterable[T]) -> list[T]:
    """Eagerly materialize an asynchronous iterable into a list.

    Example:
        ```python
        items = await async_collect_all(
            async_paginate(fetch_page, max_items=100)
        )
        ```
    """
    return [item async for item in items]
