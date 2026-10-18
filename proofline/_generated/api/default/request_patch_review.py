from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.patch_review_request import PatchReviewRequest
from ...models.patch_review_response import PatchReviewResponse
from ...models.problem import Problem
from ...models.run_now_refused import RunNowRefused
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    *,
    body: PatchReviewRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/patch-reviews".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchReviewResponse | Problem | RunNowRefused:
    if response.status_code == 200:
        response_200 = PatchReviewResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = RunNowRefused.from_dict(response.json())

        return response_400

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchReviewResponse | Problem | RunNowRefused]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: PatchReviewRequest,
) -> Response[PatchReviewResponse | Problem | RunNowRefused]:
    """Review local changes

     Reviews a unified diff against a commit GitHub has in the repository, and returns that patch's
    review when one exists. The review reads only that commit and the patch, and is never posted to a
    pull request. With `verify_finding_ids`, the review also re-verifies those open findings of one pull
    request against the patch and reports each outcome on the review, without changing the pull
    request's findings. Requires live GitHub read access; the same patch on the same base, re-verifying
    the same findings, always returns the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (PatchReviewRequest): Local changes to review: a unified diff against a commit GitHub
            has.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchReviewResponse | Problem | RunNowRefused]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: PatchReviewRequest,
) -> PatchReviewResponse | Problem | RunNowRefused | None:
    """Review local changes

     Reviews a unified diff against a commit GitHub has in the repository, and returns that patch's
    review when one exists. The review reads only that commit and the patch, and is never posted to a
    pull request. With `verify_finding_ids`, the review also re-verifies those open findings of one pull
    request against the patch and reports each outcome on the review, without changing the pull
    request's findings. Requires live GitHub read access; the same patch on the same base, re-verifying
    the same findings, always returns the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (PatchReviewRequest): Local changes to review: a unified diff against a commit GitHub
            has.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchReviewResponse | Problem | RunNowRefused
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: PatchReviewRequest,
) -> Response[PatchReviewResponse | Problem | RunNowRefused]:
    """Review local changes

     Reviews a unified diff against a commit GitHub has in the repository, and returns that patch's
    review when one exists. The review reads only that commit and the patch, and is never posted to a
    pull request. With `verify_finding_ids`, the review also re-verifies those open findings of one pull
    request against the patch and reports each outcome on the review, without changing the pull
    request's findings. Requires live GitHub read access; the same patch on the same base, re-verifying
    the same findings, always returns the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (PatchReviewRequest): Local changes to review: a unified diff against a commit GitHub
            has.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchReviewResponse | Problem | RunNowRefused]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: PatchReviewRequest,
) -> PatchReviewResponse | Problem | RunNowRefused | None:
    """Review local changes

     Reviews a unified diff against a commit GitHub has in the repository, and returns that patch's
    review when one exists. The review reads only that commit and the patch, and is never posted to a
    pull request. With `verify_finding_ids`, the review also re-verifies those open findings of one pull
    request against the patch and reports each outcome on the review, without changing the pull
    request's findings. Requires live GitHub read access; the same patch on the same base, re-verifying
    the same findings, always returns the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (PatchReviewRequest): Local changes to review: a unified diff against a commit GitHub
            has.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchReviewResponse | Problem | RunNowRefused
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
