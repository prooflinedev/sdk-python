from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.agent_session import AgentSession
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    session_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/agent-sessions/{session_id}".format(
            org_id=quote(str(org_id), safe=""),
            session_id=quote(str(session_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AgentSession | Problem:
    if response.status_code == 200:
        response_200 = AgentSession.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AgentSession | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    session_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AgentSession | Problem]:
    """Get a coding-agent session

     Returns a coding-agent session's latest status, its vendor link, its untrusted vendor summary and
    the pull request GitHub confirmed it opened in the target repository.

    Args:
        org_id (UUID):
        session_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSession | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        session_id=session_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    session_id: UUID,
    *,
    client: AuthenticatedClient,
) -> AgentSession | Problem | None:
    """Get a coding-agent session

     Returns a coding-agent session's latest status, its vendor link, its untrusted vendor summary and
    the pull request GitHub confirmed it opened in the target repository.

    Args:
        org_id (UUID):
        session_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSession | Problem
    """

    return sync_detailed(
        org_id=org_id,
        session_id=session_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    session_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AgentSession | Problem]:
    """Get a coding-agent session

     Returns a coding-agent session's latest status, its vendor link, its untrusted vendor summary and
    the pull request GitHub confirmed it opened in the target repository.

    Args:
        org_id (UUID):
        session_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSession | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        session_id=session_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    session_id: UUID,
    *,
    client: AuthenticatedClient,
) -> AgentSession | Problem | None:
    """Get a coding-agent session

     Returns a coding-agent session's latest status, its vendor link, its untrusted vendor summary and
    the pull request GitHub confirmed it opened in the target repository.

    Args:
        org_id (UUID):
        session_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSession | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            session_id=session_id,
            client=client,
        )
    ).parsed
