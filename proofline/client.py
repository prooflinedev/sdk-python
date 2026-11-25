"""Small sync and async facades over the generated review operations."""

from __future__ import annotations

import math
import threading
from asyncio import FIRST_COMPLETED
from asyncio import CancelledError as AsyncCancelledError
from asyncio import Event as AsyncEvent
from asyncio import Future as AsyncFuture
from asyncio import get_running_loop as async_get_running_loop
from asyncio import sleep as async_sleep
from asyncio import wait as async_wait
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from string import hexdigits
from time import monotonic, sleep
from types import TracebackType
from typing import Any, Self, TypedDict, TypeVar, Unpack, cast
from urllib.parse import quote
from uuid import UUID

import httpx2
from pydantic import SecretStr

from . import _transport
from ._generated.api.default import (
    get_agent_session,
    get_agent_session_prompt,
    get_assessment,
    get_deployment_review,
    get_finding,
    get_finding_fix_prompt,
    get_pull_request_review,
    get_review,
    get_review_guidance,
    get_review_routing,
    list_pull_request_reviews,
    list_repositories,
    list_reviews,
    request_commit_review,
    request_file_review,
    request_patch_review,
    request_review,
    rerun_review,
    start_agent_session,
    stop_review,
    upload_coverage_reports,
)
from ._generated.api.operations import AsyncOperations, Operations
from ._generated.client import AuthenticatedClient
from ._generated.models.agent_session import AgentSession
from ._generated.models.agent_session_prompt_type_0 import AgentSessionPromptType0
from ._generated.models.agent_session_prompt_type_1 import AgentSessionPromptType1
from ._generated.models.commit_review_request import CommitReviewRequest
from ._generated.models.commit_review_response import CommitReviewResponse
from ._generated.models.coverage_upload_request import CoverageUploadRequest
from ._generated.models.coverage_upload_response import CoverageUploadResponse
from ._generated.models.customer_assessment_detail import CustomerAssessmentDetail
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.file_review_request import FileReviewRequest
from ._generated.models.file_review_response import FileReviewResponse
from ._generated.models.finding_fix_prompt_type_0 import FindingFixPromptType0
from ._generated.models.finding_fix_prompt_type_1 import FindingFixPromptType1
from ._generated.models.patch_review_request import PatchReviewRequest
from ._generated.models.patch_review_response import PatchReviewResponse
from ._generated.models.repository_guidance import RepositoryGuidance
from ._generated.models.repository_names import RepositoryNames
from ._generated.models.rerun_response import RerunResponse
from ._generated.models.review_page import ReviewPage
from ._generated.models.review_routing_view_type_0 import ReviewRoutingViewType0
from ._generated.models.review_routing_view_type_1 import ReviewRoutingViewType1
from ._generated.models.review_routing_view_type_2 import ReviewRoutingViewType2
from ._generated.models.review_summary import ReviewSummary
from ._generated.models.run_now_request import RunNowRequest
from ._generated.models.run_now_response import RunNowResponse
from ._generated.models.start_session import StartSession
from ._generated.models.stop_response import StopResponse
from ._generated.types import UNSET, Response, Unset
from ._mcp import AsyncMcpClient, McpClient
from ._transport import ProoflineError
from .exports import ExportDataset, ExportFormat, ExportPage, decode_export
from .fixes import AsyncFixesClient, FixesClient
from .knowledge import AsyncKnowledgeClient, KnowledgeClient
from .outcomes import ReviewOutcome, outcome

T = TypeVar("T")
AgentSessionPrompt = AgentSessionPromptType0 | AgentSessionPromptType1
_AgentSessionPromptModels = tuple[type[AgentSessionPromptType0], type[AgentSessionPromptType1]]
_AGENT_SESSION_PROMPT_MODELS: _AgentSessionPromptModels = (
    AgentSessionPromptType0,
    AgentSessionPromptType1,
)
FindingFixPrompt = FindingFixPromptType0 | FindingFixPromptType1
_FindingFixPromptModels = tuple[type[FindingFixPromptType0], type[FindingFixPromptType1]]
_FINDING_FIX_PROMPT_MODELS: _FindingFixPromptModels = (
    FindingFixPromptType0,
    FindingFixPromptType1,
)
ReviewRoutingView = ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2
_ReviewRoutingModels = tuple[
    type[ReviewRoutingViewType0],
    type[ReviewRoutingViewType1],
    type[ReviewRoutingViewType2],
]
_REVIEW_ROUTING_MODELS: _ReviewRoutingModels = (
    ReviewRoutingViewType0,
    ReviewRoutingViewType1,
    ReviewRoutingViewType2,
)


