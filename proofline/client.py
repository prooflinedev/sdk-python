"""Small sync and async facades over the generated review operations."""

from __future__ import annotations

import math
from asyncio import sleep as async_sleep
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from time import monotonic, sleep
from types import TracebackType
from typing import Any, Self, TypedDict, TypeVar, Unpack, cast
from urllib.parse import quote
from uuid import UUID

import httpx
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
    author: str | None
    cursor: str | None
    environment: UUID | None
    findings: str | None
    kind: str | None
    limit: int | None
    repository: UUID | None
    search: str | None
    status: str | None


def _decoded(
    response: Response[Any],
    expected: type[T] | _ReviewRoutingModels | _FindingFixPromptModels | _AgentSessionPromptModels,
) -> T:
    if not isinstance(response.parsed, expected):
        raise _malformed()
    return cast(T, response.parsed)


def _malformed() -> ProoflineError:
    return ProoflineError(
        0, "urn:proofline:sdk:invalid-response", "Proofline returned an invalid API response."
    )


def _network(error: httpx.HTTPError) -> ProoflineError:
    if isinstance(error, httpx.TimeoutException):
        return _transport.timeout_error()
    return ProoflineError(
        0, "urn:proofline:sdk:transport-unavailable", "Could not reach the Proofline API."
    )


def _configuration(
    token: str | SecretStr | None, base_url: str, timeout: float
) -> AuthenticatedClient:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("The HTTP timeout must be a finite positive number of seconds.")
    return AuthenticatedClient(
        base_url=_transport.base_url(base_url),
        token=_transport.token_value(token),
        timeout=httpx.Timeout(timeout),
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


def _next_cursor(page: ReviewPage, seen: set[str]) -> str | None:
    if not isinstance(page.truncated, bool):
        raise _malformed()
    if not page.truncated:
        if isinstance(page.next_cursor, str) and page.next_cursor:
            raise _malformed()
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


def _pagination_limit() -> ProoflineError:
    return ProoflineError(
        0, "urn:proofline:sdk:pagination-limit", "Review pagination reached the configured bound."
    )


class ProoflineClient:
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
        self._http = httpx.Client(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.RetryTransport(self._api.token, timeout),
        )
        self._api.set_httpx_client(self._http)
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
        try:
            return _decoded(operation(*args, client=self._api, **kwargs), expected)
        except ProoflineError:
            raise
        except httpx.HTTPError as error:
            raise _network(error) from None
        except Exception:
            raise _malformed() from None

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
            return decode_export(response, format)
        except httpx.HTTPError as error:
            raise _network(error) from None

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
        self, organization_id: UUID, review_id: UUID, *, timeout: float = 300
    ) -> ReviewOutcome:
        """Wait for recorded review completion or return TIMED_OUT.

        A name lookup still running at the deadline returns TIMED_OUT; it never
        reports completion.
        """

        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        url = _review_url(self._base_url, organization_id, review_id)
        last: CustomerReviewDetail | None = None
        deadline = _transport.DEADLINE.set(monotonic() + timeout)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                try:
                    last = self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id)
                if result is not None:
                    return result
                sleep(min(interval, _transport.remaining() or 0))
                interval = min(60, interval * 2)
            return outcome(last, url, "TIMED_OUT") or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)


class AsyncProoflineClient:
    def __init__(
        self,
        token: str | SecretStr | None = None,
        *,
        base_url: str = "https://proofline.sh",
        timeout: float = 30,
    ) -> None:
        self._api = _configuration(token, base_url, timeout)
        self._base_url = _transport.base_url(base_url)
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.AsyncRetryTransport(self._api.token, timeout),
        )
        self._api.set_async_httpx_client(self._http)
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
        try:
            return _decoded(await operation(*args, client=self._api, **kwargs), expected)
        except ProoflineError:
            raise
        except httpx.HTTPError as error:
            raise _network(error) from None
        except Exception:
            raise _malformed() from None

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
            return decode_export(response, format)
        except httpx.HTTPError as error:
            raise _network(error) from None

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
        self, organization_id: UUID, review_id: UUID, *, timeout: float = 300
    ) -> ReviewOutcome:
        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        url = _review_url(self._base_url, organization_id, review_id)
        last: CustomerReviewDetail | None = None
        deadline = _transport.DEADLINE.set(monotonic() + timeout)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                try:
                    last = await self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id)
                if result is not None:
                    return result
                await async_sleep(min(interval, _transport.remaining() or 0))
                interval = min(60, interval * 2)
            return outcome(last, url, "TIMED_OUT") or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)
