from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.commit_review_request import CommitReviewRequest
from ...models.commit_review_response import CommitReviewResponse
from ...models.problem import Problem
from ...models.run_now_refused import RunNowRefused
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    *,
    body: CommitReviewRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/commit-reviews".format(
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
) -> CommitReviewResponse | Problem | RunNowRefused:
    if response.status_code == 200:
        response_200 = CommitReviewResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = RunNowRefused.from_dict(response.json())

        return response_400

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CommitReviewResponse | Problem | RunNowRefused]:
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
    body: CommitReviewRequest,
) -> Response[CommitReviewResponse | Problem | RunNowRefused]:
    """Review pushed commits

     Reviews the change from an exact base commit to an exact head commit, both of which GitHub has in
    the repository, and returns those commits' review when one exists. The base must be an ancestor of
    the head. The review reads only those two commits, and is never posted to a pull request. Requires
    live GitHub read access; the same commits always return the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CommitReviewRequest): Pushed commits to review: the exact base the change is
            compared with and
             the exact head it ends at.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommitReviewResponse | Problem | RunNowRefused]
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
    body: CommitReviewRequest,
) -> CommitReviewResponse | Problem | RunNowRefused | None:
    """Review pushed commits

     Reviews the change from an exact base commit to an exact head commit, both of which GitHub has in
    the repository, and returns those commits' review when one exists. The base must be an ancestor of
    the head. The review reads only those two commits, and is never posted to a pull request. Requires
    live GitHub read access; the same commits always return the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CommitReviewRequest): Pushed commits to review: the exact base the change is
            compared with and
             the exact head it ends at.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommitReviewResponse | Problem | RunNowRefused
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
    body: CommitReviewRequest,
) -> Response[CommitReviewResponse | Problem | RunNowRefused]:
    """Review pushed commits

     Reviews the change from an exact base commit to an exact head commit, both of which GitHub has in
    the repository, and returns those commits' review when one exists. The base must be an ancestor of
    the head. The review reads only those two commits, and is never posted to a pull request. Requires
    live GitHub read access; the same commits always return the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CommitReviewRequest): Pushed commits to review: the exact base the change is
            compared with and
             the exact head it ends at.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommitReviewResponse | Problem | RunNowRefused]
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
    body: CommitReviewRequest,
) -> CommitReviewResponse | Problem | RunNowRefused | None:
    """Review pushed commits

     Reviews the change from an exact base commit to an exact head commit, both of which GitHub has in
    the repository, and returns those commits' review when one exists. The base must be an ancestor of
    the head. The review reads only those two commits, and is never posted to a pull request. Requires
    live GitHub read access; the same commits always return the same review.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CommitReviewRequest): Pushed commits to review: the exact base the change is
            compared with and
             the exact head it ends at.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommitReviewResponse | Problem | RunNowRefused
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
