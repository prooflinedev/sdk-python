from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.finding_fix_prompt_type_0 import FindingFixPromptType0
from ...models.finding_fix_prompt_type_1 import FindingFixPromptType1
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    finding_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/findings/{finding_id}/fix-prompt".format(
            org_id=quote(str(org_id), safe=""),
            finding_id=quote(str(finding_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FindingFixPromptType0 | FindingFixPromptType1 | Problem:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> FindingFixPromptType0 | FindingFixPromptType1:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_finding_fix_prompt_type_0 = FindingFixPromptType0.from_dict(data)

                return componentsschemas_finding_fix_prompt_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_finding_fix_prompt_type_1 = FindingFixPromptType1.from_dict(data)

            return componentsschemas_finding_fix_prompt_type_1

        response_200 = _parse_response_200(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[FindingFixPromptType0 | FindingFixPromptType1 | Problem]:
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
) -> Response[FindingFixPromptType0 | FindingFixPromptType1 | Problem]:
    """Get a finding's fix prompt

     Returns a bounded untrusted prompt for a recorded pull request finding, or an explicit refusal.
    Requires access to every repository in the review. Each code reference retains its recorded commit;
    private evidence and diagnostics are omitted.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FindingFixPromptType0 | FindingFixPromptType1 | Problem]
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
) -> FindingFixPromptType0 | FindingFixPromptType1 | Problem | None:
    """Get a finding's fix prompt

     Returns a bounded untrusted prompt for a recorded pull request finding, or an explicit refusal.
    Requires access to every repository in the review. Each code reference retains its recorded commit;
    private evidence and diagnostics are omitted.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FindingFixPromptType0 | FindingFixPromptType1 | Problem
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
) -> Response[FindingFixPromptType0 | FindingFixPromptType1 | Problem]:
    """Get a finding's fix prompt

     Returns a bounded untrusted prompt for a recorded pull request finding, or an explicit refusal.
    Requires access to every repository in the review. Each code reference retains its recorded commit;
    private evidence and diagnostics are omitted.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FindingFixPromptType0 | FindingFixPromptType1 | Problem]
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
) -> FindingFixPromptType0 | FindingFixPromptType1 | Problem | None:
    """Get a finding's fix prompt

     Returns a bounded untrusted prompt for a recorded pull request finding, or an explicit refusal.
    Requires access to every repository in the review. Each code reference retains its recorded commit;
    private evidence and diagnostics are omitted.

    Args:
        org_id (UUID):
        finding_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FindingFixPromptType0 | FindingFixPromptType1 | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            finding_id=finding_id,
            client=client,
        )
    ).parsed
