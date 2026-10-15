from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.agent_session import AgentSession
from ...models.problem import Problem
from ...models.start_session import StartSession
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    finding_id: UUID,
    *,
    body: StartSession,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/findings/{finding_id}/agent-sessions".format(
            org_id=quote(str(org_id), safe=""),
            finding_id=quote(str(finding_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AgentSession | Problem:
    if response.status_code == 201:
        response_201 = AgentSession.from_dict(response.json())

        return response_201

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
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
    body: StartSession,
) -> Response[AgentSession | Problem]:
    """Start a coding-agent session

     Starts one Cursor Cloud Agents or Devin session on the finding's reviewed pull request through an
    administrator's vendor connection, with the prompt whose digest the request names. Only a personal
    token or a browser session may start one, and it requires live GitHub write access to the
    repository. A repeated request starts another session, up to 3 per finding at one commit.

    Args:
        org_id (UUID):
        finding_id (UUID):
        body (StartSession):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSession | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        finding_id=finding_id,
        body=body,
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
    body: StartSession,
) -> AgentSession | Problem | None:
    """Start a coding-agent session

     Starts one Cursor Cloud Agents or Devin session on the finding's reviewed pull request through an
    administrator's vendor connection, with the prompt whose digest the request names. Only a personal
    token or a browser session may start one, and it requires live GitHub write access to the
    repository. A repeated request starts another session, up to 3 per finding at one commit.

    Args:
        org_id (UUID):
        finding_id (UUID):
        body (StartSession):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSession | Problem
    """

    return sync_detailed(
        org_id=org_id,
        finding_id=finding_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
    body: StartSession,
) -> Response[AgentSession | Problem]:
    """Start a coding-agent session

     Starts one Cursor Cloud Agents or Devin session on the finding's reviewed pull request through an
    administrator's vendor connection, with the prompt whose digest the request names. Only a personal
    token or a browser session may start one, and it requires live GitHub write access to the
    repository. A repeated request starts another session, up to 3 per finding at one commit.

    Args:
        org_id (UUID):
        finding_id (UUID):
        body (StartSession):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSession | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        finding_id=finding_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    finding_id: UUID,
    *,
    client: AuthenticatedClient,
    body: StartSession,
) -> AgentSession | Problem | None:
    """Start a coding-agent session

     Starts one Cursor Cloud Agents or Devin session on the finding's reviewed pull request through an
    administrator's vendor connection, with the prompt whose digest the request names. Only a personal
    token or a browser session may start one, and it requires live GitHub write access to the
    repository. A repeated request starts another session, up to 3 per finding at one commit.

    Args:
        org_id (UUID):
        finding_id (UUID):
        body (StartSession):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSession | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            finding_id=finding_id,
            client=client,
            body=body,
        )
    ).parsed