class ReviewFilters(TypedDict, total=False):
    attention: str | None
    audits: str | None
    author: str | None
    cursor: str | None
    environment: UUID | None
    findings: str | None
    kind: str | None
    limit: int | None
    query: str | None
    repository: UUID | None
    search: str | None
    status: str | None


def _decoded(
    response: Response[Any],
    expected: type[T] | _ReviewRoutingModels | _FindingFixPromptModels | _AgentSessionPromptModels,
) -> T:
    if not isinstance(response.parsed, expected):
        raise _transport.invalid_response()
    return cast(T, response.parsed)


def _configuration(
    token: str | SecretStr | None, base_url: str, timeout: float
) -> AuthenticatedClient:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("The HTTP timeout must be a finite positive number of seconds.")
    return AuthenticatedClient(
        base_url=_transport.base_url(base_url),
        token=_transport.token_value(token),
        timeout=httpx2.Timeout(timeout),
    )


def _review_url(base_url: str, organization_id: UUID, review_id: UUID) -> str:
    return (
        f"{base_url}/orgs/by-id/{quote(str(organization_id), safe='')}"
        f"/reviews/{quote(str(review_id), safe='')}"
    )


def _page_limits(page_size: int, max_pages: int, max_items: int) -> None:
    if not 1 <= page_size <= 100 or not 1 <= max_pages <= 1_000 or not 1 <= max_items <= 100_000:
        raise ValueError(
            "Pagination requires page_size 1..100, max_pages 1..1000, max_items 1..100000."
        )


def _head_commit(value: str | None) -> None:
    # Only a full SHA names one exact commit; a branch or an abbreviation does not.
    if value is not None and (
        not isinstance(value, str)
        or len(value) not in (40, 64)
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError("The head commit must be a full 40 or 64 character hexadecimal SHA.")


def _next_cursor(page: ReviewPage, seen: set[str]) -> str | None:
    if not isinstance(page.truncated, bool):
        raise _transport.invalid_response()
    if not page.truncated:
        if isinstance(page.next_cursor, str) and page.next_cursor:
            raise _transport.invalid_response()
        return None
    cursor = page.next_cursor
    if not isinstance(cursor, str) or not cursor or cursor in seen:
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-pagination",
            "The review page has no new continuation cursor.",
        )
    seen.add(cursor)
    return cursor


def _pagination_limit(resource: str = "Review") -> ProoflineError:
    return ProoflineError(
        0,
        "urn:proofline:sdk:pagination-limit",
        f"{resource} pagination reached the configured bound.",
    )


_CANCEL_REASON = "The wait was cancelled by the caller."


class _SignalDeadline:
    def __init__(self, end: float) -> None:
        self.end = end
        self.signalled_at: float | None = None
        self.conditions: tuple[threading.Condition, ...] = ()

    def record(self, now: float) -> None:
        if self.signalled_at is None and now < self.end:
            self.signalled_at = now


class _ConditionSignalTracker:
    def __init__(self, condition: threading.Condition) -> None:
        self.condition = condition
        self.original_notify_all = condition.notify_all
        self.original_notify = condition.notify
        self.deadlines: set[_SignalDeadline] = set()
        condition.notify_all = self.notify_all  # type: ignore[method-assign]
        condition.notify = self.notify  # type: ignore[method-assign]

    def record(self) -> None:
        now = monotonic()
        with _notify_lock:
            deadlines = tuple(self.deadlines)
        for deadline in deadlines:
            deadline.record(now)

    def notify_all(self) -> None:
        self.record()
        self.original_notify_all()

    def notify(self, *args: Any, **kwargs: Any) -> None:
        self.record()
        self.original_notify(*args, **kwargs)


_notify_lock = threading.Lock()
_notify_trackers: dict[int, _ConditionSignalTracker] = {}


def _thread_conditions(event: threading.Event) -> tuple[threading.Condition, ...]:
    conditions: list[threading.Condition] = []
    seen: set[int] = set()
    candidates = [getattr(event, "_cond", None), *vars(event).values()]
    for candidate in candidates:
        if isinstance(candidate, threading.Condition) and id(candidate) not in seen:
            seen.add(id(candidate))
            conditions.append(candidate)
    return tuple(conditions)


def _track_thread_signal(event: threading.Event, deadline: _SignalDeadline) -> _SignalDeadline:
    deadline.conditions = _thread_conditions(event)
    with _notify_lock:
        for condition in deadline.conditions:
            key = id(condition)
            tracker = _notify_trackers.get(key)
            if tracker is None:
                tracker = _ConditionSignalTracker(condition)
                _notify_trackers[key] = tracker
            tracker.deadlines.add(deadline)
    return deadline


