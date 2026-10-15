from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.repository_guidance import RepositoryGuidance
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/review-guidance".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | RepositoryGuidance:
    if response.status_code == 200:
        response_200 = RepositoryGuidance.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | RepositoryGuidance]:
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
) -> Response[Problem | RepositoryGuidance]:
    """Get repository review guidance

     Returns the review guidance configured for a repository, for tools and coding agents that read it
    before writing code.

    Args:
        org_id (UUID):
        repo_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RepositoryGuidance]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
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
) -> Problem | RepositoryGuidance | None:
    """Get repository review guidance

     Returns the review guidance configured for a repository, for tools and coding agents that read it
    before writing code.

    Args:
        org_id (UUID):
        repo_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RepositoryGuidance
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Problem | RepositoryGuidance]:
    """Get repository review guidance

     Returns the review guidance configured for a repository, for tools and coding agents that read it
    before writing code.

    Args:
        org_id (UUID):
        repo_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RepositoryGuidance]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Problem | RepositoryGuidance | None:
    """Get repository review guidance

     Returns the review guidance configured for a repository, for tools and coding agents that read it
    before writing code.

    Args:
        org_id (UUID):
        repo_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RepositoryGuidance
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            client=client,
        )
    ).parsed
