from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.customer_review_detail import CustomerReviewDetail
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repository: str,
    pull_request_number: int,
    run_number: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/reviews/pr/{repository}/{pull_request_number}/runs/{run_number}".format(
            org_id=quote(str(org_id), safe=""),
            repository=quote(str(repository), safe=""),
            pull_request_number=quote(str(pull_request_number), safe=""),
            run_number=quote(str(run_number), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerReviewDetail | Problem:
    if response.status_code == 200:
        response_200 = CustomerReviewDetail.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CustomerReviewDetail | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repository: str,
    pull_request_number: int,
    run_number: int,
    *,
    client: AuthenticatedClient,
) -> Response[CustomerReviewDetail | Problem]:
    """Get a pull request review run

     Returns one review run of a pull request, addressed by repository name, pull request number and run
    number.

    Args:
        org_id (UUID):
        repository (str):
        pull_request_number (int):
        run_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerReviewDetail | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repository=repository,
        pull_request_number=pull_request_number,
        run_number=run_number,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repository: str,
    pull_request_number: int,
    run_number: int,
    *,
    client: AuthenticatedClient,
) -> CustomerReviewDetail | Problem | None:
    """Get a pull request review run

     Returns one review run of a pull request, addressed by repository name, pull request number and run
    number.

    Args:
        org_id (UUID):
        repository (str):
        pull_request_number (int):
        run_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerReviewDetail | Problem
    """

    return sync_detailed(
        org_id=org_id,
        repository=repository,
        pull_request_number=pull_request_number,
        run_number=run_number,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repository: str,
    pull_request_number: int,
    run_number: int,
    *,
    client: AuthenticatedClient,
) -> Response[CustomerReviewDetail | Problem]:
    """Get a pull request review run

     Returns one review run of a pull request, addressed by repository name, pull request number and run
    number.

    Args:
        org_id (UUID):
        repository (str):
        pull_request_number (int):
        run_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerReviewDetail | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repository=repository,
        pull_request_number=pull_request_number,
        run_number=run_number,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repository: str,
    pull_request_number: int,
    run_number: int,
    *,
    client: AuthenticatedClient,
) -> CustomerReviewDetail | Problem | None:
    """Get a pull request review run

     Returns one review run of a pull request, addressed by repository name, pull request number and run
    number.

    Args:
        org_id (UUID):
        repository (str):
        pull_request_number (int):
        run_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerReviewDetail | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repository=repository,
            pull_request_number=pull_request_number,
            run_number=run_number,
            client=client,
        )
    ).parsed
