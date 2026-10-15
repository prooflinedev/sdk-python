from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.review_routing_view_type_0 import ReviewRoutingViewType0
from ...models.review_routing_view_type_1 import ReviewRoutingViewType1
from ...models.review_routing_view_type_2 import ReviewRoutingViewType2
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    review_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/reviews/{review_id}/routing".format(
            org_id=quote(str(org_id), safe=""),
            review_id=quote(str(review_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_review_routing_view_type_0 = ReviewRoutingViewType0.from_dict(
                    data
                )

                return componentsschemas_review_routing_view_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_review_routing_view_type_1 = ReviewRoutingViewType1.from_dict(
                    data
                )

                return componentsschemas_review_routing_view_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_review_routing_view_type_2 = ReviewRoutingViewType2.from_dict(data)

            return componentsschemas_review_routing_view_type_2

        response_200 = _parse_response_200(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2]:
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
) -> Response[Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2]:
    """Get review routing

     Returns the review's validated routing plan and recorded finding placements. It reports retained
    routing facts, not model output or a deployment recommendation.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2]
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
) -> Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2 | None:
    """Get review routing

     Returns the review's validated routing plan and recorded finding placements. It reports retained
    routing facts, not model output or a deployment recommendation.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2
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
) -> Response[Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2]:
    """Get review routing

     Returns the review's validated routing plan and recorded finding placements. It reports retained
    routing facts, not model output or a deployment recommendation.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2]
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
) -> Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2 | None:
    """Get review routing

     Returns the review's validated routing plan and recorded finding placements. It reports retained
    routing facts, not model output or a deployment recommendation.

    Args:
        org_id (UUID):
        review_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            review_id=review_id,
            client=client,
        )
    ).parsed
