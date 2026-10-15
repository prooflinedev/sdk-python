from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.agent_session_prompt_type_0 import AgentSessionPromptType0
from ...models.agent_session_prompt_type_1 import AgentSessionPromptType1
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    finding_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/findings/{finding_id}/agent-session-prompt".format(
            org_id=quote(str(org_id), safe=""),
            finding_id=quote(str(finding_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AgentSessionPromptType0 | AgentSessionPromptType1 | Problem:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> AgentSessionPromptType0 | AgentSessionPromptType1:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_agent_session_prompt_type_0 = AgentSessionPromptType0.from_dict(
                    data
                )

                return componentsschemas_agent_session_prompt_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_agent_session_prompt_type_1 = AgentSessionPromptType1.from_dict(data)

            return componentsschemas_agent_session_prompt_type_1

        response_200 = _parse_response_200(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AgentSessionPromptType0 | AgentSessionPromptType1 | Problem]:
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
) -> Response[AgentSessionPromptType0 | AgentSessionPromptType1 | Problem]:
    """Preview a coding-agent session

     Returns the exact prompt and target a coding-agent session on this pull request finding would send,
    with every protected value withheld, and the prompt digest a start names. Requires access to every
    repository in the review.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSessionPromptType0 | AgentSessionPromptType1 | Problem]
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
) -> AgentSessionPromptType0 | AgentSessionPromptType1 | Problem | None:
    """Preview a coding-agent session

     Returns the exact prompt and target a coding-agent session on this pull request finding would send,
    with every protected value withheld, and the prompt digest a start names. Requires access to every
    repository in the review.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSessionPromptType0 | AgentSessionPromptType1 | Problem
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
) -> Response[AgentSessionPromptType0 | AgentSessionPromptType1 | Problem]:
    """Preview a coding-agent session

     Returns the exact prompt and target a coding-agent session on this pull request finding would send,
    with every protected value withheld, and the prompt digest a start names. Requires access to every
    repository in the review.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentSessionPromptType0 | AgentSessionPromptType1 | Problem]
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
) -> AgentSessionPromptType0 | AgentSessionPromptType1 | Problem | None:
    """Preview a coding-agent session

     Returns the exact prompt and target a coding-agent session on this pull request finding would send,
    with every protected value withheld, and the prompt digest a start names. Requires access to every
    repository in the review.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentSessionPromptType0 | AgentSessionPromptType1 | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            finding_id=finding_id,
            client=client,
        )
    ).parsed
