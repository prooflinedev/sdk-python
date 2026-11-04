from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.run_now_refused import RunNowRefused
from ...models.scan_request_body import ScanRequestBody
from ...models.scan_response import ScanResponse
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    *,
    body: ScanRequestBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/scans".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | RunNowRefused | ScanResponse:
    if response.status_code == 200:
        response_200 = ScanResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = RunNowRefused.from_dict(response.json())

        return response_400

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | RunNowRefused | ScanResponse]:
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
    body: ScanRequestBody,
) -> Response[Problem | RunNowRefused | ScanResponse]:
    """Scan a repository revision

     Scans the whole repository at one commit, resolved once from `ref` or named by `commit_sha`, and
    records that resolution. Requires live GitHub write access, and `budget_credits` at most the
    organization's on-demand scan limit; a limit of 0 turns on-demand scans off. Sending the same
    `request_id` again returns the first resolution. Results remain in Proofline and are never posted to
    GitHub.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (ScanRequestBody): One request to scan a ref or an exact commit of the repository.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RunNowRefused | ScanResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
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
    body: ScanRequestBody,
) -> Problem | RunNowRefused | ScanResponse | None:
    """Scan a repository revision

     Scans the whole repository at one commit, resolved once from `ref` or named by `commit_sha`, and
    records that resolution. Requires live GitHub write access, and `budget_credits` at most the
    organization's on-demand scan limit; a limit of 0 turns on-demand scans off. Sending the same
    `request_id` again returns the first resolution. Results remain in Proofline and are never posted to
    GitHub.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (ScanRequestBody): One request to scan a ref or an exact commit of the repository.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RunNowRefused | ScanResponse
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ScanRequestBody,
) -> Response[Problem | RunNowRefused | ScanResponse]:
    """Scan a repository revision

     Scans the whole repository at one commit, resolved once from `ref` or named by `commit_sha`, and
    records that resolution. Requires live GitHub write access, and `budget_credits` at most the
    organization's on-demand scan limit; a limit of 0 turns on-demand scans off. Sending the same
    `request_id` again returns the first resolution. Results remain in Proofline and are never posted to
    GitHub.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (ScanRequestBody): One request to scan a ref or an exact commit of the repository.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RunNowRefused | ScanResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ScanRequestBody,
) -> Problem | RunNowRefused | ScanResponse | None:
    """Scan a repository revision

     Scans the whole repository at one commit, resolved once from `ref` or named by `commit_sha`, and
    records that resolution. Requires live GitHub write access, and `budget_credits` at most the
    organization's on-demand scan limit; a limit of 0 turns on-demand scans off. Sending the same
    `request_id` again returns the first resolution. Results remain in Proofline and are never posted to
    GitHub.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (ScanRequestBody): One request to scan a ref or an exact commit of the repository.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RunNowRefused | ScanResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