def _untrack_thread_signal(event: threading.Event, deadline: _SignalDeadline) -> None:
    with _notify_lock:
        for condition in deadline.conditions:
            key = id(condition)
            tracker = _notify_trackers.get(key)
            if tracker is None:
                continue
            tracker.deadlines.discard(deadline)
            if not tracker.deadlines:
                tracker.condition.notify_all = tracker.original_notify_all  # type: ignore[method-assign]
                tracker.condition.notify = tracker.original_notify  # type: ignore[method-assign]
                del _notify_trackers[key]


def _cancelled(event: threading.Event | AsyncEvent | None) -> bool:
    return event is not None and event.is_set()


def _stopped(
    url: str,
    last: CustomerReviewDetail | None,
    review_id: UUID,
    head_commit_sha: str | None = None,
) -> ReviewOutcome:
    """Build a STOPPED outcome, validating any review and keeping its gaps."""
    if last is None:
        return ReviewOutcome("STOPPED", url, reason=_CANCEL_REASON)
    result = outcome(
        last,
        url,
        "STOPPED",
        review_id=review_id,
        head_commit_sha=head_commit_sha,
    )
    assert result is not None
    return ReviewOutcome("STOPPED", url, last, result.gaps, _CANCEL_REASON)


def _wait_for_event(
    event: threading.Event, timeout: float, deadline: _SignalDeadline | None = None
) -> bool:
    """Return True when the event woke the wait, False when it timed out."""
    if deadline is None:
        return event.wait(timeout)
    conditions = deadline.conditions
    if conditions:
        # Install the tracker and check the flag under the same condition lock,
        # so a set/clear between the check and waiter registration is recorded.
        with conditions[0]:
            _track_thread_signal(event, deadline)
            if deadline.signalled_at is not None:
                return True
            if getattr(event, "_flag", False) is True:
                deadline.record(monotonic())
                return True
    now = monotonic()
    remaining = min(timeout, deadline.end - now)
    if remaining <= 0:
        return False
    woke = event.wait(remaining)
    if woke and deadline.signalled_at is None:
        # A subclass may notify through a primitive we cannot observe. A
        # successful wait is evidence that its signal reached the wait primitive
        # after this call began, which is before the absolute cutoff.
        deadline.record(now)
    return woke


async def _async_wait_for_event(event: AsyncEvent, cutoff: float) -> bool:
    """Return True when the event is signalled before cutoff, False on timeout."""
    loop = async_get_running_loop()
    if monotonic() >= cutoff:
        return False
    timer: AsyncFuture[None] = loop.create_future()
    handle = loop.call_at(loop.time() + max(0.0, cutoff - monotonic()), timer.set_result, None)
    delivered = event.is_set() and monotonic() < cutoff
    waiter: Any = None
    future: AsyncFuture[Any] | None = None
    original_set_result: Any = None
    started = False
    resumed = False
    try:
        # Drive the event's public wait() coroutine directly. It honors
        # subclasses that delegate to a backing event while still letting us
        # observe the future that carries the signal.
        waiter = event.wait()
        started = True
        try:
            awaited = waiter.send(None)
        except StopIteration as stop:
            resumed = True
            if stop.value and monotonic() < cutoff:
                delivered = True
            return delivered
        except BaseException:
            # A coroutine that raises during startup is already closed.
            resumed = True
            raise
        future = cast(AsyncFuture[Any], awaited)
        original_set_result = future.set_result

        def set_result(result: Any) -> None:
            nonlocal delivered
            if monotonic() < cutoff:
                delivered = True
            original_set_result(result)

        future.set_result = set_result  # type: ignore[method-assign]
        await async_wait((future, timer), return_when=FIRST_COMPLETED)
        if future.done():
            # Mark this before resuming: a failed send closes the coroutine, and
            # cleanup must not throw into it again.
            resumed = True
            try:
                waiter.send(None)
            except (StopIteration, AsyncCancelledError):
                pass
        return delivered
    finally:
        handle.cancel()
        if future is not None and original_set_result is not None:
            future.set_result = original_set_result  # type: ignore[method-assign]
        if waiter is not None:
            if started and not resumed:
                if future is not None and not future.done():
                    future.cancel()
                try:
                    waiter.throw(AsyncCancelledError())
                except (StopIteration, AsyncCancelledError):
                    pass
            if future is not None and future.done() and not future.cancelled():
                try:
                    future.exception()
                except AsyncCancelledError:
                    pass
            waiter.close()


def _cancel_end(delay: float, cutoff: float | None) -> float:
    end = monotonic() + delay
    return min(end, cutoff) if cutoff is not None else end


