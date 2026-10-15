from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.customer_finding import CustomerFinding
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    finding_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/findings/{finding_id}".format(
            org_id=quote(str(org_id), safe=""),
            finding_id=quote(str(finding_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CustomerFinding | Problem:
    if response.status_code == 200:
        response_200 = CustomerFinding.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CustomerFinding | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[CustomerFinding | Problem]:
    """Get a finding

     Returns one finding with its evidence references, validation state and causal graph.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerFinding | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        finding_id=finding_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
) -> CustomerFinding | Problem | None:
    """Get a finding

     Returns one finding with its evidence references, validation state and causal graph.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerFinding | Problem
    """

    return sync_detailed(
        org_id=org_id,
        finding_id=finding_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[CustomerFinding | Problem]:
    """Get a finding

     Returns one finding with its evidence references, validation state and causal graph.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CustomerFinding | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        finding_id=finding_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
) -> CustomerFinding | Problem | None:
    """Get a finding

     Returns one finding with its evidence references, validation state and causal graph.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CustomerFinding | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            finding_id=finding_id,
            client=client,
        )
    ).parsed
