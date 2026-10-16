from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.stop_response import StopResponse
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    review_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/reviews/{review_id}/stop".format(
            org_id=quote(str(org_id), safe=""),
            review_id=quote(str(review_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | StopResponse:
    if response.status_code == 200:
        response_200 = StopResponse.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | StopResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    review_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Problem | StopResponse]:
    """Stop your local review

     Stops the holder's own pending or running withheld patch, commit or named-file review. Requires a
    personal or CLI device token with live GitHub read access to the review's repository. Organization,
    CI job and MCP OAuth tokens cannot stop reviews. The stopped review retains its findings and exact
    code identity; requesting the same input returns that stopped review.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | StopResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        review_id=review_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    review_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Problem | StopResponse | None:
    """Stop your local review

     Stops the holder's own pending or running withheld patch, commit or named-file review. Requires a
    personal or CLI device token with live GitHub read access to the review's repository. Organization,
    CI job and MCP OAuth tokens cannot stop reviews. The stopped review retains its findings and exact
    code identity; requesting the same input returns that stopped review.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | StopResponse
    """

    return sync_detailed(
        org_id=org_id,
        review_id=review_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    review_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Problem | StopResponse]:
    """Stop your local review

     Stops the holder's own pending or running withheld patch, commit or named-file review. Requires a
    personal or CLI device token with live GitHub read access to the review's repository. Organization,
    CI job and MCP OAuth tokens cannot stop reviews. The stopped review retains its findings and exact
    code identity; requesting the same input returns that stopped review.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | StopResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        review_id=review_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    review_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Problem | StopResponse | None:
    """Stop your local review

     Stops the holder's own pending or running withheld patch, commit or named-file review. Requires a
    personal or CLI device token with live GitHub read access to the review's repository. Organization,
    CI job and MCP OAuth tokens cannot stop reviews. The stopped review retains its findings and exact
    code identity; requesting the same input returns that stopped review.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | StopResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            review_id=review_id,
            client=client,
        )
    ).parsed