def _sleep_with_cancel(
    delay: float, event: threading.Event | None, cutoff: float | None = None
) -> bool:
    """Wait on the event until the delay or cutoff, returning False if cancelled."""
    if event is None:
        sleep(delay)
        return True
    end = _cancel_end(delay, cutoff)
    deadline = _track_thread_signal(event, _SignalDeadline(end))
    try:
        while True:
            if deadline.signalled_at is not None:
                return False
            now = monotonic()
            if now >= end:
                return True
            if _cancelled(event):
                # Read the flag before the final cutoff check: a signal at or
                # after the cutoff cannot turn a timeout into a stop.
                if monotonic() < end:
                    deadline.record(monotonic())
                    return False
                return True
            if not _wait_for_event(event, end - now, deadline):
                if deadline.signalled_at is not None:
                    return False
                if monotonic() < end and _cancelled(event):
                    deadline.record(monotonic())
                    return False
                return True
    finally:
        _untrack_thread_signal(event, deadline)


async def _async_sleep_with_cancel(
    delay: float, event: AsyncEvent | None, cutoff: float | None = None
) -> bool:
    if event is None:
        await async_sleep(delay)
        return True
    end = _cancel_end(delay, cutoff)
    while True:
        if monotonic() >= end:
            return True
        if await _async_wait_for_event(event, end):
            return False
        if monotonic() >= end:
            return True


def _export_page_limit(max_pages: int) -> None:
    if isinstance(max_pages, bool) or not isinstance(max_pages, int) or not 1 <= max_pages <= 1_000:
        raise ValueError("Export pagination requires max_pages 1..1000.")


def _export_next_cursor(page: ExportPage, seen: set[str]) -> str | None:
    cursor = page.next_cursor
    if cursor is None:
        return None
    if not cursor or cursor in seen:
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-pagination",
            "The export page has no new continuation cursor.",
        )
    seen.add(cursor)
    return cursor


