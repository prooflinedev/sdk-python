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
    review_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/reviews/{review_id}".format(
            org_id=quote(str(org_id), safe=""),
            review_id=quote(str(review_id), safe=""),
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
    review_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[CustomerReviewDetail | Problem]:
    """Get a review

     Returns a review with its subjects, assessments and open items. An incomplete assessment reports its
    gaps; an empty finding list from it says nothing about the change.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerReviewDetail | Problem]
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
) -> CustomerReviewDetail | Problem | None:
    """Get a review

     Returns a review with its subjects, assessments and open items. An incomplete assessment reports its
    gaps; an empty finding list from it says nothing about the change.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerReviewDetail | Problem
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
) -> Response[CustomerReviewDetail | Problem]:
    """Get a review

     Returns a review with its subjects, assessments and open items. An incomplete assessment reports its
    gaps; an empty finding list from it says nothing about the change.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerReviewDetail | Problem]
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
) -> CustomerReviewDetail | Problem | None:
    """Get a review

     Returns a review with its subjects, assessments and open items. An incomplete assessment reports its
    gaps; an empty finding list from it says nothing about the change.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerReviewDetail | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            review_id=review_id,
            client=client,
        )
    ).parsed