class ProoflineClient(Operations):
    """Synchronous typed HTTP operations.

    Name resolution, connection, TLS and socket operations stop at the configured
    HTTP timeout and at a wait deadline.
    """

    def __init__(
        self,
        token: str | SecretStr | None = None,
        *,
        base_url: str = "https://proofline.sh",
        timeout: float = 30,
    ) -> None:
        self._api = _configuration(token, base_url, timeout)
        self._base_url = _transport.base_url(base_url)
        self._http = httpx2.Client(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx2.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.RetryTransport(self._api.token, timeout),
        )
        self._api.set_httpx_client(self._http)
        self.mcp = McpClient(self._http)
        self.knowledge = KnowledgeClient(self._http)
        self.fixes = FixesClient(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _call(
        self,
        operation: Callable[..., Response[Any]],
        expected: type[T]
        | _ReviewRoutingModels
        | _FindingFixPromptModels
        | _AgentSessionPromptModels,
        *args: object,
        **kwargs: object,
    ) -> T:
        with _transport.operation_errors():
            return _decoded(operation(*args, client=self._api, **kwargs), expected)

    def export_reviews(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
    ) -> ExportPage:
        """Read one export page. Repeat with next_cursor and the same filters."""
        if dataset not in (
            "reviews",
            "finding_outcomes",
            "finding_validations",
            "spend",
            "findings",
        ):
            raise ValueError("Unknown export dataset.")
        if format not in ("csv", "ndjson"):
            raise ValueError("Export format must be csv or ndjson.")
        params = {"from": from_time, "to": to_time, "format": format}
        if cursor is not None:
            params["cursor"] = cursor
        if group_by is not None:
            params["group_by"] = group_by
        try:
            response = self._http.get(
                f"/api/v1/organizations/{organization_id}/exports/{dataset}",
                params=params,
                headers={"Accept": "text/csv" if format == "csv" else "application/x-ndjson"},
            )
            return decode_export(response, format, dataset)
        except httpx2.HTTPError as error:
            raise _transport.network_error(error) from None

    def iter_export_pages(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
        max_pages: int = 100,
    ) -> Iterator[ExportPage]:
        """Stream export pages, refusing cursor cycles and incomplete bounded traversals."""
        _export_page_limit(max_pages)
        seen = {cursor} if cursor is not None else set()
        for _ in range(max_pages):
            page = self.export_reviews(
                organization_id,
                dataset,
                from_time=from_time,
                to_time=to_time,
                format=format,
                cursor=cursor,
                group_by=group_by,
            )
            cursor = _export_next_cursor(page, seen)
            yield page
            if cursor is None:
                return
        raise _pagination_limit("Export")

    def list_reviews(self, organization_id: UUID, **filters: Unpack[ReviewFilters]) -> ReviewPage:
        return self._call(list_reviews.sync_detailed, ReviewPage, organization_id, **filters)

    def list_pull_request_reviews(
        self,
        organization_id: UUID,
        repository: str,
        pull_request_number: int,
        *,
        filters: ReviewFilters | None = None,
    ) -> ReviewPage:
        params = dict(filters or {})
        params["repository_query"] = params.pop("repository", None)
        return self._call(
            list_pull_request_reviews.sync_detailed,
            ReviewPage,
            organization_id,
            repository,
            pull_request_number,
            **params,
        )

    def get_pull_request_review(
        self, organization_id: UUID, repository: str, pull_request_number: int, run_number: int
    ) -> CustomerReviewDetail:
        return self._call(
            get_pull_request_review.sync_detailed,
            CustomerReviewDetail,
            organization_id,
            repository,
            pull_request_number,
            run_number,
        )

    def get_deployment_review(self, organization_id: UUID, public_key: str) -> CustomerReviewDetail:
        return self._call(
            get_deployment_review.sync_detailed, CustomerReviewDetail, organization_id, public_key
        )

    def get_review(self, organization_id: UUID, review_id: UUID) -> CustomerReviewDetail:
        return self._call(
            get_review.sync_detailed, CustomerReviewDetail, organization_id, review_id
        )

    def get_review_routing(self, organization_id: UUID, review_id: UUID) -> ReviewRoutingView:
        return self._call(
            get_review_routing.sync_detailed,
            _REVIEW_ROUTING_MODELS,
            organization_id,
            review_id,
        )

    def get_assessment(
        self, organization_id: UUID, review_id: UUID, assessment_id: UUID
    ) -> CustomerAssessmentDetail:
        return self._call(
            get_assessment.sync_detailed,
            CustomerAssessmentDetail,
            organization_id,
            review_id,
            assessment_id,
        )

    def get_finding(self, organization_id: UUID, finding_id: UUID) -> CustomerFinding:
        return self._call(get_finding.sync_detailed, CustomerFinding, organization_id, finding_id)

    def get_agent_session(self, organization_id: UUID, session_id: UUID) -> AgentSession:
        return self._call(
            get_agent_session.sync_detailed, AgentSession, organization_id, session_id
        )

    def get_agent_session_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> AgentSessionPrompt:
        return self._call(
            get_agent_session_prompt.sync_detailed,
            _AGENT_SESSION_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    def start_agent_session(
        self, organization_id: UUID, finding_id: UUID, *, body: StartSession
    ) -> AgentSession:
        return self._call(
            start_agent_session.sync_detailed, AgentSession, organization_id, finding_id, body=body
        )

    def get_finding_fix_prompt(self, organization_id: UUID, finding_id: UUID) -> FindingFixPrompt:
        return self._call(
            get_finding_fix_prompt.sync_detailed,
            _FINDING_FIX_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    def get_review_guidance(self, organization_id: UUID, repository_id: UUID) -> RepositoryGuidance:
        return self._call(
            get_review_guidance.sync_detailed, RepositoryGuidance, organization_id, repository_id
        )

    def list_repositories(self, organization_id: UUID) -> RepositoryNames:
        return self._call(list_repositories.sync_detailed, RepositoryNames, organization_id)

    def request_review(
        self,
        organization_id: UUID,
        repository_id: UUID,
        pull_request_number: int,
        *,
        body: RunNowRequest | Unset = UNSET,
    ) -> RunNowResponse:
        return self._call(
            request_review.sync_detailed,
            RunNowResponse,
            organization_id,
            repository_id,
            pull_request_number,
            body=body,
        )

    def request_patch_review(
        self, organization_id: UUID, repository_id: UUID, *, body: PatchReviewRequest
    ) -> PatchReviewResponse:
        return self._call(
            request_patch_review.sync_detailed,
            PatchReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def upload_coverage_reports(
        self, organization_id: UUID, repository_id: UUID, *, body: CoverageUploadRequest
    ) -> CoverageUploadResponse:
        return self._call(
            upload_coverage_reports.sync_detailed,
            CoverageUploadResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def request_file_review(
        self, organization_id: UUID, repository_id: UUID, *, body: FileReviewRequest
    ) -> FileReviewResponse:
        return self._call(
            request_file_review.sync_detailed,
            FileReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def stop_review(self, organization_id: UUID, review_id: UUID) -> StopResponse:
        return self._call(stop_review.sync_detailed, StopResponse, organization_id, review_id)

    def request_commit_review(
        self, organization_id: UUID, repository_id: UUID, *, body: CommitReviewRequest
    ) -> CommitReviewResponse:
        return self._call(
            request_commit_review.sync_detailed,
            CommitReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def rerun_review(self, organization_id: UUID, review_id: UUID) -> RerunResponse:
        return self._call(rerun_review.sync_detailed, RerunResponse, organization_id, review_id)

    def iter_reviews(
        self,
        organization_id: UUID,
        *,
        page_size: int = 100,
        max_pages: int = 100,
        max_items: int = 10_000,
        filters: ReviewFilters | None = None,
    ) -> Iterator[ReviewSummary]:
        _page_limits(page_size, max_pages, max_items)
        params: ReviewFilters = {}
        if filters:
            params.update(filters)
        params["limit"] = page_size
        seen: set[str] = set()
        cursor = params.get("cursor")
        if cursor:
            seen.add(cursor)
        count = 0
        for _ in range(max_pages):
            page = self.list_reviews(organization_id, **params)
            for item in page.items:
                if count == max_items:
                    raise _pagination_limit()
                yield item
                count += 1
            cursor = _next_cursor(page, seen)
            if cursor is None:
                return
            params["cursor"] = cursor
        raise _pagination_limit()

    def wait_for_review(
        self,
        organization_id: UUID,
        review_id: UUID,
        *,
        timeout: float = 300,
        head_commit_sha: str | None = None,
        cancel_event: threading.Event | None = None,
    ) -> ReviewOutcome:
        """Wait for recorded review completion or return TIMED_OUT.

        A name lookup still running at the deadline returns TIMED_OUT; it never
        reports completion.

        head_commit_sha holds the outcome to that commit. A review pinned to
        another head ends the wait on that read and is never COMPLETED.

        cancel_event stops the wait before another request. It is checked before
        each poll, during the backoff, and after each read. An in-flight read is
        not interrupted: cancellation waits for that read to finish, including
        transport retries and their delays. Those delays count toward the overall
        wait deadline rather than a single HTTP timeout.
        """

        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        _head_commit(head_commit_sha)
        if cancel_event is not None and not isinstance(cancel_event, threading.Event):
            raise TypeError("cancel_event must be a threading.Event.")
        url = _review_url(self._base_url, organization_id, review_id)
        if _cancelled(cancel_event):
            return _stopped(url, None, review_id, head_commit_sha)
        last: CustomerReviewDetail | None = None
        deadline_at = monotonic() + timeout
        deadline = _transport.DEADLINE.set(deadline_at)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                if _cancelled(cancel_event):
                    return _stopped(url, last, review_id, head_commit_sha)
                try:
                    last = self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if _cancelled(cancel_event):
                        return _stopped(url, last, review_id, head_commit_sha)
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if _cancelled(cancel_event):
                    return _stopped(url, last, review_id, head_commit_sha)
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id, head_commit_sha=head_commit_sha)
                if result is not None:
                    return result
                remaining = _transport.remaining() or 0
                if not _sleep_with_cancel(min(interval, remaining), cancel_event, deadline_at):
                    return _stopped(url, last, review_id, head_commit_sha)
                interval = min(60, interval * 2)
            if (_transport.remaining() or 0) > 0 and _cancelled(cancel_event):
                return _stopped(url, last, review_id, head_commit_sha)
            timed_out = outcome(last, url, "TIMED_OUT", head_commit_sha=head_commit_sha)
            return timed_out or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)


class AsyncProoflineClient(AsyncOperations):
    def __init__(
        self,
        token: str | SecretStr | None = None,
        *,
        base_url: str = "https://proofline.sh",
        timeout: float = 30,
    ) -> None:
        self._api = _configuration(token, base_url, timeout)
        self._base_url = _transport.base_url(base_url)
        self._http = httpx2.AsyncClient(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx2.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.AsyncRetryTransport(self._api.token, timeout),
        )
        self._api.set_async_httpx_client(self._http)
        self.mcp = AsyncMcpClient(self._http)
        self.knowledge = AsyncKnowledgeClient(self._http)
        self.fixes = AsyncFixesClient(self._http)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _call(
        self,
        operation: Callable[..., Awaitable[Response[Any]]],
        expected: type[T]
        | _ReviewRoutingModels
        | _FindingFixPromptModels
        | _AgentSessionPromptModels,
        *args: object,
        **kwargs: object,
    ) -> T:
        with _transport.operation_errors():
            return _decoded(await operation(*args, client=self._api, **kwargs), expected)

    async def export_reviews(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
    ) -> ExportPage:
        """Read one export page. Repeat with next_cursor and the same filters."""
        if dataset not in (
            "reviews",
            "finding_outcomes",
            "finding_validations",
            "spend",
            "findings",
        ):
            raise ValueError("Unknown export dataset.")
        if format not in ("csv", "ndjson"):
            raise ValueError("Export format must be csv or ndjson.")
        params = {"from": from_time, "to": to_time, "format": format}
        if cursor is not None:
            params["cursor"] = cursor
        if group_by is not None:
            params["group_by"] = group_by
        try:
            response = await self._http.get(
                f"/api/v1/organizations/{organization_id}/exports/{dataset}",
                params=params,
                headers={"Accept": "text/csv" if format == "csv" else "application/x-ndjson"},
            )
            return decode_export(response, format, dataset)
        except httpx2.HTTPError as error:
            raise _transport.network_error(error) from None

    async def iter_export_pages(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
        max_pages: int = 100,
    ) -> AsyncIterator[ExportPage]:
        """Stream export pages, refusing cursor cycles and incomplete bounded traversals."""
        _export_page_limit(max_pages)
        seen = {cursor} if cursor is not None else set()
        for _ in range(max_pages):
            page = await self.export_reviews(
                organization_id,
                dataset,
                from_time=from_time,
                to_time=to_time,
                format=format,
                cursor=cursor,
                group_by=group_by,
            )
            cursor = _export_next_cursor(page, seen)
            yield page
            if cursor is None:
                return
        raise _pagination_limit("Export")

    async def list_reviews(
        self, organization_id: UUID, **filters: Unpack[ReviewFilters]
    ) -> ReviewPage:
        return await self._call(
            list_reviews.asyncio_detailed, ReviewPage, organization_id, **filters
        )

    async def list_pull_request_reviews(
        self,
        organization_id: UUID,
        repository: str,
        pull_request_number: int,
        *,
        filters: ReviewFilters | None = None,
    ) -> ReviewPage:
        params = dict(filters or {})
        params["repository_query"] = params.pop("repository", None)
        return await self._call(
            list_pull_request_reviews.asyncio_detailed,
            ReviewPage,
            organization_id,
            repository,
            pull_request_number,
            **params,
        )

    async def get_pull_request_review(
        self, organization_id: UUID, repository: str, pull_request_number: int, run_number: int
    ) -> CustomerReviewDetail:
        return await self._call(
            get_pull_request_review.asyncio_detailed,
            CustomerReviewDetail,
            organization_id,
            repository,
            pull_request_number,
            run_number,
        )

    async def get_deployment_review(
        self, organization_id: UUID, public_key: str
    ) -> CustomerReviewDetail:
        return await self._call(
            get_deployment_review.asyncio_detailed,
            CustomerReviewDetail,
            organization_id,
            public_key,
        )

    async def get_review(self, organization_id: UUID, review_id: UUID) -> CustomerReviewDetail:
        return await self._call(
            get_review.asyncio_detailed, CustomerReviewDetail, organization_id, review_id
        )

    async def get_review_routing(self, organization_id: UUID, review_id: UUID) -> ReviewRoutingView:
        return await self._call(
            get_review_routing.asyncio_detailed,
            _REVIEW_ROUTING_MODELS,
            organization_id,
            review_id,
        )

    async def get_assessment(
        self, organization_id: UUID, review_id: UUID, assessment_id: UUID
    ) -> CustomerAssessmentDetail:
        return await self._call(
            get_assessment.asyncio_detailed,
            CustomerAssessmentDetail,
            organization_id,
            review_id,
            assessment_id,
        )

    async def get_finding(self, organization_id: UUID, finding_id: UUID) -> CustomerFinding:
        return await self._call(
            get_finding.asyncio_detailed, CustomerFinding, organization_id, finding_id
        )

    async def get_agent_session(self, organization_id: UUID, session_id: UUID) -> AgentSession:
        return await self._call(
            get_agent_session.asyncio_detailed, AgentSession, organization_id, session_id
        )

    async def get_agent_session_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> AgentSessionPrompt:
        return await self._call(
            get_agent_session_prompt.asyncio_detailed,
            _AGENT_SESSION_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    async def start_agent_session(
        self, organization_id: UUID, finding_id: UUID, *, body: StartSession
    ) -> AgentSession:
        return await self._call(
            start_agent_session.asyncio_detailed,
            AgentSession,
            organization_id,
            finding_id,
            body=body,
        )

    async def get_finding_fix_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> FindingFixPrompt:
        return await self._call(
            get_finding_fix_prompt.asyncio_detailed,
            _FINDING_FIX_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    async def get_review_guidance(
        self, organization_id: UUID, repository_id: UUID
    ) -> RepositoryGuidance:
        return await self._call(
            get_review_guidance.asyncio_detailed, RepositoryGuidance, organization_id, repository_id
        )

    async def list_repositories(self, organization_id: UUID) -> RepositoryNames:
        return await self._call(
            list_repositories.asyncio_detailed, RepositoryNames, organization_id
        )

    async def request_review(
        self,
        organization_id: UUID,
        repository_id: UUID,
        pull_request_number: int,
        *,
        body: RunNowRequest | Unset = UNSET,
    ) -> RunNowResponse:
        return await self._call(
            request_review.asyncio_detailed,
            RunNowResponse,
            organization_id,
            repository_id,
            pull_request_number,
            body=body,
        )

    async def request_patch_review(
        self, organization_id: UUID, repository_id: UUID, *, body: PatchReviewRequest
    ) -> PatchReviewResponse:
        return await self._call(
            request_patch_review.asyncio_detailed,
            PatchReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def upload_coverage_reports(
        self, organization_id: UUID, repository_id: UUID, *, body: CoverageUploadRequest
    ) -> CoverageUploadResponse:
        return await self._call(
            upload_coverage_reports.asyncio_detailed,
            CoverageUploadResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def request_file_review(
        self, organization_id: UUID, repository_id: UUID, *, body: FileReviewRequest
    ) -> FileReviewResponse:
        return await self._call(
            request_file_review.asyncio_detailed,
            FileReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def stop_review(self, organization_id: UUID, review_id: UUID) -> StopResponse:
        return await self._call(
            stop_review.asyncio_detailed, StopResponse, organization_id, review_id
        )

    async def request_commit_review(
        self, organization_id: UUID, repository_id: UUID, *, body: CommitReviewRequest
    ) -> CommitReviewResponse:
        return await self._call(
            request_commit_review.asyncio_detailed,
            CommitReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def rerun_review(self, organization_id: UUID, review_id: UUID) -> RerunResponse:
        return await self._call(
            rerun_review.asyncio_detailed, RerunResponse, organization_id, review_id
        )

    async def iter_reviews(
        self,
        organization_id: UUID,
        *,
        page_size: int = 100,
        max_pages: int = 100,
        max_items: int = 10_000,
        filters: ReviewFilters | None = None,
    ) -> AsyncIterator[ReviewSummary]:
        _page_limits(page_size, max_pages, max_items)
        params: ReviewFilters = {}
        if filters:
            params.update(filters)
        params["limit"] = page_size
        seen: set[str] = set()
        cursor = params.get("cursor")
        if cursor:
            seen.add(cursor)
        count = 0
        for _ in range(max_pages):
            page = await self.list_reviews(organization_id, **params)
            for item in page.items:
                if count == max_items:
                    raise _pagination_limit()
                yield item
                count += 1
            cursor = _next_cursor(page, seen)
            if cursor is None:
                return
            params["cursor"] = cursor
        raise _pagination_limit()

    async def wait_for_review(
        self,
        organization_id: UUID,
        review_id: UUID,
        *,
        timeout: float = 300,
        head_commit_sha: str | None = None,
        cancel_event: AsyncEvent | None = None,
    ) -> ReviewOutcome:
        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        _head_commit(head_commit_sha)
        if cancel_event is not None and not isinstance(cancel_event, AsyncEvent):
            raise TypeError("cancel_event must be an asyncio.Event.")
        url = _review_url(self._base_url, organization_id, review_id)
        if _cancelled(cancel_event):
            return _stopped(url, None, review_id, head_commit_sha)
        last: CustomerReviewDetail | None = None
        deadline_at = monotonic() + timeout
        deadline = _transport.DEADLINE.set(deadline_at)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                if _cancelled(cancel_event):
                    return _stopped(url, last, review_id, head_commit_sha)
                try:
                    last = await self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if _cancelled(cancel_event):
                        return _stopped(url, last, review_id, head_commit_sha)
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if _cancelled(cancel_event):
                    return _stopped(url, last, review_id, head_commit_sha)
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id, head_commit_sha=head_commit_sha)
                if result is not None:
                    return result
                remaining = _transport.remaining() or 0
                if not await _async_sleep_with_cancel(
                    min(interval, remaining), cancel_event, deadline_at
                ):
                    return _stopped(url, last, review_id, head_commit_sha)
                interval = min(60, interval * 2)
            if (_transport.remaining() or 0) > 0 and _cancelled(cancel_event):
                return _stopped(url, last, review_id, head_commit_sha)
            timed_out = outcome(last, url, "TIMED_OUT", head_commit_sha=head_commit_sha)
            return timed_out or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)
